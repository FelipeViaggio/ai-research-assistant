'''
Tests del Human Input Parser - Validación de REQUIREMENT crítico
'''
import pytest
from src.utils.parsers import HumanInputParser

class TestHumanInTheLoop:
    '''REQUIREMENT: Sistema debe pausar y pedir input humano con parsing robusto'''
    
    def setup_method(self):
        self.parser = HumanInputParser()
        self.available_ids = [1, 2, 3, 4, 5]
    
    def test_approve_multiple_ids(self):
        '''Comando: approve 1,3,5'''
        feedback, error = self.parser.parse('approve 1,3,5', self.available_ids)
        
        assert error is None, f'No debe dar error: {error}'
        assert feedback.approved_ids == [1, 3, 5]
        assert feedback.rejected_ids == []
    
    def test_reject_command(self):
        '''Comando: reject 2'''
        feedback, error = self.parser.parse('reject 2', self.available_ids)
        
        assert error is None
        assert feedback.rejected_ids == [2]
        assert feedback.approved_ids == []
    
    def test_add_custom_topic(self):
        '''Comando: add 'nuevo tema' '''
        feedback, error = self.parser.parse("add 'nuevo tema'", self.available_ids)
        
        assert error is None
        assert 'nuevo tema' in feedback.additions
    
    def test_modify_command(self):
        '''Comando: modify 1 to 'tema modificado' '''
        feedback, error = self.parser.parse("modify 1 to 'tema modificado'", self.available_ids)
        
        assert error is None
        assert 1 in feedback.modifications
        assert feedback.modifications[1] == 'tema modificado'
    
    def test_approve_all(self):
        '''Comando: approve all'''
        feedback, error = self.parser.parse('approve all', self.available_ids)
        
        assert error is None
        assert set(feedback.approved_ids) == set(self.available_ids)
    
    def test_approve_all_except(self):
        '''Comando: approve all except 2,3'''
        feedback, error = self.parser.parse('approve all except 2,3', self.available_ids)
        
        assert error is None
        assert set(feedback.approved_ids) == {1, 4, 5}
        assert set(feedback.rejected_ids) == {2, 3}
    
    def test_complex_multi_command(self):
        '''REQUIREMENT: Debe manejar comandos complejos'''
        feedback, error = self.parser.parse("approve 1,3 and add 'nuevo tema'", self.available_ids)
        
        assert error is None
        assert 1 in feedback.approved_ids
        assert 3 in feedback.approved_ids
        assert 'nuevo tema' in feedback.additions
    
    def test_invalid_id_error(self):
        '''REQUIREMENT: Debe validar IDs y dar error claro'''
        feedback, error = self.parser.parse('approve 99', self.available_ids)
        
        assert feedback is None
        assert error is not None
        assert '99' in error
        assert 'inválido' in error.lower()
    
    def test_typo_suggestion(self):
        '''REQUIREMENT: Debe sugerir correcciones para typos'''
        feedback, error = self.parser.parse('aprovar 1', self.available_ids)
        
        assert feedback is None
        assert error is not None
        assert 'approve' in error.lower()
    
    def test_empty_input_error(self):
        '''REQUIREMENT: Debe manejar input vacío'''
        feedback, error = self.parser.parse('', self.available_ids)
        
        assert feedback is None
        assert error is not None
    
    def test_conflict_detection(self):
        '''REQUIREMENT: Debe detectar conflictos (mismo ID aprobado y rechazado)'''
        feedback, error = self.parser.parse('approve 1 and reject 1', self.available_ids)
        
        assert feedback is None
        assert error is not None
        assert 'conflicto' in error.lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
