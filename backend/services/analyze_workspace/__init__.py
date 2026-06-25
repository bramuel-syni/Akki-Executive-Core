"""JC-WS Phase 2 (2026-06-25) — Analyze workspace (Part B) service module.

This module powers the "Analyze drawer as workspace" canonical-spec
journey. The drawer surfaces deterministic analyzer outputs as
tweet-style highlight cards grouped under topics, with a docked
free-text prompt that auto-routes follow-up questions to the right
analyzer (forecast / simulate / extract / refuse).

Public entry points:
  • route_question      — Shield-routed intent classifier + executor
  • generate_tips       — Shield-routed data-aware question suggestions
  • persist_highlight   — Append a highlight to analyses.highlights[]
"""

from .ask import route_question, persist_highlight
from .tips import generate_tips

__all__ = ["route_question", "persist_highlight", "generate_tips"]
