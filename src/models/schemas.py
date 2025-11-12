from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Finding(BaseModel):
    """Representa un hallazgo del Investigator Agent"""
    id: int
    title: str
    description: str
    source: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)

class HumanFeedback(BaseModel):
    """Feedback del usuario durante validación"""
    approved_ids: List[int] = Field(default_factory=list)
    rejected_ids: List[int] = Field(default_factory=list)
    modifications: Dict[int, str] = Field(default_factory=dict)
    additions: List[str] = Field(default_factory=list)
    raw_input: str

class CuratedContent(BaseModel):
    """Contenido analizado por el Curator Agent"""
    topic: str
    analysis: str
    key_points: List[str]
    sources: List[str]
    word_count: int

class CostMetrics(BaseModel):
    """Métricas de costo de la ejecución"""
    cheap_model_calls: int = 0
    moderate_model_calls: int = 0
    expensive_model_calls: int = 0
    cheap_cost: float = 0.0
    moderate_cost: float = 0.0
    expensive_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        return self.cheap_cost + self.moderate_cost + self.expensive_cost
    
    @property
    def total_calls(self) -> int:
        return self.cheap_model_calls + self.moderate_model_calls + self.expensive_model_calls

class ExecutionMetrics(BaseModel):
    """Métricas generales de la ejecución"""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_findings: int = 0
    approved_findings: int = 0
    sources_analyzed: int = 0
    final_report_words: int = 0
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
