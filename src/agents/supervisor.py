'''
Supervisor Agent - Orquesta el flujo completo del sistema
'''
from typing import Dict, Literal
from ..models.state import ResearchState
from ..models.enums import TaskComplexity
from ..core.llm_client import LLMClient
from ..core.cost_optimizer import CostOptimizer
from ..utils.parsers import HumanInputParser
from ..utils.visualizer import WorkflowVisualizer
from .investigator import InvestigatorAgent
from .curator import CuratorAgent
from .reporter import ReporterAgent
from rich.console import Console
from rich.table import Table

console = Console()

class SupervisorAgent:
    '''
    Agente Supervisor que orquesta todo el workflow.
    
    Responsabilidades:
    - Decidir qué agente ejecutar en cada paso
    - Manejar el flujo de datos entre agentes
    - Gestionar el estado del sistema
    - Coordinar la validación humana
    '''
    
    def __init__(self):
        console.print('[dim]🤖 Inicializando Supervisor Agent...[/dim]')
        
        # Componentes core
        self.llm_client = LLMClient()
        self.cost_optimizer = CostOptimizer()
        self.parser = HumanInputParser()
        self.visualizer = WorkflowVisualizer()
        
        # Inicializar agentes subordinados
        self.investigator = InvestigatorAgent(self.llm_client, self.cost_optimizer)
        self.curator = CuratorAgent(self.llm_client, self.cost_optimizer)
        self.reporter = ReporterAgent(self.llm_client, self.cost_optimizer)
        
        console.print('[dim]✓ Supervisor Agent listo[/dim]')
    
    def orchestrate(self, state: ResearchState) -> ResearchState:
        '''
        Orquesta el flujo completo basado en el estado actual.
        
        Esta es la función principal que decide qué hacer en cada paso.
        '''
        current_step = state['current_step']
        
        console.print(f'[dim]📋 Supervisor: Paso actual = {current_step}[/dim]')
        
        if current_step == 'investigator':
            return self._run_investigator(state)
        
        elif current_step == 'human_validation':
            return self._run_human_validation(state)
        
        elif current_step == 'curator':
            return self._run_curator(state)
        
        elif current_step == 'reporter':
            return self._run_reporter(state)
        
        else:
            console.print(f'[red]❌ Supervisor: Estado desconocido: {current_step}[/red]')
            state['error'] = f'Unknown step: {current_step}'
            return state
    
    def _run_investigator(self, state: ResearchState) -> ResearchState:
        '''Ejecuta el Investigator Agent'''
        console.print('[dim]🎯 Supervisor: Delegando a Investigator Agent[/dim]')
        
        # Actualizar visualizer
        self.visualizer.update_status('investigator', 'running')
        self.visualizer.display()
        
        console.print()
        console.print('='*60)
        console.print('[bold cyan]PASO 1: INVESTIGACIÓN INICIAL[/bold cyan]')
        console.print('='*60)
        
        # Ejecutar investigator
        findings = self.investigator.investigate(state['topic'])
        
        # Actualizar estado
        state['raw_findings'] = findings
        state['investigator_completed'] = True
        state['awaiting_human_input'] = True
        state['current_step'] = 'human_validation'
        
        # Actualizar visualizer
        self.visualizer.update_status(
            'investigator', 
            'completed', 
            f'{len(findings)} subtemas encontrados'
        )
        self.visualizer.display()
        
        console.print('[dim]✓ Supervisor: Investigator completado[/dim]')
        
        return state
    
    def _run_human_validation(self, state: ResearchState) -> ResearchState:
        '''Ejecuta la validación humana'''
        console.print('[dim]🎯 Supervisor: Iniciando validación humana[/dim]')
        
        # Actualizar visualizer
        self.visualizer.update_status('human_validation', 'waiting', 'Aguardando tu decisión')
        self.visualizer.display()
        
        console.print()
        console.print('='*60)
        console.print('[bold yellow]PASO 2: VALIDACIÓN HUMANA[/bold yellow]')
        console.print('='*60)
        
        findings = state['raw_findings']
        
        # Mostrar findings
        self._display_findings(findings)
        
        # Pedir input al usuario
        console.print()
        console.print('[bold]¿Qué subtemas querés investigar a fondo?[/bold]')
        console.print()
        console.print('[dim]Comandos disponibles:[/dim]')
        console.print('  • approve 1,3,5        (aprobar subtemas específicos)')
        console.print('  • reject 2             (rechazar subtemas)')
        console.print('  • approve all          (aprobar todos)')
        console.print('  • approve all except 2 (aprobar todos menos algunos)')
        console.print("  • add 'nuevo tema'     (agregar tema custom)")
        console.print("  • modify 1 to 'texto'  (modificar un subtema)")
        console.print()
        
        # Loop hasta obtener input válido
        feedback = None
        available_ids = [f.id for f in findings]
        
        while feedback is None:
            user_input = input('[Tu decisión] > ').strip()
            
            feedback, error = self.parser.parse(user_input, available_ids)
            
            if error:
                console.print(f'{error}')
                console.print()
                feedback = None
            else:
                # Mostrar resumen
                console.print(self.parser.format_feedback_summary(feedback))
                
                # Confirmar
                confirm = input('¿Confirmar? (s/n) > ').strip().lower()
                if confirm not in ['s', 'si', 'y', 'yes']:
                    console.print('[yellow]Cancelado. Ingresá tu decisión de nuevo.[/yellow]')
                    console.print()
                    feedback = None
        
        # Actualizar estado
        state['human_feedback'] = feedback
        state['awaiting_human_input'] = False
        
        # Decidir próximo paso
        if not feedback.approved_ids and not feedback.additions:
            console.print()
            console.print('[yellow]⚠️  No se aprobó ningún subtema. Finalizando.[/yellow]')
            state['current_step'] = 'completed'
        else:
            state['current_step'] = 'curator'
        
        # Actualizar visualizer
        approved_count = len(feedback.approved_ids) + len(feedback.additions)
        self.visualizer.update_status(
            'human_validation', 
            'completed', 
            f'{approved_count} subtemas aprobados'
        )
        
        console.print('[dim]✓ Supervisor: Validación humana completada[/dim]')
        
        return state
    
    def _run_curator(self, state: ResearchState) -> ResearchState:
        '''Ejecuta el Curator Agent'''
        console.print('[dim]🎯 Supervisor: Delegando a Curator Agent[/dim]')
        
        # Actualizar visualizer
        self.visualizer.update_status('curator', 'running')
        self.visualizer.display()
        
        console.print()
        console.print('='*60)
        console.print('[bold magenta]PASO 3: ANÁLISIS PROFUNDO[/bold magenta]')
        console.print('='*60)
        
        feedback = state['human_feedback']
        all_findings = state['raw_findings']
        
        # Obtener findings aprobados
        approved_findings = [
            f for f in all_findings 
            if f.id in feedback.approved_ids
        ]
        
        # Agregar temas custom
        if feedback.additions:
            console.print()
            console.print(f'[cyan]📝 Agregando {len(feedback.additions)} temas personalizados...[/cyan]')
            from ..models.schemas import Finding
            for i, topic in enumerate(feedback.additions):
                custom_finding = Finding(
                    id=max([f.id for f in all_findings]) + i + 1,
                    title=topic,
                    description=f'Tema agregado por el usuario: {topic}',
                    relevance_score=1.0,
                    source='User Input'
                )
                approved_findings.append(custom_finding)
        
        # Aplicar modificaciones
        if feedback.modifications:
            for finding in approved_findings:
                if finding.id in feedback.modifications:
                    finding.title = feedback.modifications[finding.id]
        
        # Ejecutar curator
        curated = self.curator.curate(approved_findings, state['topic'])
        
        # Actualizar estado
        state['curated_content'] = curated
        state['curator_completed'] = True
        state['current_step'] = 'reporter'
        
        # Actualizar visualizer
        self.visualizer.update_status(
            'curator', 
            'completed', 
            f'{len(curated)} items analizados'
        )
        self.visualizer.display()
        
        console.print('[dim]✓ Supervisor: Curator completado[/dim]')
        
        return state
    
    def _run_reporter(self, state: ResearchState) -> ResearchState:
        '''Ejecuta el Reporter Agent'''
        console.print('[dim]🎯 Supervisor: Delegando a Reporter Agent[/dim]')
        
        # Actualizar visualizer
        self.visualizer.update_status('reporter', 'running')
        self.visualizer.display()
        
        console.print()
        console.print('='*60)
        console.print('[bold green]PASO 4: GENERACIÓN DE REPORTE[/bold green]')
        console.print('='*60)
        
        curated_content = state['curated_content']
        
        # Ejecutar reporter
        report, file_path = self.reporter.generate_report(
            state['topic'],
            curated_content
        )
        
        # Actualizar estado
        state['final_report'] = report
        state['report_file_path'] = file_path
        state['reporter_completed'] = True
        state['current_step'] = 'completed'
        
        # Actualizar métricas finales
        from datetime import datetime
        state['execution_metrics'].end_time = datetime.now()
        state['execution_metrics'].final_report_words = len(report.split())
        
        # Actualizar visualizer
        word_count = len(report.split())
        self.visualizer.update_status(
            'reporter', 
            'completed', 
            f'{word_count} palabras generadas'
        )
        self.visualizer.display()
        
        console.print('[dim]✓ Supervisor: Reporter completado[/dim]')
        
        return state
    
    def _display_findings(self, findings):
        '''Muestra los findings en una tabla'''
        table = Table(title='Subtemas Identificados', show_header=True, header_style='bold cyan')
        
        table.add_column('ID', style='cyan', width=4, justify='center')
        table.add_column('Título', style='magenta', width=40)
        table.add_column('Descripción', style='white', width=50)
        table.add_column('Relevancia', style='green', width=10, justify='center')
        
        for finding in findings:
            table.add_row(
                str(finding.id),
                finding.title,
                finding.description[:80] + '...' if len(finding.description) > 80 else finding.description,
                f'{finding.relevance_score:.1f}'
            )
        
        console.print(table)
    
    def get_cost_optimizer(self):
        '''Retorna el cost optimizer para métricas'''
        return self.cost_optimizer
