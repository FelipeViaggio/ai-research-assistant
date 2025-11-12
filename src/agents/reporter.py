from typing import List
from ..models.schemas import CuratedContent
from ..models.enums import TaskComplexity
from ..core.llm_client import LLMClient
from ..core.cost_optimizer import CostOptimizer
from rich.console import Console
from datetime import datetime
import os

console = Console()

class ReporterAgent:
    """
    Agente que genera el reporte final en formato Markdown.
    SIEMPRE usa el modelo más potente para máxima calidad.
    """
    
    def __init__(self, llm_client: LLMClient, cost_optimizer: CostOptimizer):
        self.llm = llm_client
        self.cost_optimizer = cost_optimizer
    
    def generate_report(
        self, 
        topic: str, 
        curated_content: List[CuratedContent],
        output_dir: str = "./reports"
    ) -> tuple[str, str]:
        """
        Genera el reporte final en Markdown.
        
        Args:
            topic: Tema principal de investigación
            curated_content: Contenido curado por el Curator
            output_dir: Directorio donde guardar el reporte
        
        Returns:
            Tuple de (reporte_texto, ruta_archivo)
        """
        console.print(f"\n[bold green]📝 Reporter Agent:[/bold green] Generando reporte final...")
        
        # CRÍTICO: Siempre usar el modelo más potente
        model = self.cost_optimizer.select_model(
            task_complexity=TaskComplexity.CRITICAL,
            force_model="expensive"
        )
        
        # Construir contexto para el LLM
        context = self._build_context(curated_content)
        
        prompt = f"""You are a professional technical writer.

Generate a comprehensive research report on: {topic}

Analyzed content:
{context}

REQUIRED STRUCTURE:

# {topic}: Comprehensive Analysis

## Introduction
[Introductory paragraph contextualizing the topic]

## [For each subtopic, create a section]

### [Subtopic Title]
[Detailed analysis]

**Key Points:**
- [Point 1]
- [Point 2]

## Conclusions
[Synthesis of main findings and future perspectives]

## References
[Sources and related knowledge areas mentioned]

---

IMPORTANT:
- Use professional Markdown
- Clear and technical language
- Minimum 500 words
- Well structured with headers
- No placeholder text
"""

        system_message = "You are a senior technical writer specialized in academic and research reports."
        
        # Mostrar header de streaming
        console.print('[bold cyan]📄 Reporte generándose en tiempo real:[/bold cyan]')
        console.print()
        console.print('─' * 60)
        console.print()

        report = self.llm.generate(
            prompt=prompt,
            model=model,
            temperature=0.4,
            max_tokens=3000,
            system_message=system_message,
            stream=False  # Activar Streaming
        )

        console.print()
        console.print('─' * 60)
        console.print()
                
        # Log del uso
        tokens_used = self.llm.count_tokens_estimate(prompt + report)
        self.cost_optimizer.log_usage(model, tokens_used, "Generación de reporte final")
        
        # Guardar archivo
        file_path = self._save_report(report, topic, output_dir)
        
        console.print(f"[green]✓[/green] Reporte generado: {file_path}")
        
        return report, file_path
    
    def _build_context(self, curated_content: List[CuratedContent]) -> str:
        """Construye el contexto para el LLM"""
        
        context_parts = []
        
        for i, content in enumerate(curated_content, 1):
            part = f"""
SUBTEMA {i}: {content.topic}

Análisis:
{content.analysis}

Puntos Clave:
{chr(10).join(f'- {point}' for point in content.key_points)}

Fuentes:
{chr(10).join(f'- {source}' for source in content.sources)}
"""
            context_parts.append(part)
        
        return "\n\n---\n\n".join(context_parts)
    
    def _save_report(self, report: str, topic: str, output_dir: str) -> str:
        """Guarda el reporte en un archivo Markdown"""
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
        safe_topic = safe_topic.replace(' ', '_').lower()[:50]
        
        filename = f"{safe_topic}_{timestamp}.md"
        file_path = os.path.join(output_dir, filename)
        
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return file_path
