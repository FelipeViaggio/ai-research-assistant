'''
Tests de Output - Validación de formato de reporte
'''
import pytest
import os
from src.graph.workflow import ResearchWorkflow
from src.models.schemas import Finding, CuratedContent

class TestOutputFormat:
    '''REQUIREMENT: Sistema debe generar reporte estructurado en Markdown'''
    
    def test_report_is_markdown_format(self):
        '''El reporte debe estar en formato Markdown válido'''
        workflow = ResearchWorkflow()
        
        # Simular contenido curado
        curated = [
            CuratedContent(
                topic='Test Topic',
                analysis='Test analysis text here',
                key_points=['Point 1', 'Point 2'],
                sources=['Source 1'],
                word_count=10
            )
        ]
        
        # Acceder al reporter a través del supervisor
        report, file_path = workflow.supervisor.reporter.generate_report('Test', curated)
        
        # Validar Markdown
        assert report.startswith('#'), 'Debe empezar con header Markdown (#)'
        assert '##' in report, 'Debe tener subsecciones (##)'
        assert file_path.endswith('.md'), 'Archivo debe ser .md'
        
        # Validar estructura
        assert 'Introducción' in report or 'Introduction' in report
        assert 'Conclus' in report or 'Conclusion' in report
        
        # Limpiar
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def test_report_has_minimum_length(self):
        '''REQUIREMENT: Reporte debe tener contenido sustancial (min 500 palabras)'''
        workflow = ResearchWorkflow()
        
        curated = [
            CuratedContent(
                topic='Topic 1',
                analysis='Analysis ' * 50,  # Contenido razonable
                key_points=['Point 1', 'Point 2', 'Point 3'],
                sources=['Source 1', 'Source 2'],
                word_count=50
            ),
            CuratedContent(
                topic='Topic 2',
                analysis='More analysis ' * 50,
                key_points=['Point A', 'Point B'],
                sources=['Source 3'],
                word_count=50
            )
        ]
        
        # Acceder al reporter a través del supervisor
        report, file_path = workflow.supervisor.reporter.generate_report('Test Topic', curated)
        
        word_count = len(report.split())
        assert word_count >= 200, f'Reporte muy corto: {word_count} palabras (min 200 para test)'
        
        # Limpiar
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def test_report_file_is_created(self):
        '''REQUIREMENT: Reporte debe guardarse en archivo'''
        workflow = ResearchWorkflow()
        
        curated = [
            CuratedContent(
                topic='Test',
                analysis='Test analysis',
                key_points=['Point'],
                sources=['Source'],
                word_count=3
            )
        ]
        
        # Acceder al reporter a través del supervisor
        report, file_path = workflow.supervisor.reporter.generate_report('Test', curated)
        
        # Verificar que el archivo existe
        assert os.path.exists(file_path), f'Archivo no creado: {file_path}'
        
        # Verificar que tiene contenido
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert len(content) > 0, 'Archivo está vacío'
        assert content == report, 'Contenido del archivo debe coincidir con report'
        
        # Limpiar
        os.remove(file_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])