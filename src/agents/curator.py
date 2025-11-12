from typing import List
from ..models.schemas import Finding, CuratedContent
from ..models.enums import TaskComplexity
from ..core.llm_client import LLMClient
from ..core.cost_optimizer import CostOptimizer
from rich.console import Console

console = Console()

class CuratorAgent:
    """
    Agente que analiza en profundidad los findings aprobados.
    Usa modelos más potentes para análisis complejo.
    """
    
    def __init__(self, llm_client: LLMClient, cost_optimizer: CostOptimizer):
        self.llm = llm_client
        self.cost_optimizer = cost_optimizer
    
    def curate(self, findings: List[Finding], topic: str) -> List[CuratedContent]:
        """
        Analiza en profundidad los findings aprobados.
        
        Args:
            findings: Lista de findings aprobados por el usuario
            topic: Tema principal de investigación
        
        Returns:
            Lista de contenido curado y analizado
        """
        console.print(f"\n[bold magenta]🔬 Curator Agent:[/bold magenta] Analizando {len(findings)} subtemas...")
        
        curated_items = []
        
        for finding in findings:
            console.print(f"[dim]  Analizando: {finding.title}...[/dim]")
            curated = self._deep_analysis(finding, topic)
            curated_items.append(curated)
        
        console.print(f"[green]✓[/green] Análisis profundo completado")
        
        return curated_items
    
    def _deep_analysis(self, finding: Finding, main_topic: str) -> CuratedContent:
        """Realiza análisis profundo de un finding"""
        
        # Seleccionar modelo más potente para análisis complejo
        model = self.cost_optimizer.select_model(
            task_complexity=TaskComplexity.MODERATE,
            estimated_tokens=1500
        )
        
        prompt = f"""You are an expert analyst researching: {main_topic}

    Specific subtopic: {finding.title}
    Description: {finding.description}

    Your task: Perform an in-depth, structured analysis of this subtopic.

    Provide:
    1. A detailed analysis (2-3 paragraphs)
    2. 3-5 most important key points
    3. Related sources or knowledge areas

    Response format:

    ANALYSIS:
    [Your detailed analysis here]

    KEY POINTS:
    - Point 1
    - Point 2
    - Point 3

    SOURCES/AREAS:
    - Source 1
    - Source 2
    """

        system_message = "You are an expert academic researcher with deep knowledge across multiple disciplines."
        
        response = self.llm.generate(
            prompt=prompt,
            model=model,
            temperature=0.6,
            max_tokens=1500,
            system_message=system_message
        )
        
        # Log del uso
        tokens_used = self.llm.count_tokens_estimate(prompt + response)
        self.cost_optimizer.log_usage(model, tokens_used, f"Deep analysis: {finding.title}")
        
        # Parsear respuesta
        analysis, key_points, sources = self._parse_analysis_response(response)
        
        return CuratedContent(
            topic=finding.title,
            analysis=analysis,
            key_points=key_points,
            sources=sources,
            word_count=len(analysis.split())
        )
    
    def _parse_analysis_response(self, response: str) -> tuple[str, List[str], List[str]]:
        """Parsea la respuesta estructurada del LLM"""
        
        try:
            # Extraer secciones
            parts = response.split('ANÁLISIS:')
            if len(parts) < 2:
                return response, [], []
            
            rest = parts[1]
            
            # Extraer análisis
            if 'PUNTOS CLAVE:' in rest:
                analysis = rest.split('PUNTOS CLAVE:')[0].strip()
                rest = rest.split('PUNTOS CLAVE:')[1]
            else:
                analysis = rest.strip()
                return analysis, [], []
            
            # Extraer puntos clave
            if 'FUENTES/ÁREAS:' in rest:
                key_points_text = rest.split('FUENTES/ÁREAS:')[0].strip()
                sources_text = rest.split('FUENTES/ÁREAS:')[1].strip()
            else:
                key_points_text = rest.strip()
                sources_text = ""
            
            # Parsear listas
            key_points = [
                line.strip().lstrip('-•').strip() 
                for line in key_points_text.split('\n') 
                if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•'))
            ]
            
            sources = [
                line.strip().lstrip('-•').strip() 
                for line in sources_text.split('\n') 
                if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•'))
            ]
            
            return analysis, key_points, sources
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Error parseando análisis: {e}[/yellow]")
            return response, [], []
