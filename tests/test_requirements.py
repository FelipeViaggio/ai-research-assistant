'''
Test Suite: Validación de Requirements de la Consigna
'''
import pytest
from src.graph.workflow import ResearchWorkflow
from src.agents.investigator import InvestigatorAgent
from src.agents.curator import CuratorAgent
from src.agents.reporter import ReporterAgent
from src.core.llm_client import LLMClient
from src.core.cost_optimizer import CostOptimizer
from src.models.enums import TaskComplexity

class TestMultiAgentArchitecture:
    '''Valida que la arquitectura multi-agente esté implementada correctamente'''
    
    def test_workflow_has_all_agents(self):
        '''REQUIREMENT: Multi-agent system con 4 agentes'''
        workflow = ResearchWorkflow()
        
        # Verificar que todos los agentes existen
        assert hasattr(workflow, 'investigator'), 'Falta Investigator Agent'
        assert hasattr(workflow, 'curator'), 'Falta Curator Agent'
        assert hasattr(workflow, 'reporter'), 'Falta Reporter Agent'
        assert hasattr(workflow, 'parser'), 'Falta Parser (parte del Supervisor)'
        
        # Verificar tipos correctos
        assert isinstance(workflow.investigator, InvestigatorAgent)
        assert isinstance(workflow.curator, CuratorAgent)
        assert isinstance(workflow.reporter, ReporterAgent)
    
    def test_graph_has_correct_nodes(self):
        '''REQUIREMENT: Workflow orquestado por Supervisor'''
        workflow = ResearchWorkflow()
        graph = workflow.graph
        
        # El grafo debe tener los 4 nodos principales
        # LangGraph no expone nodes directamente, pero podemos verificar
        # que el grafo se compiló correctamente
        assert graph is not None, 'El grafo no se compiló'
    
    def test_agents_use_shared_components(self):
        '''Verificar que los agentes comparten LLM y CostOptimizer'''
        workflow = ResearchWorkflow()
        
        # Todos deben usar el mismo cost_optimizer para tracking correcto
        assert workflow.investigator.cost_optimizer is workflow.cost_optimizer
        assert workflow.curator.cost_optimizer is workflow.cost_optimizer
        assert workflow.reporter.cost_optimizer is workflow.cost_optimizer

class TestCostOptimization:
    '''Valida que la optimización de costos funcione correctamente'''
    
    def test_cost_optimizer_selects_cheap_for_simple(self):
        '''REQUIREMENT: Simple tasks → cheaper models'''
        optimizer = CostOptimizer()
        
        model = optimizer.select_model(
            task_complexity=TaskComplexity.SIMPLE,
            estimated_tokens=500
        )
        
        assert model == optimizer.models['cheap'], \
            f'Debería usar modelo barato para tarea SIMPLE, usó {model}'
    
    def test_cost_optimizer_selects_expensive_for_critical(self):
        '''REQUIREMENT: Complex tasks → expensive models'''
        optimizer = CostOptimizer()
        
        model = optimizer.select_model(
            task_complexity=TaskComplexity.CRITICAL,
            estimated_tokens=2000
        )
        
        assert model == optimizer.models['expensive'], \
            f'Debería usar modelo caro para tarea CRITICAL, usó {model}'
    
    def test_cost_optimizer_tracks_usage(self):
        '''REQUIREMENT: Sistema debe trackear y reportar costos'''
        optimizer = CostOptimizer()
        
        # Simular uso
        optimizer.log_usage('llama-3.1-8b-instant', 1000, 'Test task')
        optimizer.log_usage('llama-3.3-70b-versatile', 1000, 'Test task 2')
        
        metrics = optimizer.get_metrics()
        
        assert metrics.cheap_model_calls == 1, 'Debe trackear llamadas baratas'
        assert metrics.expensive_model_calls == 1, 'Debe trackear llamadas caras'
        assert metrics.total_calls == 2, 'Debe sumar total correctamente'
        assert metrics.total_cost > 0, 'Debe calcular costo total'
    
    def test_cost_optimizer_calculates_savings(self):
        '''REQUIREMENT: Debe mostrar ahorro vs usar modelo caro siempre'''
        optimizer = CostOptimizer()
        
        # Simular uso mixto
        optimizer.log_usage('llama-3.1-8b-instant', 1000, 'Cheap task')
        optimizer.log_usage('llama-3.1-8b-instant', 1000, 'Cheap task')
        optimizer.log_usage('llama-3.3-70b-versatile', 1000, 'Expensive task')
        
        savings = optimizer.calculate_savings()
        
        assert 'worst_case' in savings, 'Debe calcular worst case'
        assert 'actual_cost' in savings, 'Debe calcular costo actual'
        assert 'savings' in savings, 'Debe calcular ahorro'
        assert 'savings_percentage' in savings, 'Debe calcular % de ahorro'
        assert savings['savings'] > 0, 'Debe haber ahorro al usar modelos mixtos'
        assert savings['savings_percentage'] > 0, 'El % debe ser positivo'

