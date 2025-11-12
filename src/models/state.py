from typing import TypedDict, List, Optional
from .schemas import Finding, HumanFeedback, CuratedContent, CostMetrics, ExecutionMetrics

class ResearchState(TypedDict):
    '''
    Estado global que fluye por todos los agentes.
    '''
    
    # Input inicial
    topic: str
    
    # Investigator outputs (sin Annotated, lista simple)
    raw_findings: List[Finding]
    investigator_completed: bool
    
    # Human validation
    human_feedback: Optional[HumanFeedback]
    awaiting_human_input: bool
    
    # Curator outputs (sin Annotated, lista simple)
    curated_content: List[CuratedContent]
    curator_completed: bool
    
    # Reporter outputs
    final_report: Optional[str]
    report_file_path: Optional[str]
    reporter_completed: bool
    
    # Métricas
    cost_metrics: CostMetrics
    execution_metrics: ExecutionMetrics
    
    # Control de flujo
    current_step: str
    error: Optional[str]
