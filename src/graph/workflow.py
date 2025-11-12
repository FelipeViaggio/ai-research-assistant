from langgraph.graph import StateGraph, END
from ..models.state import ResearchState
from ..models.schemas import ExecutionMetrics
from ..agents.supervisor import SupervisorAgent
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

console = Console()

class ResearchWorkflow:
    '''
    Workflow que usa LangGraph para orquestar el Supervisor Agent.
    El Supervisor Agent es quien realmente maneja todo el flujo.
    '''
    
    def __init__(self):
        # Inicializar el Supervisor Agent
        self.supervisor = SupervisorAgent()
        
        # Crear el grafo
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        '''Construye el grafo de LangGraph con el Supervisor'''
        
        workflow = StateGraph(ResearchState)
        
        # Un solo nodo: el Supervisor que decide todo
        workflow.add_node('supervisor', self._supervisor_node)
        
        # Entry point
        workflow.set_entry_point('supervisor')
        
        # Edge condicional: el supervisor decide si continuar o terminar
        workflow.add_conditional_edges(
            'supervisor',
            self._should_continue,
            {
                'continue': 'supervisor',  # Loop back al supervisor
                'end': END
            }
        )
        
        return workflow.compile()
    
    def _supervisor_node(self, state: ResearchState) -> ResearchState:
        '''Nodo que ejecuta el Supervisor Agent'''
        return self.supervisor.orchestrate(state)
    
    def _should_continue(self, state: ResearchState) -> str:
        '''Decide si el supervisor debe continuar o terminar'''
        if state['current_step'] == 'completed':
            return 'end'
        elif state.get('error'):
            return 'end'
        else:
            return 'continue'
    
    def run(self, topic: str) -> dict:
        '''
        Ejecuta el workflow completo.
        
        Args:
            topic: Tema a investigar
        
        Returns:
            Estado final con el reporte generado
        '''
        console.print(Panel.fit(
            f'[bold]🔍 Iniciando Research Assistant[/bold]\n\nTema: {topic}',
            border_style='cyan'
        ))
        
        # Estado inicial
        initial_state: ResearchState = {
            'topic': topic,
            'raw_findings': [],
            'investigator_completed': False,
            'human_feedback': None,
            'awaiting_human_input': False,
            'curated_content': [],
            'curator_completed': False,
            'final_report': None,
            'report_file_path': None,
            'reporter_completed': False,
            'cost_metrics': self.supervisor.cost_optimizer.get_metrics(),
            'execution_metrics': ExecutionMetrics(
                start_time=datetime.now(),
                total_findings=0,
                approved_findings=0,
                sources_analyzed=0,
                final_report_words=0
            ),
            'current_step': 'investigator',
            'error': None
        }
        
        # Ejecutar el grafo
        try:
            final_state = self.graph.invoke(initial_state)
            
            # Actualizar métricas de costo
            final_state['cost_metrics'] = self.supervisor.cost_optimizer.get_metrics()
            
            # Mostrar resumen final
            self._display_final_summary(final_state)
            
            return final_state
        
        except Exception as e:
            console.print(f'\n[red]❌ Error durante la ejecución: {e}[/red]')
            raise
    
    def _display_final_summary(self, state: dict):
        '''Muestra el resumen final de la ejecución'''
        from ..utils.metrics_display import MetricsDisplay
        from rich.table import Table
        
        console.print()
        console.print('='*70)
        console.print('[bold green]✓ INVESTIGACIÓN COMPLETADA[/bold green]')
        console.print('='*70)
        
        metrics = state['execution_metrics']
        
        # Calcular valores correctos
        total_findings = len(state['raw_findings'])
        approved_findings = len(state.get('curated_content', []))
        
        # Tabla de resumen de ejecución
        console.print()
        console.print('[bold]📊 Resumen de Ejecución:[/bold]')
        
        summary = Table(show_header=False, box=None, padding=(0, 2))
        summary.add_column('Métrica', style='cyan')
        summary.add_column('Valor', style='white')
        
        summary.add_row('⏱️  Duración', f'{metrics.duration_seconds:.1f} segundos')
        summary.add_row('📊 Subtemas encontrados', str(total_findings))
        summary.add_row('✅ Subtemas aprobados', str(approved_findings))
        summary.add_row('📝 Palabras en reporte', str(metrics.final_report_words))
        summary.add_row('💾 Archivo guardado', state.get('report_file_path', 'N/A'))
        
        console.print(summary)
        
        # Métricas detalladas de costo
        detailed_metrics = self.supervisor.cost_optimizer.get_detailed_metrics()
        MetricsDisplay.display_detailed_metrics(detailed_metrics)
        
        console.print()
        console.print('='*70)
        console.print('[bold]🎯 Siguiente paso:[/bold] Revisá el reporte en:')
        console.print(f'   [cyan]{state.get("report_file_path", "N/A")}[/cyan]')
