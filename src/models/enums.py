from enum import Enum

class TaskComplexity(str, Enum):
    """Niveles de complejidad para optimización de costos"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    CRITICAL = "critical"

class AgentRole(str, Enum):
    """Roles de los agentes en el sistema"""
    INVESTIGATOR = "investigator"
    CURATOR = "curator"
    REPORTER = "reporter"
    SUPERVISOR = "supervisor"

class ValidationAction(str, Enum):
    """\Acciones posibles en la validación humana"""
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    ADD = "add"
