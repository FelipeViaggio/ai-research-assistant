'''
Display avanzado de métricas de costo
'''
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Dict

console = Console()

class MetricsDisplay:
    '''Visualización avanzada de métricas de optimización'''
    
    @staticmethod
    def display_detailed_metrics(detailed_metrics: Dict):
        '''Muestra métricas detalladas con análisis'''
        
        console.print()
        console.print('='*70)
        console.print('[bold cyan]💰 ANÁLISIS DETALLADO DE OPTIMIZACIÓN DE COSTOS[/bold cyan]')
        console.print('='*70)
        
        # Tabla principal de costos
        MetricsDisplay._display_cost_table(detailed_metrics)
        
        # Distribución de llamadas
        console.print()
        MetricsDisplay._display_distribution_chart(detailed_metrics)
        
        # Análisis de ahorro
        console.print()
        MetricsDisplay._display_savings_analysis(detailed_metrics)
        
        # Insights
        console.print()
        MetricsDisplay._display_insights(detailed_metrics)
    
    @staticmethod
    def _display_cost_table(metrics: Dict):
        '''Tabla detallada de costos'''
        console.print()
        console.print('[bold]📊 Breakdown de Costos por Modelo:[/bold]')
        
        table = Table(show_header=True, header_style='bold cyan')
        table.add_column('Modelo', style='cyan', width=20)
        table.add_column('Llamadas', justify='right', width=10)
        table.add_column('Tokens Est.', justify='right', width=12)
        table.add_column('Costo', justify='right', width=15, style='green')
        table.add_column('% Total', justify='right', width=10)
        
        dist = metrics['distribution']
        total_cost = metrics['total_cost']
        
        # Estimar tokens (aprox 800 tokens por llamada cheap, 1500 por expensive)
        cheap_tokens = dist['cheap']['calls'] * 800
        moderate_tokens = dist['moderate']['calls'] * 1200
        expensive_tokens = dist['expensive']['calls'] * 1500
        
        # Asegurar que siempre haya algo que mostrar
        cheap_cost = dist['cheap']['cost']
        moderate_cost = dist['moderate']['cost']
        expensive_cost = dist['expensive']['cost']
        
        table.add_row(
            'Cheap (8b)',
            str(dist['cheap']['calls']),
            f'{cheap_tokens:,}',
            f'${cheap_cost:.6f}' if cheap_cost > 0 else '$0.000000 (FREE)',
            f'{dist["cheap"]["percentage"]:.1f}%'
        )
        
        table.add_row(
            'Moderate',
            str(dist['moderate']['calls']),
            f'{moderate_tokens:,}',
            f'${moderate_cost:.6f}' if moderate_cost > 0 else '$0.000000 (FREE)',
            f'{dist["moderate"]["percentage"]:.1f}%'
        )
        
        table.add_row(
            'Expensive (70b)',
            str(dist['expensive']['calls']),
            f'{expensive_tokens:,}',
            f'${expensive_cost:.6f}' if expensive_cost > 0 else '$0.000000 (FREE)',
            f'{dist["expensive"]["percentage"]:.1f}%'
        )
        
        # Total row
        total_tokens = cheap_tokens + moderate_tokens + expensive_tokens
        cost_display = f'${total_cost:.6f}' if total_cost > 0 else '$0.000000 (FREE)'
        
        table.add_row(
            '[bold]TOTAL[/bold]',
            f'[bold]{metrics["total_calls"]}[/bold]',
            f'[bold]{total_tokens:,}[/bold]',
            f'[bold]{cost_display}[/bold]',
            '[bold]100.0%[/bold]'
        )
        
        console.print(table)
        
        # Nota sobre Groq
        if total_cost < 0.01:
            console.print()
            console.print('[dim]💡 Nota: Groq ofrece uso gratuito. Los costos mostrados son simulados[/dim]')
            console.print('[dim]   para demostrar la optimización. Con OpenAI serían reales.[/dim]')
    
    @staticmethod
    def _display_distribution_chart(metrics: Dict):
        '''Gráfico ASCII de distribución de llamadas'''
        console.print('[bold]📈 Distribución de Llamadas:[/bold]')
        console.print()
        
        dist = metrics['distribution']
        total = metrics['total_calls']
        
        if total == 0:
            console.print('[dim]No hay llamadas para mostrar[/dim]')
            return
        
        # Calcular barras (max 50 chars)
        max_width = 50
        
        cheap_width = int((dist['cheap']['calls'] / total) * max_width)
        moderate_width = int((dist['moderate']['calls'] / total) * max_width)
        expensive_width = int((dist['expensive']['calls'] / total) * max_width)
        
        console.print(f'  Cheap (8b):     [green]{"█" * cheap_width}[/green] {dist["cheap"]["calls"]} llamadas ({dist["cheap"]["percentage"]:.1f}%)')
        console.print(f'  Moderate:       [yellow]{"█" * moderate_width}[/yellow] {dist["moderate"]["calls"]} llamadas ({dist["moderate"]["percentage"]:.1f}%)')
        console.print(f'  Expensive (70b):[red]{"█" * expensive_width}[/red] {dist["expensive"]["calls"]} llamadas ({dist["expensive"]["percentage"]:.1f}%)')
    
    @staticmethod
    def _display_savings_analysis(metrics: Dict):
        '''Análisis de ahorro vs escenarios alternativos'''
        console.print('[bold]💵 Análisis Comparativo de Costos:[/bold]')
        console.print()
        
        savings = metrics['savings']
        actual = savings['actual_cost']
        worst_case = savings['worst_case']
        savings_amount = savings['savings']
        savings_pct = savings['savings_percentage']
        
        # Calcular mejor caso (todo cheap)
        total_calls = metrics['total_calls']
        best_case = total_calls * (1000 / 1000) * 0.0001  # Todo cheap
        
        # Si todos los costos son 0, mostrar costos simulados
        if worst_case == 0:
            # Usar precios simulados más realistas
            worst_case = total_calls * 0.015  # ~$0.015 por llamada con GPT-4
            actual = (metrics['distribution']['cheap']['calls'] * 0.001 + 
                    metrics['distribution']['expensive']['calls'] * 0.015)
            best_case = total_calls * 0.001
            savings_amount = worst_case - actual
            savings_pct = (savings_amount / worst_case * 100) if worst_case > 0 else 0
        
        # Gráfico de barras comparativo
        max_cost = max(actual, worst_case, best_case)
        bar_scale = 40 / max_cost if max_cost > 0 else 1
        
        actual_bar = int(actual * bar_scale)
        worst_bar = int(worst_case * bar_scale)
        best_bar = int(best_case * bar_scale)
        
        console.print(f'  Todo modelo caro:     [red]{"█" * worst_bar}[/red] ${worst_case:.4f}')
        console.print(f'  [bold cyan]Tu sistema (optimizado):[/bold cyan] [cyan]{"█" * actual_bar}[/cyan] [bold]${actual:.4f}[/bold] ← [green]SWEET SPOT[/green]')
        console.print(f'  Todo modelo barato:   [green]{"█" * best_bar}[/green] ${best_case:.4f} (menor calidad)')
        
        console.print()
        
        if savings_amount > 0:
            console.print(f'  [bold green]✓ Ahorro vs worst case: ${savings_amount:.4f} ({savings_pct:.1f}%)[/bold green]')
        else:
            console.print(f'  [yellow]Costo similar al worst case[/yellow]')
        
        console.print()
        console.print('[dim]💡 Costos simulados basados en precios de OpenAI GPT-4 (~$0.03/1K tokens)[/dim]')
        console.print('[dim]   para demostrar el valor de la optimización.[/dim]')
    
    @staticmethod
    def _display_insights(metrics: Dict):
        '''Insights automáticos sobre la optimización'''
        console.print('[bold]💡 Insights de Optimización:[/bold]')
        console.print()
        
        dist = metrics['distribution']
        total = metrics['total_calls']
        
        insights = []
        
        # Insight 1: Distribución de llamadas
        cheap_pct = int(dist['cheap']['percentage'])
        if cheap_pct >= 60:
            insights.append(f'[green]✓[/green] Excelente uso de modelos baratos ({cheap_pct}% de llamadas)')
        elif cheap_pct >= 40:
            insights.append(f'[yellow]•[/yellow] Buen balance de modelos baratos ({cheap_pct}%)')
        else:
            insights.append(f'[yellow]⚠[/yellow]  Pocas llamadas a modelo barato ({cheap_pct}%)')
        
        # Insight 2: Uso de modelo caro
        expensive_calls = dist['expensive']['calls']
        if expensive_calls == 1:
            insights.append('[green]✓[/green] Uso óptimo del modelo caro (solo para reporte final)')
        elif expensive_calls == 0:
            insights.append('[yellow]⚠[/yellow]  No se usó el modelo más potente')
        else:
            insights.append(f'[yellow]•[/yellow] {expensive_calls} llamadas al modelo caro')
        
        # Insight 3: Costo promedio (ARREGLADO)
        avg_cost = metrics['avg_cost_per_call']
        if avg_cost > 0:
            if avg_cost < 0.001:
                insights.append(f'[green]✓[/green] Costo promedio muy bajo por llamada (${avg_cost:.6f})')
            else:
                insights.append(f'[yellow]•[/yellow] Costo promedio por llamada: ${avg_cost:.4f}')
        else:
            # Si es 0 (Groq gratis), mostrar costo simulado
            simulated_avg = 0.0078 / total if total > 0 else 0
            insights.append(f'[green]✓[/green] Costo promedio simulado: ${simulated_avg:.4f}/llamada (con Groq: gratis)')
        
        # Insight 4: Ahorro significativo
        savings_pct = metrics['savings']['savings_percentage']
        if savings_pct > 70:
            insights.append(f'[green]✓[/green] Ahorro excelente ({int(savings_pct)}%) vs usar siempre modelo caro')
        elif savings_pct > 50:
            insights.append(f'[green]✓[/green] Buen ahorro ({int(savings_pct)}%) manteniendo calidad')
        elif savings_pct > 0:
            insights.append(f'[yellow]•[/yellow] Ahorro moderado ({int(savings_pct)}%)')
        
        for insight in insights:
            console.print(f'  {insight}')
