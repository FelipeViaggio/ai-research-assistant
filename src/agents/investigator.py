from typing import List, Dict
from ..models.schemas import Finding
from ..models.enums import TaskComplexity
from ..core.llm_client import LLMClient
from ..core.cost_optimizer import CostOptimizer
from rich.console import Console


console = Console()

class InvestigatorAgent:
    """
    Agente encargado de la investigación inicial.
    """
    
    def __init__(self, llm_client: LLMClient, cost_optimizer: CostOptimizer):
        self.llm = llm_client
        self.cost_optimizer = cost_optimizer
    
    def investigate(self, topic: str) -> List[Finding]:
        console.print(f"\n[bold cyan]🔍 Investigator Agent:[/bold cyan] Investigando '{topic}'...")
        
        mock_sources = self._mock_web_search(topic)
        findings = self._extract_subtopics(topic, mock_sources)
        
        console.print(f"[green]✓[/green] Encontrados {len(findings)} subtemas potenciales")
        
        return findings
    
    def _mock_web_search(self, topic: str) -> List[Dict[str, str]]:
        """
        Simula una búsqueda web con resultados realistas y variados.
        En producción esto sería reemplazado por Tavily API o similar.
        """
        import random
        from datetime import datetime, timedelta
        
        # Fuentes variadas
        sources = [
            "arXiv", "Nature", "Science", "IEEE", "ACM",
            "TechCrunch", "Wired", "MIT Technology Review",
            "Forbes", "Harvard Business Review", "McKinsey",
            "GitHub", "Stack Overflow", "Medium"
        ]
        
        # Templates de títulos variados
        title_templates = [
            f"Recent advances in {topic}: A 2024 comprehensive review",
            f"How {topic} is transforming industries",
            f"The future of {topic}: Expert predictions",
            f"Practical applications of {topic} in real-world scenarios",
            f"Challenges and limitations of {topic}",
            f"A beginner's guide to {topic}",
            f"Case study: Successful implementation of {topic}",
            f"{topic}: Current state and future directions",
            f"Ethical considerations in {topic}",
            f"Comparative analysis of {topic} approaches"
        ]
        
        # Snippet templates
        snippet_templates = [
            f"This comprehensive study examines the latest developments in {topic}, "
            f"highlighting key breakthroughs and their implications for the field...",
            
            f"Major companies are implementing {topic} to transform their operations. "
            f"This article explores successful use cases and lessons learned...",
            
            f"Experts predict that {topic} will significantly impact various sectors. "
            f"We analyze current trends and future possibilities...",
            
            f"Understanding {topic} requires examining both theoretical foundations "
            f"and practical applications. This guide provides a comprehensive overview...",
            
            f"While {topic} offers numerous benefits, it also presents challenges. "
            f"This analysis explores limitations and potential solutions...",
            
            f"From fundamentals to advanced concepts, this resource covers everything "
            f"you need to know about {topic}...",
            
            f"Real-world implementation of {topic} reveals important insights. "
            f"This case study documents the journey and outcomes...",
            
            f"The landscape of {topic} is rapidly evolving. This report provides "
            f"an up-to-date assessment of current capabilities and future directions...",
            
            f"As {topic} becomes more prevalent, ethical considerations become crucial. "
            f"This paper examines key concerns and proposes frameworks...",
            
            f"Different approaches to {topic} offer various trade-offs. "
            f"This comparative study evaluates strengths and weaknesses..."
        ]
        
        # Generar 8-10 resultados variados
        results = []
        num_results = random.randint(8, 10)
        
        for i in range(num_results):
            # Fecha aleatoria en los últimos 6 meses
            days_ago = random.randint(1, 180)
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            result = {
                "title": random.choice(title_templates),
                "url": f"https://example.com/article/{i+1}",
                "snippet": random.choice(snippet_templates),
                "source": random.choice(sources),
                "date": date,
                "relevance": round(random.uniform(0.7, 0.95), 2)
            }
            results.append(result)
        
        # Ordenar por relevancia
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results
    
    def _extract_subtopics(self, topic: str, sources: List[Dict[str, str]]) -> List[Finding]:
        """Extrae subtemas usando LLM (modelo barato)"""
        
        # Seleccionar modelo (tarea simple = modelo barato)
        model = self.cost_optimizer.select_model(
            task_complexity=TaskComplexity.SIMPLE,
            estimated_tokens=800
        )
        
        # Formatear sources de manera más rica
        formatted_sources = []
        for src in sources[:5]:  # Top 5 más relevantes
            formatted_sources.append(
                f"• [{src['source']}] {src['title']}\n"
                f"  Date: {src['date']} | Relevance: {src['relevance']}\n"
                f"  {src['snippet'][:150]}..."
            )
        
        sources_text = "\n\n".join(formatted_sources)
        
        prompt = f"""You are an expert research assistant.

    Main topic: {topic}

    Sources found on the web:
    {sources_text}

    Your task: Identify between 4 and 6 specific and relevant subtopics that should be investigated in depth.

    IMPORTANT: Respond ONLY with the following JSON format, without additional text:

    {{
    "subtopics": [
        {{
        "id": 1,
        "title": "Subtopic title",
        "description": "Brief description of why it is relevant",
        "relevance": 0.9
        }}
    ]
    }}

    The 'relevance' field must be a number between 0 and 1.
    """

        system_message = "You are an expert academic researcher who identifies key subtopics for research."
        
        response = self.llm.generate(
            prompt=prompt,
            model=model,
            temperature=0.3,
            system_message=system_message
        )
        
        # Log del uso
        tokens_used = self.llm.count_tokens_estimate(prompt + response)
        self.cost_optimizer.log_usage(model, tokens_used, "Extracción de subtemas")
        
        # Parsear respuesta JSON
        findings = self._parse_llm_response(response, topic)
        
        return findings
    
    def _parse_llm_response(self, response: str, topic: str) -> List[Finding]:
        import json
        
        try:
            clean_response = response.strip()
            if clean_response.startswith('`'):
                clean_response = clean_response.split('`')[1]
                if clean_response.startswith('json'):
                    clean_response = clean_response[4:]
            if clean_response.endswith('`'):
                clean_response = clean_response.rsplit('`', 1)[0]
            clean_response = clean_response.strip()
            
            data = json.loads(clean_response)
            
            findings = []
            for item in data.get('subtopics', []):
                finding = Finding(
                    id=item['id'],
                    title=item['title'],
                    description=item['description'],
                    relevance_score=item.get('relevance', 0.5),
                    source="LLM Analysis"
                )
                findings.append(finding)
            
            return findings
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Error parseando JSON: {e}[/yellow]")
            console.print(f"[dim]Respuesta: {response[:200]}...[/dim]")
            return self._create_fallback_findings(topic)
    
    def _create_fallback_findings(self, topic: str) -> List[Finding]:
        console.print("[yellow]⚠️  Usando findings de fallback[/yellow]")
        
        return [
            Finding(
                id=1,
                title=f"Fundamentos de {topic}",
                description=f"Conceptos básicos de {topic}",
                relevance_score=0.8,
                source="Fallback"
            ),
            Finding(
                id=2,
                title=f"Aplicaciones de {topic}",
                description=f"Usos prácticos de {topic}",
                relevance_score=0.9,
                source="Fallback"
            ),
            Finding(
                id=3,
                title=f"Desafíos de {topic}",
                description=f"Limitaciones actuales de {topic}",
                relevance_score=0.7,
                source="Fallback"
            ),
        ]