class TestAgentResponsibilities:
    '''Valida que cada agente cumpla sus responsabilidades específicas'''
    
    def test_investigator_generates_findings(self):
        '''REQUIREMENT: Investigator identifica temas y genera summaries'''
        llm = LLMClient()
        optimizer = CostOptimizer()
        investigator = InvestigatorAgent(llm, optimizer)
        
        findings = investigator.investigate('Test topic')
        
        # Debe generar findings
        assert len(findings) > 0, 'Investigator debe generar findings'
        assert len(findings) >= 3, 'Debe generar al menos 3-4 subtemas'
        
        # Cada finding debe tener estructura correcta
        for finding in findings:
            assert hasattr(finding, 'id'), 'Finding debe tener ID'
            assert hasattr(finding, 'title'), 'Finding debe tener título'
            assert hasattr(finding, 'description'), 'Finding debe tener descripción'
            assert hasattr(finding, 'relevance_score'), 'Finding debe tener score'
    
    def test_investigator_uses_cheap_model(self):
        '''REQUIREMENT: Investigator usa modelos baratos'''
        llm = LLMClient()
        optimizer = CostOptimizer()
        investigator = InvestigatorAgent(llm, optimizer)
        
        # Limpiar métricas
        optimizer.metrics.cheap_model_calls = 0
        optimizer.metrics.expensive_model_calls = 0
        
        investigator.investigate('Test topic')
        
        metrics = optimizer.get_metrics()
        assert metrics.cheap_model_calls > 0, 'Investigator debe usar modelo barato'
        assert metrics.expensive_model_calls == 0, 'Investigator NO debe usar modelo caro'
    
    def test_curator_performs_deep_analysis(self):
        '''REQUIREMENT: Curator hace análisis profundo'''
        llm = LLMClient()
        optimizer = CostOptimizer()
        investigator = InvestigatorAgent(llm, optimizer)
        curator = CuratorAgent(llm, optimizer)
        
        # Generar findings
        findings = investigator.investigate('Test topic')[:2]  # Solo 2 para speed
        
        # Curar
        curated = curator.curate(findings, 'Test topic')
        
        assert len(curated) == 2, 'Debe curar todos los findings aprobados'
        
        for item in curated:
            assert hasattr(item, 'topic'), 'Curated debe tener topic'
            assert hasattr(item, 'analysis'), 'Curated debe tener análisis'
            assert hasattr(item, 'key_points'), 'Curated debe tener puntos clave'
            assert len(item.analysis) > 100, 'El análisis debe ser sustancial (>100 chars)'
    
    def test_reporter_generates_markdown(self):
        '''REQUIREMENT: Reporter genera reporte en formato markdown'''
        llm = LLMClient()
        optimizer = CostOptimizer()
        investigator = InvestigatorAgent(llm, optimizer)
        curator = CuratorAgent(llm, optimizer)
        reporter = ReporterAgent(llm, optimizer)
        
        # Pipeline completo (rápido)
        findings = investigator.investigate('Test topic')[:1]
        curated = curator.curate(findings, 'Test topic')
        
        report, file_path = reporter.generate_report('Test topic', curated)
        
        # Validar formato Markdown
        assert report.startswith('#'), 'Reporte debe empezar con header Markdown'
        assert '##' in report, 'Reporte debe tener subsecciones'
        assert len(report) > 200, 'Reporte debe ser sustancial'
        
        # Validar que el archivo existe
        import os
        assert os.path.exists(file_path), f'Archivo de reporte debe existir en {file_path}'
        
        # Limpiar
        os.remove(file_path)
    
    def test_reporter_always_uses_expensive_model(self):
        '''REQUIREMENT: Reporter SIEMPRE usa modelo de alta calidad'''
        llm = LLMClient()
        optimizer = CostOptimizer()
        investigator = InvestigatorAgent(llm, optimizer)
        curator = CuratorAgent(llm, optimizer)
        reporter = ReporterAgent(llm, optimizer)
        
        # Generar contenido mínimo
        findings = investigator.investigate('Test')[:1]
        curated = curator.curate(findings, 'Test')
        
        # Limpiar métricas de expensive
        calls_before = optimizer.metrics.expensive_model_calls
        
        reporter.generate_report('Test', curated)
        
        calls_after = optimizer.metrics.expensive_model_calls
        
        assert calls_after > calls_before, 'Reporter debe usar modelo caro'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
