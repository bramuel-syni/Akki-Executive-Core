"""Phase 4.1 — Akki FastAPI app.

Standalone FastAPI instance that owns the Akki HTTP surface
(auth, contexts, documents, work studio, tasks, cycles, chat,
calendar, admin, cohort, billing, monitor, search, website,
inbound email, and every other product surface that is neither
SyniSense nor Solva). Mounted into the master `server.py` app
via its `ROUTERS` list so the existing single-process
composition continues serving every `/api/*` path unchanged.
Phase 4.3 will run this app as its own uvicorn process;
Phase 4.4 adds dual-mount `/v1/akki/*` versioned paths.

Router ownership (113 modules — `len(ROUTERS) == 113`).

Mount ordering within Akki preserves the original `server.py`
sequence. Two ordering constraints are critical and verified:
  • `chat_audit_panel` registers BEFORE `chat` so that
    `/api/chats/archived` is matched as an exact path before
    `/api/chats/{chat_id}` (server.py L237-242 + L266 comment).
  • `inbound_email.router` BEFORE `inbound_email.backcompat_router`
    (default first, BC mirror second).
"""
from __future__ import annotations

from fastapi import FastAPI

# Imports in alphabetical order; mount order preserved in ROUTERS list.
from routers import account_deletion as _account_deletion
from routers import active_context as _active_context
from routers import admin_audit_invariant as _admin_audit_invariant
from routers import admin_auth_events as _admin_auth_events
from routers import admin_cohort as _admin_cohort
from routers import admin_cohort_applications as _admin_cohort_apps
from routers import admin_email_provider as _admin_email_provider
from routers import admin_extractions as _admin_extractions
from routers import admin_health as _admin_health
from routers import admin_inbox as _admin_inbox
from routers import admin_journal as _admin_journal
from routers import admin_llm_spend as _admin_llm_spend
from routers import admin_qa_hooks as _admin_qa_hooks
from routers import admin_sandbox_kpi as _admin_sandbox_kpi
from routers import admin_tenants as _admin_tenants
from routers import admin_users as _admin_users
from routers import agenda as _agenda
from routers import async_jobs as _async_jobs
from routers import audit as _audit
from routers import auth as _auth
from routers import auth_magic as _auth_magic
from routers import auth_oauth as _auth_oauth
from routers import auth_password_change as _auth_password_change
from routers import billing as _billing
from routers import blog as _blog
from routers import briefings as _briefings
from routers import chat as _chat
from routers import chat_audit_panel as _chat_audit_panel
from routers import cohort_applications as _cohort_applications
from routers import cohort_email_events as _cohort_email_events
from routers import cohort_magic_link as _cohort_magic_link
from routers import cohort_waitlist as _cohort_waitlist
from routers import comments as _comments
from routers import committees as _committees
from routers import company_home as _company_home
from routers import compilations as _compilations
from routers import contexts as _contexts
from routers import csrf as _csrf
from routers import cycle as _cycle
from routers import cycle_assignments as _cycle_assignments
from routers import cycle_manager as _cycle_manager
from routers import cycles as _cycles
from routers import daily_review as _daily_review
from routers import decks as _decks
from routers import depth as _depth
from routers import docs_download as _docs_download
from routers import jc_artifacts as _jc_artifacts
from routers import document_engagement as _document_engagement
from routers import documents as _documents
from routers import documents_async_mirror as _documents_async_mirror
from routers import early_access as _early_access
from routers import enterprise as _enterprise
from routers import events as _events
from routers import exco_teams as _exco_teams
from routers import feedback as _feedback
from routers import first_session as _first_session
from routers import health_composite as _health_composite
from routers import healthz_clamav as _healthz_clamav
from routers import help as _help
from routers import home as _home
from routers import ideas as _ideas
from routers import inbound_email as _inbound_email
from routers import inbound_queue as _inbound_queue
from routers import inbox_message_preview as _inbox_message_preview
from routers import influence_map as _influence_map
from routers import learn as _learn
from routers import lens as _lens
from routers import llm_quota as _llm_quota
from routers import mfa as _mfa
from routers import misc as _misc
from routers import monitor_dashboard as _monitor_dashboard
from routers import monitor_status_assessment as _monitor_status
from routers import monitor_strategic_items as _monitor_strategic_items
from routers import ned_cycle as _ned_cycle
from routers import news as _news
from routers import oauth_google as _oauth_google
from routers import observability as _observability
from routers import onboarding_briefs as _onboarding_briefs
from routers import onboarding_status as _onboarding_status
from routers import password_reset as _password_reset
from routers import pipeline as _pipeline
from routers import portfolio as _portfolio
from routers import portfolio_data as _portfolio_data
from routers import prepare as _prepare
from routers import product_features as _product_features
from routers import profile as _profile
from routers import pulse as _pulse
from routers import questions as _questions
from routers import quick_actions as _quick_actions
from routers import sandbox as _sandbox
from routers import sandbox_generation as _sandbox_generation
from routers import search as _search
from routers import shares as _shares
from routers import simulate as _simulate
from routers import strategic_goal_assessment as _strategic_goal_assessment
from routers import strategic_goal_evolution as _strategic_goal_evolution
from routers import strategic_goals as _strategic_goals
from routers import streaming_v9 as _streaming_v9
from routers import studio as _studio
from routers import studio_blocks as _studio_blocks
from routers import tasks as _tasks
from routers import tasks_initiatives as _tasks_initiatives
from routers import team_catalogue as _team_catalogue
from routers import trial_status as _trial_status
from routers import walkin as _walkin
from routers import website as _website
from routers import work_studio_export as _work_studio_export
from routers import work_studio_from_source as _work_studio_from_source
from routers import work_studio_overlay as _work_studio_overlay
from routers import work_studio_phase_c as _work_studio_phase_c
from routers import work_studio_phase_c2 as _work_studio_phase_c2
from routers import work_studio_render as _work_studio_render
from routers._internal_transport import make_internal_router  # Phase 4.2 internal HTTP transport.


