import sys
import os
import glob
import pytest

# Agregar directorio actual al path de Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

@pytest.fixture(autouse=True, scope="function")
def cleanup_test_reports():
    """Limpia reportes generados por tests"""
    yield  # Corre el test primero
    
    for report in glob.glob('reports/*test*.md'):
        try:
            os.remove(report)
        except:
            pass
    
    for report in glob.glob('reports/*Test*.md'):
        try:
            os.remove(report)
        except:
            pass