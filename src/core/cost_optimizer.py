from typing import Literal
from ..models.enums import TaskComplexity
from ..models.schemas import CostMetrics
import os
from dotenv import load_dotenv

load_dotenv()

ModelType = Literal['cheap', 'moderate', 'expensive']

class CostOptimizer:
    '''
    Optimizador de costos que selecciona el modelo apropiado
    basado en la complejidad de la tarea.
    '''
    
    # Precios aproximados por 1K tokens (simulados ya que Groq es gratis)
    # Usamos precios como si fueran modelos de OpenAI para demostrar optimización
    PRICES = {
        'llama-3.1-8b-instant': 0.0001,    # Simula modelo barato
        'llama-3.3-70b-versatile': 0.001,  # Simula modelo caro (10x más)
    }
    
    def __init__(self):
        self.models = {
            'cheap': os.getenv('MODEL_CHEAP', 'llama-3.1-8b-instant'),
            'moderate': os.getenv('MODEL_MODERATE', 'llama-3.1-8b-instant'),
            'expensive': os.getenv('MODEL_EXPENSIVE', 'llama-3.3-70b-versatile'),
        }
        self.metrics = CostMetrics()
    
    def select_model(
        self, 
        task_complexity: TaskComplexity,
        estimated_tokens: int = 1000,
        force_model: ModelType | None = None
    ) -> str:
        '''Selecciona el modelo apropiado basado en complejidad.'''
        if force_model:
            return self.models[force_model]
        
        # Lógica de decisión
        if task_complexity == TaskComplexity.SIMPLE:
            return self.models['cheap']
        elif task_complexity == TaskComplexity.MODERATE:
            if estimated_tokens < 500:
                return self.models['cheap']
            return self.models['moderate']
        elif task_complexity == TaskComplexity.COMPLEX:
            return self.models['moderate']
        else:  # CRITICAL
            return self.models['expensive']
    
    def log_usage(
        self, 
        model: str, 
        estimated_tokens: int,
        task_description: str = ''
    ):
        '''Registra el uso de un modelo y calcula costo'''
        cost = (estimated_tokens / 1000) * self.PRICES.get(model, 0.0001)
        
        if model == self.models['cheap']:
            self.metrics.cheap_model_calls += 1
            self.metrics.cheap_cost += cost
        elif model == self.models['moderate']:
            self.metrics.moderate_model_calls += 1
            self.metrics.moderate_cost += cost
        else:
            self.metrics.expensive_model_calls += 1
            self.metrics.expensive_cost += cost
        
        return cost
    
    def get_metrics(self) -> CostMetrics:
        '''Retorna las métricas actuales'''
        return self.metrics
    
    def calculate_savings(self) -> dict:
        '''Calcula el ahorro vs usar el modelo caro para todo'''
        total_calls = self.metrics.total_calls
        
        # Calcular worst case: todas las llamadas con el modelo más caro
        # Usamos el costo promedio real de las llamadas caras que hicimos
        if self.metrics.expensive_model_calls > 0:
            avg_expensive_cost = self.metrics.expensive_cost / self.metrics.expensive_model_calls
        else:
            # Si no hicimos ninguna cara, estimamos
            avg_expensive_cost = (1500 / 1000) * self.PRICES['llama-3.3-70b-versatile']
        
        worst_case_cost = total_calls * avg_expensive_cost
        
        actual_cost = self.metrics.total_cost
        savings = worst_case_cost - actual_cost
        savings_percentage = (savings / worst_case_cost * 100) if worst_case_cost > 0 else 0
        
        return {
            'worst_case': worst_case_cost,
            'actual_cost': actual_cost,
            'savings': savings,
            'savings_percentage': savings_percentage
        }

    def get_detailed_metrics(self) -> dict:
        """Retorna métricas detalladas con análisis"""
        metrics = self.metrics
        
        # Calcular promedios
        avg_cost_per_call = metrics.total_cost / metrics.total_calls if metrics.total_calls > 0 else 0
        
        # Distribución de llamadas
        cheap_pct = (metrics.cheap_model_calls / metrics.total_calls * 100) if metrics.total_calls > 0 else 0
        moderate_pct = (metrics.moderate_model_calls / metrics.total_calls * 100) if metrics.total_calls > 0 else 0
        expensive_pct = (metrics.expensive_model_calls / metrics.total_calls * 100) if metrics.total_calls > 0 else 0
        
        # Savings
        savings = self.calculate_savings()
        
        return {
            'total_calls': metrics.total_calls,
            'total_cost': metrics.total_cost,
            'avg_cost_per_call': avg_cost_per_call,
            'distribution': {
                'cheap': {
                    'calls': metrics.cheap_model_calls,
                    'cost': metrics.cheap_cost,
                    'percentage': cheap_pct
                },
                'moderate': {
                    'calls': metrics.moderate_model_calls,
                    'cost': metrics.moderate_cost,
                    'percentage': moderate_pct
                },
                'expensive': {
                    'calls': metrics.expensive_model_calls,
                    'cost': metrics.expensive_cost,
                    'percentage': expensive_pct
                }
            },
            'savings': savings
        }