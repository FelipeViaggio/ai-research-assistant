import re
from typing import List, Dict, Optional, Tuple
from ..models.schemas import HumanFeedback
from rich.console import Console

console = Console()

class HumanInputParser:
    """
    Parser robusto para comandos del usuario durante validación.
    
    Comandos soportados:
    - approve 1,3,5
    - reject 2,4
    - add 'nuevo tema'
    - modify 1 to 'tema modificado'
    - approve all
    - reject all
    - approve all except 2,3
    """
    
    def __init__(self):
        self.last_feedback: Optional[HumanFeedback] = None
    
    def parse(self, user_input: str, available_ids: List[int]) -> Tuple[HumanFeedback, Optional[str]]:
        """
        Parsea el input del usuario.
        
        Args:
            user_input: Comando ingresado por el usuario
            available_ids: IDs válidos de findings disponibles
        
        Returns:
            Tuple de (HumanFeedback, error_message)
            Si hay error, error_message contiene la descripción
        """
        user_input = user_input.strip().lower()
        
        # Validar input vacío
        if not user_input:
            return None, "⚠️  Input vacío. Por favor ingresá un comando válido."
        
        # Inicializar feedback
        feedback = HumanFeedback(
            approved_ids=[],
            rejected_ids=[],
            modifications={},
            additions=[],
            raw_input=user_input
        )
        
        try:
            # CASO 1: approve all
            if self._matches_approve_all(user_input):
                feedback.approved_ids = available_ids.copy()
                return feedback, None
            
            # CASO 2: reject all
            if self._matches_reject_all(user_input):
                feedback.rejected_ids = available_ids.copy()
                return feedback, None
            
            # CASO 3: approve all except X,Y
            match = re.match(r'approve\s+all\s+except\s+([\d,\s]+)', user_input)
            if match:
                except_ids = self._parse_id_list(match.group(1))
                # Validar IDs
                invalid = [id for id in except_ids if id not in available_ids]
                if invalid:
                    return None, f"❌ IDs inválidos: {invalid}. IDs disponibles: {available_ids}"
                
                feedback.approved_ids = [id for id in available_ids if id not in except_ids]
                feedback.rejected_ids = except_ids
                return feedback, None
            
            # CASO 4: Comandos múltiples separados por 'and' o ','
            # Ejemplo: \"approve 1,3 and add 'new topic'\"
            commands = self._split_commands(user_input)
            
            for cmd in commands:
                cmd = cmd.strip()
                
                # CASO 4a: approve X,Y,Z
                if cmd.startswith('approve'):
                    ids_str = cmd.replace('approve', '').strip()
                    if ids_str:
                        ids = self._parse_id_list(ids_str)
                        # Validar IDs
                        invalid = [id for id in ids if id not in available_ids]
                        if invalid:
                            return None, f"❌ IDs inválidos en approve: {invalid}. IDs disponibles: {available_ids}"
                        feedback.approved_ids.extend(ids)
                
                # CASO 4b: reject X,Y,Z
                elif cmd.startswith('reject'):
                    ids_str = cmd.replace('reject', '').strip()
                    if ids_str:
                        ids = self._parse_id_list(ids_str)
                        # Validar IDs
                        invalid = [id for id in ids if id not in available_ids]
                        if invalid:
                            return None, f"❌ IDs inválidos en reject: {invalid}. IDs disponibles: {available_ids}"
                        feedback.rejected_ids.extend(ids)
                
                # CASO 4c: add 'new topic'
                elif cmd.startswith('add'):
                    topic = self._extract_quoted_text(cmd)
                    if topic:
                        feedback.additions.append(topic)
                    else:
                        return None, "❌ Formato de 'add' inválido. Usá: add 'tu tema aquí'"
                
                # CASO 4d: modify X to 'new text'
                elif cmd.startswith('modify'):
                    match = re.match(r'modify\s+(\d+)\s+to\s+(.+)', cmd)
                    if match:
                        id_to_modify = int(match.group(1))
                        new_text = self._extract_quoted_text(match.group(2))
                        
                        if id_to_modify not in available_ids:
                            return None, f"❌ ID {id_to_modify} no existe. IDs disponibles: {available_ids}"
                        
                        if not new_text:
                            return None, "❌ Formato de 'modify' inválido. Usá: modify X to 'nuevo texto'"
                        
                        feedback.modifications[id_to_modify] = new_text
                    else:
                        return None, "❌ Formato de 'modify' inválido. Usá: modify X to 'nuevo texto'"
                
                # CASO: Comando no reconocido
                else:
                    # Intentar sugerencia de corrección
                    suggestion = self._suggest_correction(cmd)
                    if suggestion:
                        return None, f"❌ Comando no reconocido: '{cmd}'. ¿Quisiste decir '{suggestion}'?"
                    return None, f"❌ Comando no reconocido: '{cmd}'. Comandos válidos: approve, reject, add, modify"
            
            # Validar que haya al menos una acción
            has_action = (
                feedback.approved_ids or 
                feedback.rejected_ids or 
                feedback.additions or 
                feedback.modifications
            )
            
            if not has_action:
                return None, "⚠️  No se detectó ninguna acción. Ejemplo: approve 1,3"
            
            # Remover duplicados
            feedback.approved_ids = list(set(feedback.approved_ids))
            feedback.rejected_ids = list(set(feedback.rejected_ids))
            
            # Validar que no haya conflictos (mismo ID aprobado y rechazado)
            conflicts = set(feedback.approved_ids) & set(feedback.rejected_ids)
            if conflicts:
                return None, f"❌ Conflicto: Los IDs {conflicts} están en approve y reject. Elegí uno."
            
            self.last_feedback = feedback
            return feedback, None
        
        except Exception as e:
            console.print(f"[red]Error interno del parser: {e}[/red]")
            return None, f"❌ Error parseando el comando. Intentá de nuevo."
    
    def _matches_approve_all(self, text: str) -> bool:
        return bool(re.match(r'approve\s+all\s*$', text))
    
    def _matches_reject_all(self, text: str) -> bool:
        return bool(re.match(r'reject\s+all\s*$', text))
    
    def _parse_id_list(self, ids_str: str) -> List[int]:
        """Parsea una lista de IDs: '1,3,5' o '1 3 5'"""
        # Limpiar y splitear
        ids_str = ids_str.replace(',', ' ')
        parts = ids_str.split()
        
        ids = []
        for part in parts:
            try:
                ids.append(int(part))
            except ValueError:
                continue
        
        return ids
    
    def _split_commands(self, text: str) -> List[str]:
        """Splitea múltiples comandos por 'and' o ';'"""
        # Primero por 'and', luego por ';'
        commands = re.split(r'\s+and\s+|;', text)
        return [cmd.strip() for cmd in commands if cmd.strip()]
    
    def _extract_quoted_text(self, text: str) -> Optional[str]:
        """Extrae texto entre comillas simples o dobles"""
        # Intentar comillas simples
        match = re.search(r"'([^']+)'", text)
        if match:
            return match.group(1)
        
        # Intentar comillas dobles
        match = re.search(r'\"([^\"]+)\"', text)
        if match:
            return match.group(1)
        
        return None
    
    def _suggest_correction(self, text: str) -> Optional[str]:
        """Sugiere corrección para typos comunes"""
        corrections = {
            'aprobar': 'approve',
            'aprovar': 'approve',
            'aceptar': 'approve',
            'rechazar': 'reject',
            'agregar': 'add',
            'añadir': 'add',
            'modificar': 'modify',
            'cambiar': 'modify',
        }
        
        for typo, correct in corrections.items():
            if text.startswith(typo):
                return correct
        
        return None
    
    def format_feedback_summary(self, feedback: HumanFeedback) -> str:
        """Genera un resumen legible del feedback"""
        lines = ["\n[bold cyan]📋 Resumen de tu decisión:[/bold cyan]"]
        
        if feedback.approved_ids:
            lines.append(f"  ✅ Aprobados: {feedback.approved_ids}")
        
        if feedback.rejected_ids:
            lines.append(f"  ❌ Rechazados: {feedback.rejected_ids}")
        
        if feedback.modifications:
            lines.append(f"  ✏️  Modificaciones:")
            for id, text in feedback.modifications.items():
                lines.append(f"     - ID {id} → '{text}'")
        
        if feedback.additions:
            lines.append(f"  ➕ Temas agregados:")
            for topic in feedback.additions:
                lines.append(f"     - '{topic}'")
        
        return "\n".join(lines)
