"""JC-MON achievement engine package.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2a).
Entry point: `services.monitor.assessment_service.assess_objective`.
"""
from services.monitor.assessment_service import (
    assess_objective,
    recommend_interventions,
    explain_performance,
    extended_health,
)

__all__ = [
    "assess_objective",
    "recommend_interventions",
    "explain_performance",
    "extended_health",
]
