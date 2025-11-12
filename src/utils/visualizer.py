'''
Visualización del workflow en tiempo real
'''
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from typing import Dict

console = Console()

class WorkflowVisualizer:
    '''Muestra el estado del workflow en tiempo real'''
    
    STEPS = [
        ('investigator', '🔍 Investigator', 'Búsqueda de subtemas'),
        ('human_validation', '👤 Human Validation', 'Validación humana'),
        ('curator', '🔬 Curator', 'Análisis profundo'),
        ('reporter', '📝 Reporter', 'Generación de reporte'),
    ]
    
    STATUS_ICONS = {
        'pending': '[ ]',
        'running': '[yellow]⟳[/yellow]',
        'waiting': '[yellow]⏸[/yellow]',
        'completed': '[green]✓[/green]',
        'error': '[red]✗[/red]',
    }
    
    def __init__(self):
        self.status: Dict[str, str] = {
            'investigator': 'pending',
            'human_validation': 'pending',
            'curator': 'pending',
            'reporter': 'pending',
        }
        self.details: Dict[str, str] = {
            'investigator': '',
            'human_validation': '',
            'curator': '',
            'reporter': '',
        }
    
    def update_status(self, step: str, status: str, detail: str = ''):
        '''Actualiza el estado de un paso'''
        self.status[step] = status
        if detail:
            self.details[step] = detail
    
    def render(self) -> Panel:
        '''Renderiza el panel del workflow'''
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column('Status', style='bold', width=3)
        table.add_column('Step', style='cyan', width=25)
        table.add_column('Info', style='dim', width=30)
        
        for step_id, step_name, step_desc in self.STEPS:
            status = self.status.get(step_id, 'pending')
            icon = self.STATUS_ICONS[status]
            detail = self.details.get(step_id, '')
            
            # Descripción según el estado
            if status == 'pending':
                info = step_desc
            elif status == 'running':
                info = f'[yellow]{step_desc}...[/yellow]'
            elif status == 'waiting':
                info = f'[yellow]{detail or "Esperando..."}[/yellow]'
            elif status == 'completed':
                info = f'[green]{detail or "Completado"}[/green]'
            else:  # error
                info = f'[red]{detail or "Error"}[/red]'
            
            table.add_row(icon, step_name, info)
        
        return Panel(
            table,
            title='[bold cyan]🔄 WORKFLOW STATUS[/bold cyan]',
            border_style='cyan',
            padding=(1, 2)
        )
    
    def display(self):
        '''Muestra el panel actual'''
        console.print(self.render())