# Ordered list of routers this app owns. Order preserved from the
# original `server.py` registration sequence to safeguard:
#   * `chat_audit_panel` BEFORE `chat` (exact /api/chats/archived
#     match must beat /api/chats/{chat_id} parameterised match)
#   * `inbound_email.router` BEFORE `inbound_email.backcompat_router`
ROUTERS = [
    # ─── server.py L183-206 ────────────────────────────────────────────
    _auth.router,
    _contexts.router,
    _documents.router,
    _misc.router,
    _briefings.router,
    _work_studio_export.router,
    _work_studio_phase_c.router,
    _work_studio_phase_c2.router,
    _work_studio_from_source.router,
    _work_studio_overlay.router,
    _work_studio_render.router,
    _learn.router,
    _committees.router,
    _simulate.router,
    _comments.router,
    _lens.router,
    _pipeline.router,
    _audit.router,
    _shares.router,
    _sandbox.router,
    _cycle.router,
    # ─── server.py L211-236 ────────────────────────────────────────────
    _tasks.router,
    _blog.router,
    _admin_email_provider.router,
    _portfolio_data.router,
    _company_home.router,
    _events.router,
    _oauth_google.router,
    _admin_cohort.router,
    _auth_magic.router,
    _auth_oauth.router,
    _billing.router,
    _onboarding_briefs.router,
    _admin_users.router,
    _admin_extractions.router,
    _admin_tenants.router,
    _account_deletion.router,
    _strategic_goal_evolution.router,
    _password_reset.router,
    _agenda.router,
    _document_engagement.router,
    _monitor_dashboard.router,
    _strategic_goals.router,
    # ─── chat audit panel BEFORE chat (path-collision guard) ───────────
    _chat_audit_panel.router,
    _chat.router,
    _influence_map.router,
    _admin_health.router,
    _admin_sandbox_kpi.router,
    _pulse.router,
    _cycle_manager.router,
    _cycles.router,
    _quick_actions.router,
    _team_catalogue.router,
    _cycle_assignments.router,
    _ned_cycle.router,
    _prepare.router,
    _inbound_email.router,
    _inbound_email.backcompat_router,
    _inbound_queue.router,
    _enterprise.router,
    _llm_quota.router,
    _admin_llm_spend.router,
    _decks.router,
    _walkin.router,
    _admin_auth_events.router,
    _admin_journal.router,
    _admin_audit_invariant.router,
    _healthz_clamav.router,
    _observability.router,
    _observability.public_router,
    _cohort_applications.router,
    _admin_qa_hooks.router,
    _onboarding_status.router,
    _active_context.router,
    _studio.router,
    _studio_blocks.router,
    _product_features.router,
    _help.router,
    _early_access.router,
    _daily_review.router,
    _first_session.router,
    _depth.router,
    _docs_download.router,
    _jc_artifacts.router,
    # ─── server.py L324-410 ────────────────────────────────────────────
    _search.router,
    _website.router,
    _sandbox_generation.router,
    _documents_async_mirror.router,
    _exco_teams.router,
    _portfolio.router,
    _compilations.router,
    _home.router,
    _monitor_strategic_items.router,
    _monitor_status.router,
    _strategic_goal_assessment.router,
    _streaming_v9.router,
    _feedback.router,
    _trial_status.router,
    _questions.router,
    _news.router,
    _profile.router,
    _tasks_initiatives.router,
    _async_jobs.router,
    _auth_password_change.router,
    _health_composite.router,
    _csrf.router,
    _mfa.router,
    _cohort_magic_link.router,
    _admin_cohort_apps.router,
    _cohort_waitlist.router,
    _cohort_email_events.router,
    _admin_inbox.router,
    _ideas.router,
    _inbox_message_preview.router,
]


