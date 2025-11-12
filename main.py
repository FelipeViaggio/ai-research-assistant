"""
Research Assistant - Multi-Agent System
Entry point principal
"""
from src.graph.workflow import ResearchWorkflow
from src.core.config_validator import ConfigValidator
from rich.console import Console
from rich.panel import Panel
import sys

console = Console()

def main():
    console.print()
    console.print(Panel(
        "[bold]🔍 SMART CONTENT RESEARCH ASSISTANT 🔍[/bold]\n\n"
        "Sistema multi-agente con validación humana\n"
        "y optimización inteligente de costos",
        border_style="cyan",
        width=62,
        padding=(1, 2)
    ))
    
    # VALIDAR CONFIGURACIÓN PRIMERO
    if not ConfigValidator.validate_all():
        console.print()
        console.print("[red]❌ El sistema no puede iniciar debido a errores de configuración.[/red]")
        return
    
    # Obtener tema del usuario
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        console.print()
        console.print("[bold]¿Sobre qué tema querés investigar?[/bold]")
        console.print()
        topic = input("Tema: ").strip()
    
    if not topic:
        console.print("[red]❌ Necesitás especificar un tema.[/red]")
        return
    
    # Crear workflow y ejecutar
    workflow = ResearchWorkflow()
    
    try:
        final_state = workflow.run(topic)
        
        console.print()
        console.print("[bold green]✓ ¡Investigación completada exitosamente![/bold green]")
        
    except KeyboardInterrupt:
        console.print()
        console.print()
        console.print("[yellow]⚠️  Investigación cancelada por el usuario.[/yellow]")
    except Exception as e:
        console.print()
        console.print(f"[red]❌ Error: {e}[/red]")
        raise

if __name__ == "__main__":
    main()