# Phase 4.2 internal HTTP transport — every Akki contract method is
# reachable at `POST /api/internal/v1/akki/method/<name>` when
# `BOUNDED_CONTEXT_TRANSPORT=http`. Excluded from public OpenAPI.
def _akki_internal_adapter():
    from contracts._adapters.akki import InProcessAkkiAdapter
    return InProcessAkkiAdapter()


INTERNAL_ROUTER = make_internal_router(
    context_name="akki",
    adapter_factory=_akki_internal_adapter,
)


# Phase 4.3 / 4.4 will give this app its own lifespan, scheduler,
# CORS + security headers middleware. For Phase 4.1 we ship a slim
# FastAPI that exists primarily to declare the ownership contract.
app = FastAPI(
    title="Akki",
    description=(
        "Akki product surface — auth, contexts, documents, work "
        "studio, tasks, cycles, chat, calendar, admin, cohort, "
        "billing, monitor, search, website. SyniSense + Solva "
        "consume Akki via the Phase 1 contracts package "
        "(`get_akki()`)."
    ),
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
for _r in ROUTERS:
    app.include_router(_r)
app.include_router(INTERNAL_ROUTER)

# Phase 4.3 — Healthcheck Triad. Per-context probe + composite proxy.
from routers.healthz_context import (  # noqa: E402 — module-final wire-up
    make_context_healthz_router,
    make_composite_healthz_router,
)
app.include_router(make_context_healthz_router("akki"))
app.include_router(make_composite_healthz_router())


# Phase 5 Part D — Arm Akki-owned crons when running standalone.
@app.on_event("startup")
async def _arm_akki_crons_if_standalone() -> None:
    import logging as _logging
    import os as _os
    if _os.environ.get("AKKI_PROCESS_NAME") != "akki_app":
        return
    from core import db as _db
    from crons.akki_crons import arm as _arm
    _arm(app, _db, _logging.getLogger("akki.akki"))


__all__ = ["app", "ROUTERS", "INTERNAL_ROUTER"]
