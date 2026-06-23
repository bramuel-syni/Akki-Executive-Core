import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const routers__auth__RegisterIn = z
  .object({
    email: z.string().email(),
    password: z.string().min(8).max(128),
    name: z.string().min(1).max(120),
    context_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const AuthSessionResponse = z
  .object({
    access_token: z.union([z.string(), z.null()]),
    account: z.union([z.object({}).partial().passthrough(), z.null()]),
    contexts: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const ValidationError = z
  .object({
    loc: z.array(z.union([z.string(), z.number()])),
    msg: z.string(),
    type: z.string(),
  })
  .passthrough();
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
const LoginIn = z
  .object({ email: z.string().email(), password: z.string() })
  .passthrough();
const OkResponse = z
  .object({
    ok: z.union([z.boolean(), z.null()]),
    message: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const AccountWrapResponse = z
  .object({
    account: z.union([z.object({}).partial().passthrough(), z.null()]),
    contexts: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const DeclareRoleIn = z
  .object({ declared_role: z.enum(["ned", "executive", "dual", "undeclared"]) })
  .passthrough();
const SetPasswordIn = z
  .object({ password: z.string().min(10).max(128) })
  .passthrough();
const AccountUpdateIn = z
  .object({
    name: z.union([z.string(), z.null()]),
    declared_role: z.union([
      z.enum(["ned", "executive", "dual", "undeclared"]),
      z.null(),
    ]),
    preferences: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .partial()
  .passthrough();
const SetDefaultContextIn = z.object({ context_id: z.string() }).passthrough();
const ContextObjectIn = z
  .object({
    industry: z.union([z.string(), z.null()]),
    sector: z.union([z.string(), z.null()]),
    jurisdiction: z.union([z.string(), z.null()]),
    role: z.union([z.enum(["ned", "executive", "reportee"]), z.null()]),
    answers: z.object({}).partial().passthrough(),
    step: z.number().int().default(0),
    completed: z.boolean().default(false),
  })
  .partial()
  .passthrough();
const ContextCreateIn = z
  .object({
    name: z.string().min(1).max(120),
    type: z
      .enum([
        "ned_personal",
        "ned_sponsored",
        "executive_personal",
        "executive_enterprise",
      ])
      .optional()
      .default("executive_personal"),
    industry: z.union([z.string(), z.null()]).optional(),
    jurisdiction: z.union([z.string(), z.null()]).optional(),
    sector: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ContextRenameIn = z
  .object({ name: z.string().min(1).max(120) })
  .passthrough();
const InvitationIn = z
  .object({
    email: z.string().email(),
    role: z
      .enum(["ned", "executive", "reportee"])
      .optional()
      .default("executive"),
    sub_role: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DocumentMetaGenerateIn = z
  .object({
    filename: z.union([z.string(), z.null()]),
    preview_text: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const DocumentMetaResponse = z
  .object({
    display_name: z.union([z.string(), z.null()]),
    description: z.union([z.string(), z.null()]),
    shielding: z.union([z.unknown(), z.null()]),
    shielding_masked: z.union([z.unknown(), z.null()]),
    mode: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const Body_upload_document_api_contexts__context_id__documents_post = z
  .object({
    file: z.instanceof(File),
    display_name: z.union([z.string(), z.null()]).optional(),
    description: z.union([z.string(), z.null()]).optional(),
    data_trust: z.union([z.string(), z.null()]).optional(),
    mentioned_account_ids: z.union([z.string(), z.null()]).optional(),
    related_doc_id: z.union([z.string(), z.null()]).optional(),
    relation_type: z.union([z.string(), z.null()]).optional(),
    category: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const committee_id = z.union([z.string(), z.null()]).optional();
const ThreadAncestryResponse = z
  .object({
    ancestors: z.union([z.array(z.unknown()), z.null()]),
    descendants: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const _ManualCreateIn = z
  .object({
    name: z.string().max(300).default("Untitled draft"),
    body: z.string().max(200000).default(""),
    state: z.string().default("draft"),
    origin: z.string().default("akki_generated"),
    objective: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .partial()
  .passthrough();
const DocumentTrustUpdate = z
  .object({
    data_trust: z.union([z.enum(["trusted", "mixed", "weak"]), z.null()]),
    related_doc_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const AsyncJobResponse = z
  .object({
    job_id: z.union([z.string(), z.null()]),
    kind: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const IntelligenceRegenerateResponse = z
  .object({
    doc_id: z.union([z.string(), z.null()]),
    mode: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const _PromptedEditIn = z
  .object({ prompt: z.string().min(1).max(2000) })
  .passthrough();
const AttachmentCreateBody = z
  .object({
    target_doc_id: z.string().min(1),
    note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const LineagePatchBody = z
  .object({
    parent_doc_id: z.union([z.string(), z.null()]),
    version_label: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ExportPolicyResponse = z
  .object({
    can_export: z.union([z.boolean(), z.null()]),
    watermark_label: z.union([z.string(), z.null()]),
    watermark_required: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const JournalCommentaryResponse = z
  .object({
    cached: z.union([z.boolean(), z.null()]),
    commentary: z.union([z.unknown(), z.null()]),
    commentary_redacted: z.union([z.unknown(), z.null()]),
    doc_id: z.union([z.string(), z.null()]),
    generated_at: z.union([z.string(), z.null()]),
    synisense_version: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const DiffResponse = z
  .object({
    diff: z.union([z.array(z.unknown()), z.null()]),
    previous_doc: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .partial()
  .passthrough();
const ParagraphsResponse = z
  .object({
    computed_at: z.union([z.string(), z.null()]),
    doc_id: z.union([z.string(), z.null()]),
    page_count: z.union([z.number(), z.null()]),
    paragraphs: z.union([z.array(z.unknown()), z.null()]),
    version: z.union([z.unknown(), z.null()]),
  })
  .partial()
  .passthrough();
const LLMProbeIn = z
  .object({ module: z.string(), query: z.string() })
  .passthrough();
const TelemetryEventIn = z
  .object({
    event_name: z.string(),
    event_version: z.string().optional().default("1.0"),
    context_id: z.union([z.string(), z.null()]).optional(),
    session_id: z.union([z.string(), z.null()]).optional(),
    surface: z.union([z.string(), z.null()]).optional(),
    properties: z.object({}).partial().passthrough().optional(),
  })
  .passthrough();
const BriefingCreateIn = z
  .object({
    signal_ids: z.union([z.array(z.string()), z.null()]),
    title: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const MarkReadIn = z
  .object({
    via: z
      .string()
      .regex(/^(manual|scroll)$/)
      .default("manual"),
  })
  .partial()
  .passthrough();
const ExportRequestIn = z
  .object({
    description: z.string().min(1).max(2000),
    objective: z.string().min(1).max(2000),
    scope: z.string().min(1).max(2000),
    output_format: z
      .enum(["docx", "pptx", "pdf", "auto"])
      .optional()
      .default("auto"),
  })
  .passthrough();
const ExportStartResponse = z
  .object({
    export_id: z.union([z.string(), z.null()]),
    kind: z.union([z.string(), z.null()]),
    output_format: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
    created_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const Body_start_enhance_api_contexts__context_id__work_studio_enhance__kind__post =
  z
    .object({
      instructions: z.string(),
      output_format: z.string().optional().default("auto"),
      source_artefact_id: z.union([z.string(), z.null()]).optional(),
      file: z.union([z.instanceof(File), z.null()]).optional(),
    })
    .passthrough();
const _SaveDraftIn = z
  .object({
    draft_session_id: z.string().min(8).max(64),
    title: z.string().max(300).optional().default("Untitled draft"),
    structured_content: z.object({}).partial().passthrough().optional(),
    kind: z
      .enum([
        "report",
        "deck",
        "minutes",
        "committee_pack",
        "briefing",
        "board_pack",
      ])
      .optional()
      .default("report"),
    document_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DraftLifecycleResponse = z
  .object({
    draft_session_id: z.union([z.string(), z.null()]),
    export_id: z.union([z.string(), z.null()]),
    idempotent_update: z.union([z.boolean(), z.null()]),
    lifecycle_state: z.union([z.string(), z.null()]),
    updated_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ExportRequest = z
  .object({
    source_id: z.string(),
    source_type: z
      .string()
      .regex(
        /^(solva_session|cycle_compilation|chat_artefact|work_studio_brief)$/
      ),
    format: z.string().regex(/^(docx|pptx|pdf)$/),
    depth: z.string().regex(/^(executive_brief|board_summary|deep_dive)$/),
    fidelity: z.string().regex(/^(low|high)$/),
    company_label: z.string().max(80).optional().default("Akki"),
    document_type: z.string().max(80).optional().default("Board Briefing"),
    programme: z.union([z.string(), z.null()]).optional(),
    revision_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const EnhanceRequest = z
  .object({
    instruction: z.string().min(4).max(2000),
    scope: z.string().optional().default("whole_brief"),
    base_revision_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SetActiveRequest = z
  .object({ revision_id: z.string().min(1) })
  .passthrough();
const FromSourceRequest = z
  .object({
    source_type: z.enum(["solva_session", "chat_artefact"]),
    source_id: z.string().min(1).max(128),
    kind: z.enum(["briefing", "deck", "report"]),
    company_label: z.string().max(80).optional().default("Akki"),
    document_type: z.string().max(80).optional().default(""),
    programme: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ArtefactRedirectResponse = z
  .object({
    artefact_id: z.union([z.string(), z.null()]),
    kind: z.union([z.string(), z.null()]),
    redirect_url: z.union([z.string(), z.null()]),
    brief_id: z.union([z.string(), z.null()]),
    title: z.union([z.string(), z.null()]),
    document_id: z.union([z.string(), z.null()]),
    active_revision_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const CreateArtefactRequest = z
  .object({
    kind: z.enum(["deck", "report"]),
    title: z.string().min(1).max(200),
    source: z.enum(["blank", "brief", "external_document"]),
    source_brief_id: z.union([z.string(), z.null()]).optional(),
    source_document_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const FromDocumentRequest = z
  .object({
    kind: z.enum(["board_pack", "committee_pack", "minutes", "deck", "report"]),
    source_doc_id: z.string().min(1).max(128),
  })
  .passthrough();
const ItemsListResponse = z
  .object({
    items: z.union([z.array(z.unknown()), z.null()]),
    next_cursor: z.union([z.string(), z.null()]),
    total: z.union([z.number(), z.null()]),
    total_pending: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const DocumentPatchIn = z
  .object({
    title: z.union([z.string(), z.null()]),
    structured_content: z.union([
      z.object({}).partial().passthrough(),
      z.null(),
    ]),
  })
  .partial()
  .passthrough();
const IdResponse = z
  .object({
    id: z.union([z.string(), z.null()]),
    deleted: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const SaveIn = z
  .object({ label: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const SnapshotResponse = z
  .object({
    snapshot_id: z.union([z.string(), z.null()]),
    saved_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ReviseIn = z
  .object({
    instruction: z.string().min(3).max(4000),
    scope: z.enum(["entire", "section", "pages"]).optional().default("entire"),
    tone: z
      .enum(["formal", "concise", "detailed"])
      .optional()
      .default("formal"),
    section_index: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const LearnResearchIn = z
  .object({
    topic: z.string().min(3).max(200),
    context_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const CommitteeIn = z
  .object({
    name: z.string().min(2).max(80),
    your_role: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SimulateIn = z
  .object({
    hypothesis: z.string().min(10).max(800),
    horizon: z
      .string()
      .regex(/^(1y|3y|1y3y)$/)
      .optional()
      .default("1y3y"),
    signal_ids: z.union([z.array(z.string()), z.null()]).optional(),
    committee_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const routers__comments__CommentIn = z
  .object({
    body: z.string().min(1).max(4000),
    parent_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SignalGenerateIn = z
  .object({ focus: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const AskIn = z.object({ question: z.string().min(1).max(4000) }).passthrough();
const LensRunIn = z
  .object({
    lens: z.string().min(1).max(40),
    subject: z.string().min(10).max(1200),
    signal_id: z.union([z.string(), z.null()]).optional(),
    committee_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const CoachStartIn = z
  .object({
    lens: z.string().min(1).max(40),
    subject: z.string().min(2).max(200),
  })
  .passthrough();
const CoachMessageIn = z
  .object({
    lens: z.string().min(1).max(40),
    message: z.string().min(1).max(4000),
  })
  .passthrough();
const PipelineRunIn = z
  .object({ focus: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const DryrunIn = z
  .object({
    text: z.string().max(20000),
    context_id: z.union([z.string(), z.null()]).optional(),
    surface: z.string().optional().default("chat"),
    mode: z.string().optional().default("redact"),
    tier_limit: z.union([z.number(), z.null()]).optional(),
    context_people: z.union([z.array(z.string()), z.null()]).optional(),
  })
  .passthrough();
const ShareCreateIn = z
  .object({
    item_type: z.enum([
      "signal",
      "briefing",
      "brief",
      "doc_summary",
      "doc_evolution",
    ]),
    item_id: z.string(),
    to_email: z.string().email(),
    subject: z.union([z.string(), z.null()]).optional(),
    message: z.union([z.string(), z.null()]).optional(),
    include_as_quote: z.boolean().optional().default(true),
    delivery_method: z
      .enum(["email", "akki_notification"])
      .optional()
      .default("akki_notification"),
  })
  .passthrough();
const SandboxIntakeIn = z
  .object({
    company_name: z.string().min(1).max(120),
    sector: z.enum([
      "financial_services",
      "saas",
      "logistics",
      "healthcare",
      "manufacturing",
      "retail",
      "real_estate",
      "other",
    ]),
    role: z.enum(["ned", "executive", "both"]),
    region: z.enum([
      "east_africa",
      "west_africa",
      "southern_africa",
      "north_africa",
      "europe",
      "north_america",
      "middle_east",
      "asia_pacific",
    ]),
    objective: z.union([z.string(), z.null()]).optional(),
    other_sector_name: z.union([z.string(), z.null()]).optional(),
    other_sector_description: z.union([z.string(), z.null()]).optional(),
    prospect_email: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SandboxEmailCaptureIn = z
  .object({ email: z.string().email() })
  .passthrough();
const TutorialDismissIn = z
  .object({ dismissed: z.boolean().default(true) })
  .partial()
  .passthrough();
const SandboxSampleAccept = z
  .object({
    title: z.string().min(4).max(200),
    filename: z.string().min(4).max(200),
    preview: z.string().min(80).max(20000),
  })
  .passthrough();
const ObjectiveCheckAnswerIn = z
  .object({
    answer: z.string().regex(/^(yes|partial|no|skip)$/),
    note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SandboxConvertIn = z
  .object({
    email: z.string().email(),
    password: z.string().min(8).max(128),
    name: z.string().min(1).max(120),
    keep_sandbox: z.boolean().optional().default(true),
  })
  .passthrough();
const SeededContextIn = z
  .object({
    company_name: z.string().min(1).max(120),
    sector: z.enum([
      "financial_services",
      "saas",
      "logistics",
      "healthcare",
      "manufacturing",
      "retail",
      "real_estate",
      "other",
    ]),
    role: z.enum(["ned", "executive", "both"]),
    region: z.enum([
      "east_africa",
      "west_africa",
      "southern_africa",
      "north_africa",
      "europe",
      "north_america",
      "middle_east",
      "asia_pacific",
    ]),
    objective: z.union([z.string(), z.null()]).optional(),
    other_sector_name: z.union([z.string(), z.null()]).optional(),
    other_sector_description: z.union([z.string(), z.null()]).optional(),
    seed_data: z.boolean().optional().default(true),
  })
  .passthrough();
const SandboxV2WelcomeIn = z
  .object({
    name: z.string().min(1).max(120),
    role: z.enum([
      "ceo",
      "ned",
      "company_secretary",
      "exco_member",
      "government_executive",
      "regulator",
      "investor",
      "other",
    ]),
    org_type: z.enum([
      "bank",
      "healthcare",
      "logistics",
      "saas",
      "government",
      "pre_ipo",
      "listed_corporate",
      "other",
    ]),
    hope: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SandboxV2PatchIn = z
  .object({
    state: z.union([z.string(), z.null()]),
    payload: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .partial()
  .passthrough();
const SandboxV2AddSentenceIn = z
  .object({ sentence: z.string().min(2).max(400) })
  .passthrough();
const SandboxV2SaveSendIn = z
  .object({ email: z.string().email() })
  .passthrough();
const routers__cycle__QuestionIn = z
  .object({
    text: z.string().min(8).max(400),
    category: z
      .enum([
        "audit",
        "risk",
        "operational",
        "strategic",
        "people",
        "financial",
        "regulatory",
        "general",
      ])
      .optional()
      .default("general"),
    source: z.union([z.string(), z.null()]).optional(),
    committee_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const QuestionPatch = z
  .object({
    text: z.union([z.string(), z.null()]),
    category: z.union([
      z.enum([
        "audit",
        "risk",
        "operational",
        "strategic",
        "people",
        "financial",
        "regulatory",
        "general",
      ]),
      z.null(),
    ]),
    status: z.union([z.enum(["open", "answered", "retired"]), z.null()]),
    committee_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ReporteeIn = z
  .object({
    name: z.string().min(2).max(120),
    email: z.string().email(),
    title: z.string().min(2).max(120),
    areas: z
      .array(
        z.enum([
          "audit",
          "risk",
          "operational",
          "strategic",
          "people",
          "financial",
          "regulatory",
          "general",
        ])
      )
      .optional(),
    committee_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ChecklistGenerateIn = z
  .object({
    cycle_name: z.string().min(3).max(120),
    deadline_date: z.string().min(4).max(40),
    reportee_ids: z.union([z.array(z.string()), z.null()]).optional(),
    committee_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ChecklistEdit = z
  .object({
    questions: z.array(z.object({}).partial().passthrough()),
    note_to_reportee: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DispatchIn = z
  .object({ checklist_ids: z.array(z.string()).min(1) })
  .passthrough();
const routers__cycle__AnswerIn = z
  .object({
    question_id: z.union([z.string(), z.null()]),
    question_text: z.union([z.string(), z.null()]),
    answer: z.string().max(4000).default(""),
  })
  .partial()
  .passthrough();
const SubmissionIn = z
  .object({
    answers: z.array(routers__cycle__AnswerIn),
    notes: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ReviewerIn = z
  .object({
    email: z.string().email(),
    name: z.string().min(2).max(120),
    title: z.string().min(2).max(120),
  })
  .passthrough();
const ReportComposeIn = z
  .object({
    cycle_name: z.string().min(3).max(120),
    title: z.string().min(4).max(200),
    description: z.union([z.string(), z.null()]).optional(),
    chain: z.array(ReviewerIn).min(1).max(5),
  })
  .passthrough();
const ReportPatchIn = z
  .object({
    title: z.union([z.string(), z.null()]),
    body: z.union([z.string(), z.null()]),
    note: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ReviewActionIn = z
  .object({
    action: z.enum(["approve", "send_back"]),
    note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const PolishIn = z
  .object({ instruction: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const CommitteesResponse = z
  .object({ committees: z.union([z.array(z.unknown()), z.null()]) })
  .partial()
  .passthrough();
const ScheduleResponse = z
  .object({
    schedule: z.union([z.object({}).partial().passthrough(), z.null()]),
  })
  .partial()
  .passthrough();
const CycleScheduleIn = z
  .object({
    cadence: z.enum(["weekly", "monthly"]).optional().default("weekly"),
    weekday: z
      .enum(["mon", "tue", "wed", "thu", "fri", "sat", "sun"])
      .optional()
      .default("mon"),
    cycle_name_template: z.string().min(3).max(120),
    deadline_offset_days: z
      .number()
      .int()
      .gte(2)
      .lte(60)
      .optional()
      .default(10),
    committee_id: z.union([z.string(), z.null()]).optional(),
    enabled: z.boolean().optional().default(true),
  })
  .passthrough();
const CycleActionsResponse = z
  .object({
    as_of: z.union([z.string(), z.null()]),
    context_id: z.union([z.string(), z.null()]),
    counts: z.union([z.unknown(), z.null()]),
    sections: z.union([z.unknown(), z.null()]),
  })
  .partial()
  .passthrough();
const _OutputSpecIn = z
  .object({
    kind: z.string().default("template"),
    template_id: z.union([z.string(), z.null()]),
    free_text: z.union([z.string(), z.null()]),
    formats: z.array(z.string()),
    final_due_date: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const _TeamMemberIn = z
  .object({
    name: z.string(),
    role: z.union([z.string(), z.null()]).optional().default(""),
    email: z.string(),
    contribution: z.union([z.string(), z.null()]).optional().default(""),
    due_date: z.union([z.string(), z.null()]).optional(),
    contribution_mode: z.string().optional().default("akki_account"),
    contributor_id: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.string(), z.null()]).optional(),
    adherence_score: z.union([z.number(), z.null()]).optional(),
    allow_email_reply: z
      .union([z.boolean(), z.null()])
      .optional()
      .default(false),
  })
  .passthrough();
const _TaskIn = z
  .object({
    name: z.string().min(1).max(200),
    objective: z.union([z.string(), z.null()]).optional().default(""),
    success_criteria: z.union([z.string(), z.null()]).optional().default(""),
    output_spec: z.union([_OutputSpecIn, z.null()]).optional(),
    team: z.array(_TeamMemberIn).optional(),
    state: z.string().optional().default("draft"),
    context_id: z.union([z.string(), z.null()]).optional(),
    due_date: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const _TaskPatch = z
  .object({
    name: z.union([z.string(), z.null()]),
    objective: z.union([z.string(), z.null()]),
    success_criteria: z.union([z.string(), z.null()]),
    output_spec: z.union([_OutputSpecIn, z.null()]),
    team: z.union([z.array(_TeamMemberIn), z.null()]),
    state: z.union([z.string(), z.null()]),
    due_date: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const _AgentPrefillIn = z
  .object({ name: z.string().min(1).max(200) })
  .passthrough();
const ObjectiveSourceResponse = z
  .object({
    objective: z.union([z.unknown(), z.null()]),
    source: z.union([z.unknown(), z.null()]),
    success_criteria: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const _ContributionPatchIn = z
  .object({
    status: z.string().min(1).max(40),
    note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const TaskHashResponse = z
  .object({
    task_id: z.union([z.string(), z.null()]),
    task_hash: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
    contributor_id: z.union([z.string(), z.null()]),
    readiness_score: z.union([z.number(), z.null()]),
    team: z.union([z.unknown(), z.null()]),
  })
  .partial()
  .passthrough();
const _ReviewCompleteIn = z
  .object({ skip_circulation: z.boolean().default(false) })
  .partial()
  .passthrough();
const _CirculationSendIn = z
  .object({
    reviewer_emails: z.array(z.string()).min(1).max(20),
    message: z.union([z.string(), z.null()]).optional(),
    base_url: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const TaskCirculationResponse = z
  .object({
    docs: z.union([z.array(z.unknown()), z.null()]),
    expires_at: z.union([z.string(), z.null()]),
    own_comments: z.union([z.unknown(), z.null()]),
    reviewer_email: z.union([z.string(), z.null()]),
    task: z.union([z.unknown(), z.null()]),
  })
  .partial()
  .passthrough();
const _CirculationSpan = z
  .object({
    start: z.number().int().gte(0),
    end: z.number().int().gte(0),
    text: z.string().min(1).max(2000),
  })
  .passthrough();
const _CirculationCommentIn = z
  .object({
    comment: z.string().min(1).max(4000),
    doc_id: z.union([z.string(), z.null()]).optional(),
    span: z.union([_CirculationSpan, z.null()]).optional(),
  })
  .passthrough();
const _ApplyCommentIn = z
  .object({ comment_id: z.string(), action: z.string().min(1).max(40) })
  .passthrough();
const TaskContributeResponse = z
  .object({
    contribution: z.union([z.unknown(), z.null()]),
    contributor_email: z.union([z.string(), z.null()]),
    docs: z.union([z.array(z.unknown()), z.null()]),
    expires_at: z.union([z.string(), z.null()]),
    peers: z.union([z.array(z.unknown()), z.null()]),
    task: z.union([z.unknown(), z.null()]),
    your_due_date: z.union([z.string(), z.null()]),
    your_status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const Body_contributor_upload_api_tasks_contribute__token__upload_post = z
  .object({
    file: z.instanceof(File),
    note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const _ContributorCommentIn = z
  .object({ comment: z.string().min(1).max(4000) })
  .passthrough();
const _ContributorSubmitIn = z
  .object({ final_note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const SubscribeIn = z
  .object({
    email: z.string().email(),
    name: z.union([z.string(), z.null()]).optional(),
    role: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ComposeIn = z
  .object({
    topic: z.string().min(8).max(280),
    audience_hint: z
      .union([z.string(), z.null()])
      .optional()
      .default("NEDs and operating executives"),
  })
  .passthrough();
const PortfolioMetricsOut = z
  .object({
    companies: z.number().int(),
    signals: z.number().int(),
    briefings: z.number().int(),
    documents: z.number().int(),
  })
  .passthrough();
const BoardToWatchOut = z
  .object({
    context_id: z.string(),
    name: z.string(),
    score: z.number(),
    reasons: z.array(z.string()),
  })
  .passthrough();
const BoardsToWatchOut = z
  .object({ items: z.array(BoardToWatchOut) })
  .passthrough();
const LastActionOut = z
  .object({
    context_id: z.union([z.string(), z.null()]),
    context_name: z.union([z.string(), z.null()]),
    surface: z.union([z.string(), z.null()]),
    artefact_id: z.union([z.string(), z.null()]),
    artefact_kind: z.union([z.string(), z.null()]).optional(),
    artefact_title: z.union([z.string(), z.null()]),
    action: z.union([z.string(), z.null()]),
    at: z.union([z.string(), z.null()]),
    deep_link: z.union([z.string(), z.null()]),
  })
  .passthrough();
const ReadinessOut = z
  .object({
    readiness_percent: z.union([z.number(), z.null()]),
    open_task_count: z.number().int(),
  })
  .passthrough();
const CardDrafts = z
  .object({
    count: z.number().int(),
    subtext: z.string(),
    oldest_days: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const CardReports = z
  .object({ count: z.number().int(), subtext: z.string() })
  .passthrough();
const CardPulse = z
  .object({
    count: z.number().int(),
    subtext: z.string(),
    critical: z.number().int(),
    opportunities: z.number().int(),
  })
  .passthrough();
const QuestionsDecomposition = z
  .object({
    board: z.number().int(),
    ceo: z.number().int(),
    team: z.number().int(),
  })
  .passthrough();
const CardQuestions = z
  .object({
    count: z.number().int(),
    subtext: z.string(),
    decomposition: QuestionsDecomposition,
  })
  .passthrough();
const CardEvents = z
  .object({ count: z.number().int(), subtext: z.string() })
  .passthrough();
const AttentionOut = z
  .object({
    drafts: CardDrafts,
    reports: CardReports,
    pulse: CardPulse,
    questions: CardQuestions,
    events: CardEvents,
  })
  .passthrough();
const TopSignalItem = z
  .object({
    id: z.string(),
    title: z.string(),
    subtitle: z.string(),
    severity: z.union([z.string(), z.null()]),
    timestamp: z.union([z.string(), z.null()]),
    deep_link: z.string(),
  })
  .passthrough();
const TopSignalsOut = z
  .object({
    chip: z.string(),
    items: z.array(TopSignalItem),
    total_available: z.number().int(),
  })
  .passthrough();
const EventIn = z
  .object({
    title: z.string().min(1).max(200),
    type: z.string().min(1).max(40),
    start_at: z.string().min(1),
    end_at: z.union([z.string(), z.null()]).optional(),
    location: z.union([z.string(), z.null()]).optional(),
    notes: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const EventOut = z
  .object({
    id: z.string(),
    context_id: z.string(),
    title: z.string(),
    type: z.string(),
    start_at: z.string(),
    end_at: z.union([z.string(), z.null()]),
    location: z.union([z.string(), z.null()]),
    notes: z.union([z.string(), z.null()]),
    source: z.string(),
    source_ref: z.union([z.string(), z.null()]),
    created_by_account_id: z.string(),
    created_at: z.string(),
    updated_at: z.string(),
    status: z.union([z.string(), z.null()]).optional(),
    confidence: z.union([z.number(), z.null()]).optional(),
    extracted_at: z.union([z.string(), z.null()]).optional(),
    extracted_by: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const EventsList = z
  .object({ items: z.array(EventOut), total: z.number().int() })
  .passthrough();
const EventPatch = z
  .object({
    title: z.union([z.string(), z.null()]),
    type: z.union([z.string(), z.null()]),
    start_at: z.union([z.string(), z.null()]),
    end_at: z.union([z.string(), z.null()]),
    location: z.union([z.string(), z.null()]),
    notes: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ExtractEventsOut = z
  .object({
    extracted: z.array(z.object({}).partial().passthrough()),
    persisted_draft_ids: z.array(z.string()),
    discarded: z.record(z.number().int()),
  })
  .passthrough();
const ConnectOut = z.object({ authorize_url: z.string() }).passthrough();
const StatusOut = z
  .object({
    connected: z.boolean(),
    provider: z.union([z.string(), z.null()]),
    connected_at: z.union([z.string(), z.null()]),
    last_sync_at: z.union([z.string(), z.null()]),
    last_sync_status: z.union([z.string(), z.null()]),
    last_sync_error: z.union([z.string(), z.null()]),
    synced_count: z.number().int(),
  })
  .passthrough();
const SyncOut = z
  .object({
    imported: z.number().int(),
    skipped: z.number().int(),
    errors: z.number().int(),
  })
  .passthrough();
const IssueInviteIn = z
  .object({
    email: z.string().email(),
    cohort_tag: z.string().min(1).max(100),
    trial_length_days: z.number().int().gte(1).lte(365).optional().default(21),
    first_name: z.union([z.string(), z.null()]).optional(),
    logo_name: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const CopyOverrideIn = z
  .object({ fields: z.record(z.string()) })
  .partial()
  .passthrough();
const FinishIn = z
  .object({
    session_id: z.string().min(4).max(512),
    magic_link_token: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const CheckoutIn = z
  .object({
    plan_id: z.enum(["free", "pro", "team"]),
    origin_url: z.string().min(8).max(400),
  })
  .passthrough();
const NotifyOut = z
  .object({
    coming_soon: z.boolean(),
    notified: z.boolean(),
    already_subscribed: z.boolean(),
    message: z.string(),
  })
  .passthrough();
const OnboardingBriefsResponse = z
  .object({ slides: z.union([z.array(z.unknown()), z.null()]) })
  .partial()
  .passthrough();
const UserCreateIn = z
  .object({
    email: z.string().email(),
    first_name: z.union([z.string(), z.null()]).optional(),
    logo_name: z.union([z.string(), z.null()]).optional(),
    role: z.union([z.string(), z.null()]).optional(),
    cohort_tag: z.union([z.string(), z.null()]).optional(),
    initial_password: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ForceResetIn = z
  .object({ send_email: z.boolean().default(true) })
  .partial()
  .passthrough();
const DeleteAccountRequest = z.object({ confirm: z.string() }).passthrough();
const ForgotPasswordIn = z.object({ email: z.string().email() }).passthrough();
const PasswordResetTokenResponse = z
  .object({
    email_masked: z.union([z.string(), z.null()]),
    valid: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const ResetPasswordIn = z
  .object({ new_password: z.string().min(10).max(200) })
  .passthrough();
const DocumentShareIn = z
  .object({
    recipient_emails: z.array(z.string().email()).min(1).max(10),
    message: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DocumentEngagementResponse = z
  .object({
    linked_count: z.union([z.number(), z.null()]),
    linked_documents: z.union([z.array(z.unknown()), z.null()]),
    readers: z.union([z.array(z.unknown()), z.null()]),
    share_count: z.union([z.number(), z.null()]),
    shares: z.union([z.array(z.unknown()), z.null()]),
    unique_readers: z.union([z.number(), z.null()]),
    view_count: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const GoalIn = z
  .object({
    title: z.string().min(2).max(180),
    description: z.union([z.string(), z.null()]).optional(),
    department: z
      .enum(["ceo", "cfo", "coo", "commercial", "board"])
      .optional()
      .default("ceo"),
    category: z
      .enum([
        "revenue",
        "customer",
        "product",
        "people",
        "operations",
        "compliance",
      ])
      .optional()
      .default("operations"),
    initiatives_count: z.number().int().gte(0).lte(99).optional().default(0),
    owner_name: z.union([z.string(), z.null()]).optional(),
    target_metric: z.union([z.string(), z.null()]).optional(),
    target_value: z.union([z.string(), z.null()]).optional(),
    target_date: z.union([z.string(), z.null()]).optional(),
    current_value: z.union([z.string(), z.null()]).optional(),
    current_score: z.union([z.number(), z.null()]).optional(),
    probability: z.union([z.number(), z.null()]).optional(),
    status: z
      .enum(["on_track", "at_risk", "off_track", "achieved", "abandoned"])
      .optional()
      .default("on_track"),
  })
  .passthrough();
const GoalPatch = z
  .object({
    title: z.union([z.string(), z.null()]),
    description: z.union([z.string(), z.null()]),
    department: z.union([
      z.enum(["ceo", "cfo", "coo", "commercial", "board"]),
      z.null(),
    ]),
    category: z.union([
      z.enum([
        "revenue",
        "customer",
        "product",
        "people",
        "operations",
        "compliance",
      ]),
      z.null(),
    ]),
    initiatives_count: z.union([z.number(), z.null()]),
    owner_name: z.union([z.string(), z.null()]),
    target_metric: z.union([z.string(), z.null()]),
    target_value: z.union([z.string(), z.null()]),
    target_date: z.union([z.string(), z.null()]),
    current_value: z.union([z.string(), z.null()]),
    current_score: z.union([z.number(), z.null()]),
    probability: z.union([z.number(), z.null()]),
    status: z.union([
      z.enum(["on_track", "at_risk", "off_track", "achieved", "abandoned"]),
      z.null(),
    ]),
  })
  .partial()
  .passthrough();
const ExtractFromDocIn = z
  .object({
    doc_id: z.string(),
    replace_existing: z.boolean().optional().default(false),
  })
  .passthrough();
const ChatAuditPanelResponse = z
  .object({
    audit_id: z.union([z.string(), z.null()]),
    message_id: z.union([z.string(), z.null()]),
    protective_event: z.union([z.unknown(), z.null()]),
    protective_layer_prose: z.union([z.string(), z.null()]),
    provider_prose: z.union([z.string(), z.null()]),
    references: z.union([z.unknown(), z.null()]),
    scores: z.union([z.unknown(), z.null()]),
    shielding_prose: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ChatAuditAggregateResponse = z
  .object({
    average_dilution: z.union([z.number(), z.null()]),
    average_exposure_reduction: z.union([z.number(), z.null()]),
    headline_prose: z.union([z.string(), z.null()]),
    identifiers_shielded: z.union([z.number(), z.null()]),
    llm_calls: z.union([z.number(), z.null()]),
    message_count: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const SeedPayload = z
  .object({
    source: z.string().min(1).max(40),
    source_id: z.string().min(1).max(120),
    preview_text: z.string().max(4000).optional().default(""),
    attached_references: z.array(z.string()).max(20).optional(),
    sub_module_hint: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const CreateSessionIn = z
  .object({
    sub_module: z.string().min(4).max(40),
    seed_payload: z.union([SeedPayload, z.null()]).optional(),
  })
  .passthrough();
const _UpdateSessionTitleIn = z.object({ title: z.string().min(1).max(80) });
const SubmitFramingIn = z
  .object({ framing_text: z.string().min(20).max(4000) })
  .passthrough();
const SubmitAnswerIn = z
  .object({ answer_text: z.string().min(2).max(4000) })
  .passthrough();
const RefuseIn = z
  .object({ operator_reason: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const _PostBody = z
  .object({
    area: z.string(),
    action: z.enum(["increment", "suppress", "unsuppress"]),
  })
  .passthrough();
const Body_restore_one_api_admin_solva_legacy_restore_post = z
  .object({ session_id: z.string() })
  .passthrough();
const ArtefactFromSolvaIn = z
  .object({ session_id: z.string().min(1).max(120) })
  .passthrough();
const ChatModelsResponse = z
  .object({
    default_model_id: z.union([z.string(), z.null()]),
    models: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const LinkedContextIn = z
  .object({
    ctx_type: z.string().min(1).max(40),
    ctx_id: z.string().min(1).max(80),
  })
  .passthrough();
const ChatCreateIn = z
  .object({
    title: z.union([z.string(), z.null()]),
    model_id: z.string().default("claude-sonnet-4-5"),
    shielding_policy: z.enum(["auto", "always", "off"]).default("auto"),
    context_id: z.union([z.string(), z.null()]),
    linked_context: z.union([LinkedContextIn, z.null()]),
  })
  .partial()
  .passthrough();
const Body_attach_to_chat_api_chats__chat_id__attach_post = z
  .object({ file: z.instanceof(File) })
  .passthrough();
const ChatAttachmentResponse = z
  .object({
    chat_id: z.union([z.string(), z.null()]),
    context_id: z.union([z.string(), z.null()]),
    document_id: z.union([z.string(), z.null()]),
    name: z.union([z.string(), z.null()]),
    original_filename: z.union([z.string(), z.null()]),
    mime_type: z.union([z.string(), z.null()]),
    size_bytes: z.union([z.number(), z.null()]),
    char_len: z.union([z.number(), z.null()]),
    sensitivity: z.union([z.unknown(), z.null()]),
    storage_key: z.union([z.string(), z.null()]),
    created_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ChatPatchIn = z
  .object({
    title: z.union([z.string(), z.null()]),
    model_id: z.union([z.string(), z.null()]),
    shielding_policy: z.union([z.enum(["auto", "always", "off"]), z.null()]),
    context_id: z.union([z.string(), z.null()]),
    linked_context: z.union([LinkedContextIn, z.null()]),
    clear_linked_context: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const MessageSendIn = z
  .object({
    content: z.string().min(1).max(20000),
    acknowledge_unshielded: z.boolean().optional().default(false),
    attached_document_ids: z.array(z.string()).max(10).optional(),
    force_class: z
      .union([
        z.enum([
          "trivial",
          "light_substantive",
          "substantive_analytical",
          "strategic_deliverable",
        ]),
        z.null(),
      ])
      .optional(),
    show_pass_1: z.boolean().optional().default(false),
  })
  .passthrough();
const ChatAuditResponse = z
  .object({
    chat_id: z.union([z.string(), z.null()]),
    rows: z.union([z.array(z.unknown()), z.null()]),
    verification_note: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const SignalActionIn = z
  .object({
    action_type: z.string().regex(/^(acted|shared)$/),
    recommendation_idx: z.union([z.number(), z.null()]).optional(),
    recommendation_label: z.union([z.string(), z.null()]).optional(),
    recipients: z.union([z.array(z.string()), z.null()]).optional(),
    note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const state = z.union([z.string(), z.null()]).optional().default("active");
const limit = z.union([z.number(), z.null()]).optional();
const routers__pulse__CommentIn = z
  .object({ note: z.string().min(1).max(2000) })
  .passthrough();
const routers__pulse__ShareIn = z
  .object({
    recipients: z.array(z.string()),
    note: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ResolveIn = z
  .object({ resolution_note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const AgendaItemIn = z
  .object({
    id: z.union([z.string(), z.null()]).optional(),
    label: z.string().min(1).max(200),
    owner_label: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const AgendaIn = z
  .object({
    title: z.string().min(1).max(200),
    items: z.array(AgendaItemIn).max(30).optional(),
  })
  .passthrough();
const CycleTeamResponse = z
  .object({
    agenda_id: z.union([z.string(), z.null()]),
    cycle_id: z.union([z.string(), z.null()]),
    members: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const TeamMemberIn = z
  .object({
    id: z.union([z.string(), z.null()]).optional(),
    name: z.string().min(1).max(120),
    email: z.string().min(3).max(200),
    role: z.union([z.string(), z.null()]).optional(),
    contribution_description: z.string().min(1).max(600),
    owns_item_ids: z.array(z.string()).optional(),
  })
  .passthrough();
const TeamMemberPatch = z
  .object({
    name: z.union([z.string(), z.null()]),
    email: z.union([z.string(), z.null()]),
    role: z.union([z.string(), z.null()]),
    contribution_description: z.union([z.string(), z.null()]),
    owns_item_ids: z.union([z.array(z.string()), z.null()]),
  })
  .partial()
  .passthrough();
const CycleContributionsListResponse = z
  .object({
    agenda_id: z.union([z.string(), z.null()]),
    contributions: z.union([z.array(z.unknown()), z.null()]),
    cycle_id: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ContributionIn = z
  .object({
    agenda_item_id: z.union([z.string(), z.null()]),
    team_member_id: z.union([z.string(), z.null()]),
    kind: z
      .string()
      .regex(/^(note|document|email|chat)$/)
      .default("note"),
    source_doc_id: z.union([z.string(), z.null()]),
    body_text: z.union([z.string(), z.null()]),
    title: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const CycleContributionResponse = z
  .object({
    id: z.union([z.string(), z.null()]),
    agenda_id: z.union([z.string(), z.null()]),
    agenda_item_id: z.union([z.string(), z.null()]),
    body_text: z.union([z.string(), z.null()]),
    context_id: z.union([z.string(), z.null()]),
    created_at: z.union([z.string(), z.null()]),
    cycle_id: z.union([z.string(), z.null()]),
    kind: z.union([z.string(), z.null()]),
    scored_at: z.union([z.string(), z.null()]),
    scored_by: z.union([z.string(), z.null()]),
    scores: z.union([z.unknown(), z.null()]),
    source_doc_id: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
    team_member_id: z.union([z.string(), z.null()]),
    title: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ScoreIn = z
  .object({
    relevance: z.union([z.number(), z.null()]),
    fullness: z.union([z.number(), z.null()]),
    readiness: z.union([z.number(), z.null()]),
    rationale: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const FollowUpsDraftIn = z
  .object({ item_ids: z.union([z.array(z.string()), z.null()]) })
  .partial()
  .passthrough();
const FollowUpDraftsResponse = z
  .object({
    count: z.union([z.number(), z.null()]),
    drafts: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const CycleFollowUpsResponse = z
  .object({
    agenda_id: z.union([z.string(), z.null()]),
    cycle_id: z.union([z.string(), z.null()]),
    followups: z.union([z.array(z.unknown()), z.null()]),
  })
  .partial()
  .passthrough();
const CycleCreateIn = z
  .object({ title: z.string().min(1).max(200) })
  .passthrough();
const ApplyTemplateIn = z
  .object({ template_key: z.string().min(1).max(64) })
  .passthrough();
const QuickActionOrderOut = z
  .object({ order: z.array(z.string()), canonical: z.array(z.string()) })
  .passthrough();
const CatalogueMemberIn = z
  .object({ name: z.string().min(1).max(120), email: z.string().email() })
  .passthrough();
const CatalogueMemberPatch = z
  .object({
    name: z.union([z.string(), z.null()]),
    email: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const SubmitForBoardOut = z
  .object({
    brief_id: z.string(),
    board_status: z.string(),
    submitted_at: z.string(),
    submitter_account_id: z.string(),
  })
  .passthrough();
const AssignmentCreateIn = z
  .object({
    ned_ids: z.union([z.array(z.string()), z.null()]),
    cohort_id: z.union([z.string(), z.null()]),
    note: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const AcceptOut = z
  .object({
    assignment_id: z.string(),
    brief_id: z.string(),
    status: z.string(),
    accepted_at: z.string(),
  })
  .passthrough();
const DeclineIn = z
  .object({ reason: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const BriefsCountResponse = z
  .object({
    briefs: z.union([z.array(z.unknown()), z.null()]),
    count: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const MeetingCreate = z
  .object({
    context_id: z.string().min(1),
    committee: z.string().min(1).max(80),
    title: z.string().min(1).max(200),
    scheduled_at: z.string().min(10).max(40),
    paper_doc_ids: z.union([z.array(z.string()), z.null()]).optional(),
  })
  .passthrough();
const MeetingPatch = z
  .object({
    title: z.union([z.string(), z.null()]),
    committee: z.union([z.string(), z.null()]),
    scheduled_at: z.union([z.string(), z.null()]),
    paper_doc_ids: z.union([z.array(z.string()), z.null()]),
    formulated_question: z.union([z.string(), z.null()]),
    state: z.union([z.enum(["pre", "in", "post", "closed"]), z.null()]),
    prep_state: z.union([
      z.enum(["not_started", "started", "ready"]),
      z.null(),
    ]),
  })
  .partial()
  .passthrough();
const NoteCreate = z
  .object({
    kind: z.enum(["qna", "decision", "open"]),
    body: z.string().min(1).max(4000),
    related_question_index: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const PositionCreate = z
  .object({
    decision_text: z.string().min(1).max(400),
    position: z.enum(["for", "against", "abstained"]),
    private_note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const FollowupDraft = z
  .object({
    to_email: z.string().min(3).max(200),
    to_name: z.union([z.string(), z.null()]).optional(),
    subject: z.string().min(1).max(200),
    body_md: z.string().min(1).max(8000),
  })
  .passthrough();
const BriefIn = z
  .object({
    kind: z.string().min(1).max(40),
    objective: z.string().min(8).max(600),
    deep: z.boolean().optional().default(false),
  })
  .passthrough();
const ByContextSummaryResponse = z
  .object({
    by_context: z.union([z.array(z.unknown()), z.null()]),
    by_kind: z.union([z.array(z.unknown()), z.null()]),
    total: z.union([z.number(), z.null()]),
    total_pending: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const AcceptIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const RejectIn = z
  .object({ reason: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const EnterpriseInterestIn = z
  .object({
    use_case: z.union([z.string(), z.null()]),
    company_size: z.union([z.string(), z.null()]),
    timing: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const OutlineIn = z
  .object({
    intent: z.string().min(12).max(600),
    audience: z.union([z.string(), z.null()]).optional(),
    target_slides: z.union([z.number(), z.null()]).optional(),
    parent_outline_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const GenerateIn = z
  .object({
    outline_id: z.string(),
    confirmed: z.boolean().optional().default(false),
    edits: z.union([z.object({}).partial().passthrough(), z.null()]).optional(),
  })
  .passthrough();
const routers__decks__FeedbackIn = z
  .object({
    rating: z.string().regex(/^(up|down)$/),
    comment: z.union([z.string(), z.null()]).optional(),
    will_regenerate: z.boolean().optional().default(false),
    regen_reason: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const WalkinIn = z
  .object({
    kind: z.enum(["brief", "minutes", "deck"]),
    artefact_id: z.string().min(4).max(80),
    context_id: z.string().min(4).max(80),
  })
  .passthrough();
const AdminAuthEventsResponse = z
  .object({
    by_credential: z.union([z.unknown(), z.null()]),
    by_failure_reason: z.union([z.unknown(), z.null()]),
    dual_credentials_mismatched: z.union([z.number(), z.null()]),
    dual_credentials_seen: z.union([z.number(), z.null()]),
    failure: z.union([z.number(), z.null()]),
    failure_rate_pct: z.union([z.number(), z.null()]),
    recent: z.union([z.array(z.unknown()), z.null()]),
    sampled_events: z.union([z.number(), z.null()]),
    success: z.union([z.number(), z.null()]),
    top_paths: z.union([z.unknown(), z.null()]),
    window_hours: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const routers__admin_journal__BackfillRequest = z
  .object({
    limit: z.union([z.number(), z.null()]),
    sleep_ms: z.number().int().gte(0).lte(10000).default(750),
    refresh: z.boolean().default(false),
    concurrency: z.number().int().gte(1).lte(8).default(1),
  })
  .partial()
  .passthrough();
const CohortApplicationIn = z
  .object({
    name: z.string().min(2).max(200),
    email: z.string().email(),
    organisation: z.string().min(1).max(200),
    role: z.string().min(1).max(200),
    use_case: z.string().min(1).max(2000),
    referral_source: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const routers__admin_shield_backfill__BackfillRequest = z
  .object({
    batch_size: z.number().int().gte(1).lte(500).default(50),
    sleep_ms: z.number().int().gte(0).lte(10000).default(200),
    dry_run: z.boolean().default(false),
    limit: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const FirstSessionResetIn = z
  .object({ account_email: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const RecentDocSeedIn = z
  .object({
    account_email: z.union([z.string(), z.null()]),
    context_name: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const _SeedQuestionIn = z
  .object({
    context_id: z.union([z.string(), z.null()]).optional(),
    cycle_id: z.union([z.string(), z.null()]).optional(),
    assignee_account_id: z.union([z.string(), z.null()]).optional(),
    text: z.string().min(3).max(2000),
    asker_role: z.union([z.string(), z.null()]).optional(),
    status: z.union([z.string(), z.null()]).optional().default("open"),
  })
  .passthrough();
const ActiveContextIn = z
  .object({
    context_id: z.string().min(1).max(128),
    from_context_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const DemoSensitivityIn = z
  .object({ text: z.string().min(4).max(4000) })
  .passthrough();
const routers__studio__ShareIn = z
  .object({
    to_email: z.string().min(4).max(120),
    to_name: z.union([z.string(), z.null()]).optional(),
    message: z.union([z.string(), z.null()]).optional(),
    external: z.boolean().optional().default(false),
  })
  .passthrough();
const ShareEmailIn = z
  .object({
    to_email: z.string().email(),
    to_name: z.union([z.string(), z.null()]).optional(),
    message: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const BlockCreateIn = z
  .object({
    kind: z.string().min(1).max(20),
    content: z.object({}).partial().passthrough().optional(),
    after_block_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const BlockPatchIn = z
  .object({ content: z.object({}).partial().passthrough() })
  .passthrough();
const BlockMoveIn = z
  .object({ to_order: z.number().int().gte(0) })
  .passthrough();
const ReorderIn = z.object({ block_ids: z.array(z.string()) }).passthrough();
const ImageUploadIn = z
  .object({
    filename: z.string().min(1).max(200),
    mime_type: z.string().min(1).max(80),
    data_base64: z.string().min(4).max(8388608),
    alt: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SubmitReviewIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const routers__studio_blocks__ApproveIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const SendIn = z
  .object({
    to: z.array(z.string()).min(1).max(20),
    subject: z.union([z.string(), z.null()]).optional(),
    body_note: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const routers__early_access__RegisterIn = z
  .object({
    email: z.string().email(),
    full_name: z.union([z.string(), z.null()]).optional(),
    company: z.union([z.string(), z.null()]).optional(),
    role: z
      .union([z.enum(["executive", "ned", "chair", "other"]), z.null()])
      .optional(),
    board_count: z.union([z.number(), z.null()]).optional(),
    message: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const routers__daily_review__ApproveIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const approve_review_item_api_me_review_queue_items__kind___item_id__approve_post_Body =
  z.union([routers__daily_review__ApproveIn, z.null()]);
const reject_review_item_api_me_review_queue_items__kind___item_id__reject_post_Body =
  z.union([RejectIn, z.null()]);
const SolvaCycleEditIn = z
  .object({
    questions: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
    note: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const edit_review_item_api_me_review_queue_items__kind___item_id__edit_post_Body =
  z.union([SolvaCycleEditIn, z.null()]);
const StateOnlyResponse = z
  .object({ state: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const IntakeIn = z
  .object({
    role: z.string().min(1).max(32),
    primary_context_name: z.string().min(1).max(80),
    top_of_mind: z.string().min(1).max(240),
  })
  .passthrough();
const DoorIn = z.object({ door: z.string().min(1).max(16) }).passthrough();
const ArtefactIn = z
  .object({ kind: z.string().min(1).max(32), id: z.string().min(1).max(64) })
  .passthrough();
const CompleteIn = z.object({ artefact: ArtefactIn }).passthrough();
const GovernancePanelResponse = z
  .object({
    audit_log: z.union([z.unknown(), z.null()]),
    connected_models: z.union([z.unknown(), z.null()]),
    inbound: z.union([z.unknown(), z.null()]),
    sensitivity: z.union([z.unknown(), z.null()]),
    shielding: z.union([z.unknown(), z.null()]),
    synisense: z.union([z.unknown(), z.null()]),
  })
  .partial()
  .passthrough();
const ExportIn = z
  .object({
    action: z.union([z.string(), z.null()]),
    since: z.union([z.string(), z.null()]),
    until: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const StartV2In = z
  .object({
    cluster_id: z.union([z.string(), z.null()]).optional(),
    auto_cluster: z.boolean().optional().default(true),
    intent: z.string().min(20).max(1200),
    context_id: z.union([z.string(), z.null()]).optional(),
    submodule: z.string().optional().default("seek_clarity"),
    persona: z.union([z.string(), z.null()]).optional(),
    pro_tier: z.boolean().optional().default(false),
    sandbox: z.boolean().optional().default(false),
    intake_seed: z
      .union([z.object({}).partial().passthrough(), z.null()])
      .optional(),
  })
  .passthrough();
const FrameAuditDecisionIn = z
  .object({ decision: z.string().regex(/^(proceed|get_more|pause)$/) })
  .passthrough();
const AttachDocumentIn = z
  .object({ document_id: z.string().min(1).max(120) })
  .passthrough();
const ForkV2In = z
  .object({
    to_submodule: z.string().min(4).max(40),
    persona: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const IntentClassifyIn = z
  .object({ intent: z.string().min(20).max(1200) })
  .passthrough();
const TurnV2In = z
  .object({ user_text: z.string().min(2).max(4000) })
  .passthrough();
const HandoffCycleIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const EarlyAccessApplication = z
  .object({
    first_name: z.string().min(1).max(80),
    last_name: z.string().min(1).max(80),
    work_email: z.string().email(),
    company: z.string().min(1).max(160),
    role_title: z.string().min(1).max(160),
    role_type: z.string().min(1).max(40),
    linkedin_url: z.union([z.string(), z.null()]).optional(),
    valuable_text: z.union([z.string(), z.null()]).optional(),
    cohort_understood: z.boolean(),
  })
  .passthrough();
const ContactSubmission = z
  .object({
    name: z.string().min(1).max(160),
    work_email: z.string().email(),
    company: z.union([z.string(), z.null()]).optional(),
    message: z.string().min(1).max(4000),
  })
  .passthrough();
const FormPayload = z
  .object({
    name: z.string().max(80),
    role: z.string(),
    role_other: z.string().max(120).optional().default(""),
    org_type: z.string(),
    org_type_other: z.string().max(120).optional().default(""),
    org_size: z.string(),
    situation: z.string().max(1500).optional().default(""),
    emphasis: z.array(z.string()).optional(),
    email: z.string().max(200).optional().default(""),
  })
  .passthrough();
const _BatchMsgIds = z
  .object({ msg_ids: z.array(z.string()).max(200) })
  .partial()
  .passthrough();
const ShieldInvokeRequest = z
  .object({
    purpose: z.string().min(1).max(128),
    content: z.string().min(1).max(200000),
    model_preference: z
      .enum(["analytical", "generative", "balanced"])
      .optional()
      .default("balanced"),
    schema: z
      .union([z.object({}).partial().passthrough(), z.null()])
      .optional(),
    consumer_id: z.string().min(1).max(64),
    tenant_id: z.string().min(1).max(128),
    user_id: z.string().min(1).max(128),
  })
  .passthrough();
const TrustReceiptV1 = z
  .object({
    receipt_id: z.string(),
    audit_id: z.string(),
    version: z.string().optional().default("v1"),
    tenant_id: z.string(),
    consumer_id: z.string(),
    purpose: z.string(),
    timestamp: z.string(),
    llm_provider: z.string(),
    llm_model: z.string(),
    de_id_summary: z.record(z.number().int()),
    dilution_score: z.number(),
    exposure_reduction_score: z.number(),
    request_hash: z.string(),
    response_hash: z.string(),
    signature: z.string(),
  })
  .passthrough();
const ShieldInvokeResponse = z
  .object({
    response: z.string(),
    trust_receipt: TrustReceiptV1,
    audit_id: z.string(),
  })
  .passthrough();
const ErrorEnvelope = z
  .object({
    error_class: z.string(),
    message: z.string(),
    audit_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SignalQueryFilter = z
  .object({
    signal_category: z.union([
      z.enum([
        "profile",
        "anomaly",
        "life_stage",
        "risk",
        "operational",
        "compliance",
      ]),
      z.null(),
    ]),
    signal_type: z.union([z.string(), z.null()]),
    entity_ref: z.union([z.string(), z.null()]),
    confidence_min: z.union([z.number(), z.null()]),
    derivation_source: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const SignalQueryPagination = z
  .object({
    cursor: z.union([z.string(), z.null()]),
    limit: z.number().int().gte(1).lte(500).default(50),
  })
  .partial()
  .passthrough();
const SignalQueryRequest = z
  .object({
    filter: SignalQueryFilter.optional(),
    pagination: SignalQueryPagination.optional(),
    tenant_id: z.string(),
    consumer_id: z.string(),
  })
  .passthrough();
const Signal = z
  .object({
    signal_id: z.string(),
    tenant_id: z.string(),
    context_id: z.union([z.string(), z.null()]).optional(),
    signal_category: z.enum([
      "profile",
      "anomaly",
      "life_stage",
      "risk",
      "operational",
      "compliance",
    ]),
    signal_type: z.string().min(1).max(64),
    entity_ref: z.union([z.string(), z.null()]).optional(),
    payload: z.object({}).partial().passthrough().optional(),
    confidence: z.number().gte(0).lte(1),
    derivation_source: z.string().min(1).max(128),
    created_at: z.string(),
    expires_at: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const SignalQueryResponse = z
  .object({
    signals: z.array(Signal),
    next_cursor: z.union([z.string(), z.null()]).optional(),
    total_estimate: z.number().int(),
  })
  .passthrough();
const SubscriptionRequest = z
  .object({
    signal_types: z
      .array(
        z.enum([
          "anomaly_flag",
          "life_stage",
          "churn_risk",
          "behavioral_vector",
          "compliance_trigger",
          "operational_health",
        ])
      )
      .optional(),
    delivery: z.enum(["webhook", "stream", "poll"]).optional().default("poll"),
    webhook_url: z.union([z.string(), z.null()]).optional(),
    tenant_id: z.string(),
    consumer_id: z.string(),
  })
  .passthrough();
const SubscriptionResponse = z
  .object({
    subscription_id: z.string(),
    status: z
      .enum(["pending", "active", "rejected"])
      .optional()
      .default("pending"),
    delivery: z.string(),
    created_at: z.string(),
  })
  .passthrough();
const SignalTypeDefinition = z
  .object({
    signal_type: z.string(),
    signal_category: z.enum([
      "profile",
      "anomaly",
      "life_stage",
      "risk",
      "operational",
      "compliance",
    ]),
    description: z.string(),
    payload_schema: z.object({}).partial().passthrough(),
    version: z.string().optional().default("v1"),
  })
  .passthrough();
const SignalTypeCatalogue = z
  .object({ signal_types: z.array(SignalTypeDefinition) })
  .passthrough();
const StatusKindResponse = z
  .object({
    status: z.union([z.string(), z.null()]),
    kind: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ExcoCreateIn = z
  .object({
    name: z.string().min(1).max(120),
    description: z.union([z.string(), z.null()]).optional(),
    member_account_ids: z.array(z.string()).max(64).optional(),
  })
  .passthrough();
const ExcoMember = z
  .object({
    account_id: z.string(),
    name: z.string(),
    role: z.string(),
    sub_role: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ExcoTeamOut = z
  .object({
    id: z.string(),
    context_id: z.string(),
    name: z.string(),
    description: z.union([z.string(), z.null()]).optional(),
    member_account_ids: z.array(z.string()),
    members: z.union([z.array(ExcoMember), z.null()]).optional(),
    created_by: z.string(),
    created_at: z.string(),
    updated_at: z.string(),
    status: z.enum(["active", "archived"]),
    my_role: z
      .union([z.enum(["creator", "member", "outside"]), z.null()])
      .optional(),
  })
  .passthrough();
const ExcoUpdateIn = z
  .object({
    name: z.union([z.string(), z.null()]),
    description: z.union([z.string(), z.null()]),
    status: z.union([z.enum(["active", "archived"]), z.null()]),
  })
  .partial()
  .passthrough();
const ExcoAddMemberIn = z.object({ account_id: z.string() }).passthrough();
const CadencePayload = z
  .object({
    interval: z.union([z.string(), z.null()]),
    scheduled_at: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const CompilationCreate = z
  .object({
    title: z.string().min(1).max(200),
    artefact_type: z.string(),
    template_key: z.string().min(1).max(80).optional().default("standard"),
    source_ids: z.array(z.string()).optional(),
    contributor_ids: z.array(z.string()).optional(),
    cadence_kind: z.string(),
    cadence_payload: CadencePayload.optional(),
    formats: z.array(z.string()).optional(),
  })
  .passthrough();
const CompilationStartResponse = z
  .object({
    compilation_id: z.union([z.string(), z.null()]),
    export_id: z.union([z.string(), z.null()]),
    idempotent: z.union([z.boolean(), z.null()]),
    status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const RecentViewIn = z
  .object({
    surface_path: z.string().min(1).max(300),
    label: z.string().min(1).max(160),
    context_id: z.union([z.string(), z.null()]).optional(),
    artefact_id: z.union([z.string(), z.null()]).optional(),
    artefact_kind: z.union([z.string(), z.null()]).optional(),
    deep_link: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const StatusAssessmentBody = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const StrategicGoalUpdateIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const Body_work_studio_enhance_stream_api_contexts__context_id__work_studio_enhance__kind__stream_post =
  z
    .object({
      instructions: z.string(),
      output_format: z.string().optional().default("auto"),
      source_artefact_id: z.union([z.string(), z.null()]).optional(),
      file: z.union([z.instanceof(File), z.null()]).optional(),
    })
    .passthrough();
const routers__feedback__FeedbackIn = z
  .object({
    text: z.string().min(1).max(4000),
    tag: z.enum(["Broken", "Wrong", "Great"]),
    surface_path: z.string().min(1).max(200),
  })
  .passthrough();
const EarlyAccessIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const SpecialAskIn = z
  .object({
    referral_name: z.union([z.string(), z.null()]),
    referral_email: z.union([z.string(), z.null()]),
    case_study_consent: z.union([z.boolean(), z.null()]),
    testimonial_text: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const routers__questions__QuestionIn = z
  .object({
    text: z.string().min(1).max(2000),
    assignee_account_id: z.union([z.string(), z.null()]).optional(),
    agenda_item_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const routers__questions__AnswerIn = z
  .object({ text: z.string().min(1).max(4000) })
  .passthrough();
const MarkAnsweredIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const routers__questions__ShareIn = z
  .object({
    recipient_emails: z.array(z.string()).min(1).max(10),
    message: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const LinkResponseIn = z
  .object({ document_id: z.string().min(1).max(200) })
  .passthrough();
const NewsItemOut = z
  .object({
    id: z.string(),
    title: z.string(),
    summary: z.string(),
    url: z.string(),
    source: z.string(),
    published_at: z.string().datetime({ offset: true }),
    regions: z.array(z.string()),
  })
  .passthrough();
const NewsFeedOut = z
  .object({
    items: z.array(NewsItemOut),
    total: z.number().int(),
    region_applied: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ProfileOut = z
  .object({ country: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const ProfilePatchIn = z
  .object({ country: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const TaskInitiativeIn = z
  .object({
    title: z.string().min(2).max(180),
    body: z.union([z.string(), z.null()]).optional(),
    category: z
      .enum([
        "revenue",
        "customer",
        "product",
        "people",
        "operations",
        "compliance",
      ])
      .optional()
      .default("operations"),
    owner_role: z
      .union([
        z.enum([
          "CEO",
          "CFO",
          "COO",
          "CRO",
          "CTO",
          "CHRO",
          "CMO",
          "CIO",
          "OTHER",
        ]),
        z.null(),
      ])
      .optional(),
    parent_objective_id: z.union([z.string(), z.null()]).optional(),
    status: z
      .enum(["on_track", "at_risk", "off_track", "achieved", "not_started"])
      .optional()
      .default("not_started"),
    performance_score: z.number().int().gte(0).lte(100).optional().default(0),
    probability_score: z.number().int().gte(0).lte(100).optional().default(0),
    source_document_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const TaskInitiativePatch = z
  .object({
    title: z.union([z.string(), z.null()]),
    body: z.union([z.string(), z.null()]),
    category: z.union([
      z.enum([
        "revenue",
        "customer",
        "product",
        "people",
        "operations",
        "compliance",
      ]),
      z.null(),
    ]),
    owner_role: z.union([
      z.enum([
        "CEO",
        "CFO",
        "COO",
        "CRO",
        "CTO",
        "CHRO",
        "CMO",
        "CIO",
        "OTHER",
      ]),
      z.null(),
    ]),
    parent_objective_id: z.union([z.string(), z.null()]),
    status: z.union([
      z.enum(["on_track", "at_risk", "off_track", "achieved", "not_started"]),
      z.null(),
    ]),
    performance_score: z.union([z.number(), z.null()]),
    probability_score: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const ExtractTriggerIn = z
  .object({
    extract_goals: z.boolean().default(false),
    extract_tasks: z.boolean().default(true),
    force: z.boolean().default(false),
  })
  .partial()
  .passthrough();
const DocumentExtractResponse = z
  .object({
    document_id: z.union([z.string(), z.null()]),
    extract_goals: z.union([z.unknown(), z.null()]),
    extract_tasks: z.union([z.unknown(), z.null()]),
    extraction_queued: z.union([z.boolean(), z.null()]),
    has_extracted_text: z.union([z.boolean(), z.null()]),
  })
  .partial()
  .passthrough();
const PasswordChangeIn = z
  .object({
    current_password: z.string().min(1).max(200),
    new_password: z.string().min(10).max(200),
  })
  .passthrough();
const MfaEnrollStartResponse = z
  .object({
    otpauth_url: z.union([z.string(), z.null()]),
    qr_data_url: z.union([z.string(), z.null()]),
    secret: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const MFAConfirmIn = z.object({ code: z.string().min(6).max(8) }).passthrough();
const MFAVerifyIn = z.object({ code: z.string().min(6).max(14) }).passthrough();
const MFADisableIn = z
  .object({ password: z.string().min(1).max(200) })
  .passthrough();
const MfaStatusResponse = z
  .object({
    enrolled_at: z.union([z.string(), z.null()]),
    locked: z.union([z.boolean(), z.null()]),
    mfa_enabled: z.union([z.boolean(), z.null()]),
    recovery_codes_remaining: z.union([z.number(), z.null()]),
  })
  .partial()
  .passthrough();
const IssueIn = z
  .object({ application_id: z.string().min(1).max(120) })
  .passthrough();
const TokenIssueResponse = z
  .object({
    expires_at: z.union([z.string(), z.null()]),
    token: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const CohortPreviewResponse = z
  .object({
    expires_at: z.union([z.string(), z.null()]),
    first_name: z.union([z.string(), z.null()]),
    organisation: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ConsumeIn = z
  .object({
    token: z.string().min(1).max(400),
    mode: z.string().regex(/^(password|google|microsoft)$/),
    password: z.union([z.string(), z.null()]).optional(),
    oauth_code: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const _ActionIn = z
  .object({ note: z.union([z.string(), z.null()]) })
  .partial()
  .passthrough();
const WaitlistJoinRequest = z
  .object({
    email: z.string().email(),
    source_application_id: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const _StatusIn = z
  .object({ status: z.string().regex(/^(new|read|replied|dismissed)$/) })
  .passthrough();
const _RouteIn = z.object({
  route_kind: z
    .string()
    .regex(
      /^(cycle_update|task_create|signal_post|discussion_only|unclassified)$/
    ),
  target_hint: z
    .union([z.object({}).partial().passthrough(), z.null()])
    .optional(),
});
const Body_upload_workbook_api_workbook_upload_post = z
  .object({ file: z.instanceof(File) })
  .passthrough();
const SignalsResponse = z
  .object({ signals: z.union([z.array(z.unknown()), z.null()]) })
  .partial()
  .passthrough();
const SimulateRequest = z
  .object({
    sheet: z.string(),
    column: z.string(),
    distribution: z.string(),
    params: z.record(z.number()),
    iterations: z.number().int().optional().default(5000),
    formula: z.string().optional().default("=x"),
    seed: z.number().int().optional().default(42),
  })
  .passthrough();
const ForecastRequest = z
  .object({
    sheet: z.string(),
    date_column: z.string(),
    value_column: z.string(),
    horizon_periods: z.number().int().optional().default(8),
  })
  .passthrough();
const AnomaliesRequest = z
  .object({
    sheet: z.string(),
    column: z.union([z.string(), z.null()]).optional(),
    z_threshold: z.number().optional().default(3),
    iqr_multiplier: z.number().optional().default(1.5),
  })
  .passthrough();
const AnomaliesResponse = z
  .object({ anomalies: z.union([z.array(z.unknown()), z.null()]) })
  .partial()
  .passthrough();
const Body_upload_workbook_multi_api_workbook_upload_multi_post = z
  .object({
    files: z.array(z.instanceof(File)),
    title: z.union([z.string(), z.null()]).optional(),
    context_id: z.union([z.string(), z.null()]).optional(),
    objective: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const WorkbookAnalysisResponse = z
  .object({
    id: z.union([z.string(), z.null()]),
    context_id: z.union([z.string(), z.null()]),
    account_id: z.union([z.string(), z.null()]),
    status: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const _AnalysisObjectivePatch = z
  .object({ objective: z.string().max(4000) })
  .passthrough();
const _AnalysisNoteIn = z
  .object({ body: z.string().min(0).max(4000) })
  .passthrough();
const PreferencesPutRequest = z
  .object({
    custom_instructions: z.string().max(2000).default(""),
    lenses_enabled: z.array(z.string()),
  })
  .partial()
  .passthrough();

export const schemas = {
  routers__auth__RegisterIn,
  AuthSessionResponse,
  ValidationError,
  HTTPValidationError,
  LoginIn,
  OkResponse,
  AccountWrapResponse,
  DeclareRoleIn,
  SetPasswordIn,
  AccountUpdateIn,
  SetDefaultContextIn,
  ContextObjectIn,
  ContextCreateIn,
  ContextRenameIn,
  InvitationIn,
  DocumentMetaGenerateIn,
  DocumentMetaResponse,
  Body_upload_document_api_contexts__context_id__documents_post,
  committee_id,
  ThreadAncestryResponse,
  _ManualCreateIn,
  DocumentTrustUpdate,
  AsyncJobResponse,
  IntelligenceRegenerateResponse,
  _PromptedEditIn,
  AttachmentCreateBody,
  LineagePatchBody,
  ExportPolicyResponse,
  JournalCommentaryResponse,
  DiffResponse,
  ParagraphsResponse,
  LLMProbeIn,
  TelemetryEventIn,
  BriefingCreateIn,
  MarkReadIn,
  ExportRequestIn,
  ExportStartResponse,
  Body_start_enhance_api_contexts__context_id__work_studio_enhance__kind__post,
  _SaveDraftIn,
  DraftLifecycleResponse,
  ExportRequest,
  EnhanceRequest,
  SetActiveRequest,
  FromSourceRequest,
  ArtefactRedirectResponse,
  CreateArtefactRequest,
  FromDocumentRequest,
  ItemsListResponse,
  DocumentPatchIn,
  IdResponse,
  SaveIn,
  SnapshotResponse,
  ReviseIn,
  LearnResearchIn,
  CommitteeIn,
  SimulateIn,
  routers__comments__CommentIn,
  SignalGenerateIn,
  AskIn,
  LensRunIn,
  CoachStartIn,
  CoachMessageIn,
  PipelineRunIn,
  DryrunIn,
  ShareCreateIn,
  SandboxIntakeIn,
  SandboxEmailCaptureIn,
  TutorialDismissIn,
  SandboxSampleAccept,
  ObjectiveCheckAnswerIn,
  SandboxConvertIn,
  SeededContextIn,
  SandboxV2WelcomeIn,
  SandboxV2PatchIn,
  SandboxV2AddSentenceIn,
  SandboxV2SaveSendIn,
  routers__cycle__QuestionIn,
  QuestionPatch,
  ReporteeIn,
  ChecklistGenerateIn,
  ChecklistEdit,
  DispatchIn,
  routers__cycle__AnswerIn,
  SubmissionIn,
  ReviewerIn,
  ReportComposeIn,
  ReportPatchIn,
  ReviewActionIn,
  PolishIn,
  CommitteesResponse,
  ScheduleResponse,
  CycleScheduleIn,
  CycleActionsResponse,
  _OutputSpecIn,
  _TeamMemberIn,
  _TaskIn,
  _TaskPatch,
  _AgentPrefillIn,
  ObjectiveSourceResponse,
  _ContributionPatchIn,
  TaskHashResponse,
  _ReviewCompleteIn,
  _CirculationSendIn,
  TaskCirculationResponse,
  _CirculationSpan,
  _CirculationCommentIn,
  _ApplyCommentIn,
  TaskContributeResponse,
  Body_contributor_upload_api_tasks_contribute__token__upload_post,
  _ContributorCommentIn,
  _ContributorSubmitIn,
  SubscribeIn,
  ComposeIn,
  PortfolioMetricsOut,
  BoardToWatchOut,
  BoardsToWatchOut,
  LastActionOut,
  ReadinessOut,
  CardDrafts,
  CardReports,
  CardPulse,
  QuestionsDecomposition,
  CardQuestions,
  CardEvents,
  AttentionOut,
  TopSignalItem,
  TopSignalsOut,
  EventIn,
  EventOut,
  EventsList,
  EventPatch,
  ExtractEventsOut,
  ConnectOut,
  StatusOut,
  SyncOut,
  IssueInviteIn,
  CopyOverrideIn,
  FinishIn,
  CheckoutIn,
  NotifyOut,
  OnboardingBriefsResponse,
  UserCreateIn,
  ForceResetIn,
  DeleteAccountRequest,
  ForgotPasswordIn,
  PasswordResetTokenResponse,
  ResetPasswordIn,
  DocumentShareIn,
  DocumentEngagementResponse,
  GoalIn,
  GoalPatch,
  ExtractFromDocIn,
  ChatAuditPanelResponse,
  ChatAuditAggregateResponse,
  SeedPayload,
  CreateSessionIn,
  _UpdateSessionTitleIn,
  SubmitFramingIn,
  SubmitAnswerIn,
  RefuseIn,
  _PostBody,
  Body_restore_one_api_admin_solva_legacy_restore_post,
  ArtefactFromSolvaIn,
  ChatModelsResponse,
  LinkedContextIn,
  ChatCreateIn,
  Body_attach_to_chat_api_chats__chat_id__attach_post,
  ChatAttachmentResponse,
  ChatPatchIn,
  MessageSendIn,
  ChatAuditResponse,
  SignalActionIn,
  state,
  limit,
  routers__pulse__CommentIn,
  routers__pulse__ShareIn,
  ResolveIn,
  AgendaItemIn,
  AgendaIn,
  CycleTeamResponse,
  TeamMemberIn,
  TeamMemberPatch,
  CycleContributionsListResponse,
  ContributionIn,
  CycleContributionResponse,
  ScoreIn,
  FollowUpsDraftIn,
  FollowUpDraftsResponse,
  CycleFollowUpsResponse,
  CycleCreateIn,
  ApplyTemplateIn,
  QuickActionOrderOut,
  CatalogueMemberIn,
  CatalogueMemberPatch,
  SubmitForBoardOut,
  AssignmentCreateIn,
  AcceptOut,
  DeclineIn,
  BriefsCountResponse,
  MeetingCreate,
  MeetingPatch,
  NoteCreate,
  PositionCreate,
  FollowupDraft,
  BriefIn,
  ByContextSummaryResponse,
  AcceptIn,
  RejectIn,
  EnterpriseInterestIn,
  OutlineIn,
  GenerateIn,
  routers__decks__FeedbackIn,
  WalkinIn,
  AdminAuthEventsResponse,
  routers__admin_journal__BackfillRequest,
  CohortApplicationIn,
  routers__admin_shield_backfill__BackfillRequest,
  FirstSessionResetIn,
  RecentDocSeedIn,
  _SeedQuestionIn,
  ActiveContextIn,
  DemoSensitivityIn,
  routers__studio__ShareIn,
  ShareEmailIn,
  BlockCreateIn,
  BlockPatchIn,
  BlockMoveIn,
  ReorderIn,
  ImageUploadIn,
  SubmitReviewIn,
  routers__studio_blocks__ApproveIn,
  SendIn,
  routers__early_access__RegisterIn,
  routers__daily_review__ApproveIn,
  approve_review_item_api_me_review_queue_items__kind___item_id__approve_post_Body,
  reject_review_item_api_me_review_queue_items__kind___item_id__reject_post_Body,
  SolvaCycleEditIn,
  edit_review_item_api_me_review_queue_items__kind___item_id__edit_post_Body,
  StateOnlyResponse,
  IntakeIn,
  DoorIn,
  ArtefactIn,
  CompleteIn,
  GovernancePanelResponse,
  ExportIn,
  StartV2In,
  FrameAuditDecisionIn,
  AttachDocumentIn,
  ForkV2In,
  IntentClassifyIn,
  TurnV2In,
  HandoffCycleIn,
  EarlyAccessApplication,
  ContactSubmission,
  FormPayload,
  _BatchMsgIds,
  ShieldInvokeRequest,
  TrustReceiptV1,
  ShieldInvokeResponse,
  ErrorEnvelope,
  SignalQueryFilter,
  SignalQueryPagination,
  SignalQueryRequest,
  Signal,
  SignalQueryResponse,
  SubscriptionRequest,
  SubscriptionResponse,
  SignalTypeDefinition,
  SignalTypeCatalogue,
  StatusKindResponse,
  ExcoCreateIn,
  ExcoMember,
  ExcoTeamOut,
  ExcoUpdateIn,
  ExcoAddMemberIn,
  CadencePayload,
  CompilationCreate,
  CompilationStartResponse,
  RecentViewIn,
  StatusAssessmentBody,
  StrategicGoalUpdateIn,
  Body_work_studio_enhance_stream_api_contexts__context_id__work_studio_enhance__kind__stream_post,
  routers__feedback__FeedbackIn,
  EarlyAccessIn,
  SpecialAskIn,
  routers__questions__QuestionIn,
  routers__questions__AnswerIn,
  MarkAnsweredIn,
  routers__questions__ShareIn,
  LinkResponseIn,
  NewsItemOut,
  NewsFeedOut,
  ProfileOut,
  ProfilePatchIn,
  TaskInitiativeIn,
  TaskInitiativePatch,
  ExtractTriggerIn,
  DocumentExtractResponse,
  PasswordChangeIn,
  MfaEnrollStartResponse,
  MFAConfirmIn,
  MFAVerifyIn,
  MFADisableIn,
  MfaStatusResponse,
  IssueIn,
  TokenIssueResponse,
  CohortPreviewResponse,
  ConsumeIn,
  _ActionIn,
  WaitlistJoinRequest,
  _StatusIn,
  _RouteIn,
  Body_upload_workbook_api_workbook_upload_post,
  SignalsResponse,
  SimulateRequest,
  ForecastRequest,
  AnomaliesRequest,
  AnomaliesResponse,
  Body_upload_workbook_multi_api_workbook_upload_multi_post,
  WorkbookAnalysisResponse,
  _AnalysisObjectivePatch,
  _AnalysisNoteIn,
  PreferencesPutRequest,
};

export const endpoints = makeApi([
  {
    method: "get",
    path: "/api/",
    alias: "root_api__get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/accounts/:account_id/task-activity/recent",
    alias:
      "list_account_task_activity_api_accounts__account_id__task_activity_recent_get",
    description: `Account-scoped task activity feed.

The existing &#x60;/api/contexts/{cid}/activity/recent&#x60; is context-scoped
— it drops events for tasks created without a &#x60;context_id&#x60;. This
endpoint serves the Task Manager right rail&#x27;s &quot;Recent Task
Activity&quot; card, listing every &#x60;task.*&#x60; event owned by the
account regardless of &#x60;context_id&#x60; association.

Authorization: the requesting account MUST match &#x60;account_id&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(20),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/accounts/me",
    alias: "update_account_api_accounts_me_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AccountUpdateIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/accounts/me/consent-decisions",
    alias: "list_consent_decisions_api_accounts_me_consent_decisions_get",
    requestFormat: "json",
    response: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
  },
  {
    method: "post",
    path: "/api/accounts/me/default-context",
    alias: "set_default_context_api_accounts_me_default_context_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ context_id: z.string() }).passthrough(),
      },
    ],
    response: z.union([AccountWrapResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/audit-invariant-violations",
    alias:
      "list_audit_invariant_violations_api_admin_audit_invariant_violations_get",
    description: `List recent audit-invariant violations. Read-only.

H2.5 follow-up (2026-05-24) — &#x60;&#x60;include_test&#x3D;false&#x60;&#x60; by default
suppresses test-residue rows so the operator&#x27;s view shows only
violations on real user accounts. The pytest suite mocks
&#x60;&#x60;deidentifier.deidentify&#x60;&#x60; to raise &#x60;&#x60;RuntimeError&#x60;&#x60; and triggers
exactly one &#x60;&#x60;shield_failure_at_entry&#x60;&#x60; row per run; with
&#x60;&#x60;include_test&#x3D;false&#x60;&#x60; those rows are hidden from the
real-traffic view.

Response shape::

    {
        &quot;since&quot;: &quot;&lt;iso 8601 cutoff&gt;&quot;,
        &quot;total&quot;: &lt;int&gt;,
        &quot;by_kind&quot;: {&quot;&lt;kind&gt;&quot;: &lt;count&gt;, ...},
        &quot;rows&quot;: [
            {&quot;id&quot;, &quot;kind&quot;, &quot;surface&quot;, &quot;channel&quot;, &quot;account_id&quot;,
             &quot;chat_id&quot;, &quot;ts&quot;, ...},
            ...
        ]
    }`,
    requestFormat: "json",
    parameters: [
      {
        name: "hours",
        type: "Query",
        schema: z.number().int().gte(1).lte(720).optional().default(24),
      },
      {
        name: "kind",
        type: "Query",
        schema: z
          .string()
          .regex(/^$|^[a-z_]+$/)
          .optional()
          .default(""),
      },
      {
        name: "include_test",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(5000).optional().default(500),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/audit-invariant-violations/summary",
    alias:
      "audit_invariant_violations_summary_api_admin_audit_invariant_violations_summary_get",
    description: `Lightweight rollup — no row payloads, just per-kind counts.
Suitable for the Admin Health dashboard tile.`,
    requestFormat: "json",
    parameters: [
      {
        name: "hours",
        type: "Query",
        schema: z.number().int().gte(1).lte(720).optional().default(24),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/auth/events",
    alias: "auth_events_api_admin_auth_events_get",
    description: `Roll up auth events from the last N hours.`,
    requestFormat: "json",
    parameters: [
      {
        name: "hours",
        type: "Query",
        schema: z.number().int().gte(1).lte(720).optional().default(24),
      },
    ],
    response: z.union([AdminAuthEventsResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/auth/revoke-all/:account_id",
    alias: "revoke_all_sessions_api_admin_auth_revoke_all__account_id__post",
    description: `Admin kill-switch — bumps &#x60;accounts.{id}.sessions_revoked_after&#x60;
to now(). Tokens with &#x60;iat &lt; sessions_revoked_after&#x60; are rejected.
This is broader than the per-JTI blocklist but simpler — useful for
&quot;this user reports their account was compromised, kill everything&quot;
scenarios.`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/chat-retention/sweep",
    alias: "admin_chat_retention_sweep_api_admin_chat_retention_sweep_post",
    description: `Manual trigger for the retention sweep — superadmin only. Same
function the daily 03:30 UTC cron in &#x60;server.py&#x60; calls.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/admin/cohort/applications",
    alias: "list_applications_api_admin_cohort_applications_get",
    description: `List cohort applications with optional status filter, newest first.`,
    requestFormat: "json",
    parameters: [
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/cohort/applications/:application_id/approve",
    alias:
      "approve_application_api_admin_cohort_applications__application_id__approve_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ActionIn,
      },
      {
        name: "application_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/cohort/applications/:application_id/decline",
    alias:
      "decline_application_api_admin_cohort_applications__application_id__decline_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ActionIn,
      },
      {
        name: "application_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/cohort/applications/:application_id/hold",
    alias:
      "hold_application_api_admin_cohort_applications__application_id__hold_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ActionIn,
      },
      {
        name: "application_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/cohort/console",
    alias: "cohort_console_table_api_admin_cohort_console_get",
    description: `Cohort console table aggregator.

Returns per-logo rows with highest funnel stage + trial-day +
trial-status + last-signal-at. The R.5.a frontend renders this
as a sortable table with the time-window toggle.

Window options:
  - &#x60;7d&#x60;                   : events within the last 7 days
  - &#x60;28d&#x60;                  : events within the last 28 days
  - &#x60;since_trial_start&#x60; (default): events since the user&#x27;s trial began`,
    requestFormat: "json",
    parameters: [
      {
        name: "cohort_tag",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "window",
        type: "Query",
        schema: z
          .string()
          .regex(/^(7d|28d|since_trial_start)$/)
          .optional()
          .default("since_trial_start"),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(1000).optional().default(200),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/cohort/console/account/:account_id/timeline",
    alias:
      "cohort_account_drilldown_api_admin_cohort_console_account__account_id__timeline_get",
    description: `Per-account activity drill-down for the cohort console.

Returns the most recent &#x60;limit&#x60; feature_events for the account,
most-recent-first, ALONGSIDE the account&#x27;s special-ask row (if any)
so the cohort console can render the special-ask status column
without a second RTT.`,
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(500).optional().default(50),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/cohort/console/special-asks",
    alias:
      "cohort_special_asks_aggregate_api_admin_cohort_console_special_asks_get",
    description: `Per-cohort special-ask aggregate for the cohort console
secondary panel: total_invitees, total_asks, status_counts +
complete_pct. Used to render the &quot;X of N completed special-ask&quot;
progress bar above the table.`,
    requestFormat: "json",
    parameters: [
      {
        name: "cohort_tag",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/cohort/console/stages",
    alias: "cohort_console_stages_api_admin_cohort_console_stages_get",
    description: `Locked list of the 5 funnel stages (in rank order). The
frontend uses this to render the table header without baking
the names into client code.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/admin/cohort/copy",
    alias: "list_copy_overrides_api_admin_cohort_copy_get",
    description: `Return every override row + the slot field schema in one shot.
The editor page consumes this on load.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "put",
    path: "/api/admin/cohort/copy/:slot",
    alias: "put_copy_override_api_admin_cohort_copy__slot__put",
    description: `Persist a slot override. Raises 422 with the locked
&#x60;founder_placeholder_present&#x60; code if any &#x60;[FOUNDER:&#x60; literal
remains in the submitted fields.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CopyOverrideIn,
      },
      {
        name: "slot",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/cohort/funnel",
    alias: "cohort_funnel_api_admin_cohort_funnel_get",
    description: `Aggregate &#x60;db.feature_events&#x60; into a flat funnel.

Returns counts per event_type, scoped to a cohort_tag (if given)
or over all events otherwise. The aggregation runs the full
collection (TTL-trimmed to 90 days); R.5 cohort console will
layer time-window filters on top.

Output shape (locked):
  {
    &quot;cohort_tag&quot;:   &lt;str or null&gt;,
    &quot;events_by_type&quot;: { &quot;&lt;event_type&gt;&quot;: &lt;count&gt;, ... },
    &quot;unique_accounts_by_type&quot;: { &quot;&lt;event_type&gt;&quot;: &lt;count&gt;, ... },
    &quot;total_events&quot;: &lt;int&gt;,
    &quot;as_of&quot;:        &lt;iso8601&gt;,
  }`,
    requestFormat: "json",
    parameters: [
      {
        name: "cohort_tag",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/cohort/invites",
    alias: "issue_invite_api_admin_cohort_invites_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: IssueInviteIn,
      },
      {
        name: "send",
        type: "Query",
        schema: z.number().int().gte(0).lte(1).optional().default(1),
      },
      {
        name: "preview",
        type: "Query",
        schema: z.number().int().gte(0).lte(1).optional().default(0),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/cohort/invites",
    alias: "list_invites_api_admin_cohort_invites_get",
    requestFormat: "json",
    parameters: [
      {
        name: "cohort_tag",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(500).optional().default(100),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/email-provider/health",
    alias: "email_provider_health_api_admin_email_provider_health_get",
    description: `Return a health summary of the configured email provider.
Never raises — errors surface in &#x60;warnings[]&#x60;. Never returns 500.

The endpoint deliberately avoids logging secret values (e.g., the
API key itself). It reports only whether each env var is set.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/admin/extractions",
    alias: "list_extractions_api_admin_extractions_get",
    description: `List the most-recent extraction runs, newest first.

Filters:
  - &#x60;kind&#x60;       ∈ {&quot;goals&quot;, &quot;tasks&quot;} → only that kind
  - &#x60;since&#x60;      ISO datetime         → only created_at &gt;&#x3D; since
  - &#x60;tenant_id&#x60;  context_id           → only runs for that tenant
                                        (Phase W.followup.1)`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(50),
      },
      {
        name: "kind",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "since",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "tenant_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/health/full",
    alias: "admin_health_full_api_admin_health_full_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/admin/inbox/messages",
    alias: "list_inbox_messages_api_admin_inbox_messages_get",
    requestFormat: "json",
    parameters: [
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "skip",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/inbox/messages/:message_id",
    alias: "get_inbox_message_api_admin_inbox_messages__message_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/inbox/messages/:message_id/classify",
    alias:
      "classify_inbox_message_api_admin_inbox_messages__message_id__classify_post",
    description: `Run the inbox-routing classifier against this message. Persists
the envelope on the row at &#x60;classification&#x60; and returns it. Safe
to re-call — overwrites the previous classification.`,
    requestFormat: "json",
    parameters: [
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/inbox/messages/:message_id/dismiss",
    alias:
      "dismiss_inbox_message_api_admin_inbox_messages__message_id__dismiss_post",
    description: `Mark a message as discussion-only without creating a target.
Writes a discussion_only routing-log row + flips the status to
&#x60;dismissed&#x60;. Idempotent — re-calling on a dismissed row returns
&#x60;exists&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/inbox/messages/:message_id/route",
    alias:
      "route_inbox_message_api_admin_inbox_messages__message_id__route_post",
    description: `Manually route a message to a chosen route_kind. Re-uses the
persisted classification&#x27;s &#x60;rationale&#x60; + &#x60;citations&#x60; for the
audit row; overrides &#x60;route_kind&#x60; and &#x60;target_hint&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _RouteIn,
      },
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/inbox/messages/:message_id/routing-log",
    alias:
      "get_inbox_message_routing_log_api_admin_inbox_messages__message_id__routing_log_get",
    description: `Return the routing-log entries for one message. Superadmin
sees every tenant&#x27;s row; the dependency above gates on
superadmin so we always pass &#x60;is_superadmin&#x3D;True&#x60; here.`,
    requestFormat: "json",
    parameters: [
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/inbox/messages/:message_id/status",
    alias:
      "set_inbox_message_status_api_admin_inbox_messages__message_id__status_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({
            status: z.string().regex(/^(new|read|replied|dismissed)$/),
          })
          .passthrough(),
      },
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/inbox/unread-count",
    alias: "get_unread_count_api_admin_inbox_unread_count_get",
    description: `Returns the count of admin_inbox_messages with status&#x3D;&#x27;new&#x27;.

Cached for 30s in-process. Status writes (set_inbox_message_status,
capture_for_admin_inbox) bust the cache so the next poll is fresh.
Hidden from non-super-admin sessions via the dependency.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/admin/journal/backfill",
    alias: "trigger_backfill_api_admin_journal_backfill_post",
    description: `Run the Document Journal commentary backfill in-process.

The actor account id is the calling superadmin — every Synisense
run + audit row generated by this call attributes to them, NOT the
bootstrap admin. That keeps the audit log honest about who pressed
the button.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__admin_journal__BackfillRequest,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/llm/decks/quality",
    alias: "deck_quality_api_admin_llm_decks_quality_get",
    description: `Behaviour-monitoring view: how good are the decks AKKI is producing?

Returns aggregate signals over the window so the team can spot
deteriorating prompt quality or rising regen counts BEFORE budget gets
burned.`,
    requestFormat: "json",
    parameters: [
      {
        name: "days",
        type: "Query",
        schema: z.number().int().gte(1).lte(365).optional().default(30),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/llm/retries_24h",
    alias: "llm_retries_24h_api_admin_llm_retries_24h_get",
    description: `Aggregate db.llm_retry_log over the last 24h, grouped by surface.

Returns:
    {
      window_hours: 24,
      generated_at: ISO,
      total: int,
      by_surface: [{surface, count, sample_reasons: {reason: count}}],
    }`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/admin/llm/spend",
    alias: "llm_spend_api_admin_llm_spend_get",
    description: `Roll up the last N days of deep-tier calls.

Returns:
    {
      window_days: int,
      totals: {calls, est_cost_usd, active_accounts, surfaces_used},
      today_utc: &quot;YYYY-MM-DD&quot;,
      by_surface: [{surface, calls, est_cost_usd, accounts, default_limit}],
      by_account_top: [{account_id, email, name, calls, est_cost_usd, top_surface}],
      by_day: [{day, calls, est_cost_usd}],
      unit_cost_usd: float,
    }`,
    requestFormat: "json",
    parameters: [
      {
        name: "days",
        type: "Query",
        schema: z.number().int().gte(1).lte(365).optional().default(30),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/qa/first-session/reset",
    alias: "reset_first_session_api_admin_qa_first_session_reset_post",
    description: `Reset the first-session state to &#x60;current_step&#x3D;&quot;door&quot;&#x60;.

Idempotent: running it twice produces the same result. Preserves
any prior &#x60;intake&#x60; payload so the user doesn&#x27;t need to retype the
intake answers — the goal is to land them back on the door step
with their intake context intact.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FirstSessionResetIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/qa/seed/question",
    alias: "admin_qa_seed_question_api_admin_qa_seed_question_post",
    description: `Insert a single &#x60;cycle_questions&#x60; row for headless QA flows.

Defaults:
  • assignee_account_id → the caller (the admin) if not provided.
  • context_id          → the admin&#x27;s &#x60;default_context_id&#x60; if not
    provided. Fails 400 if the admin has no default context AND
    no context_id was passed.
  • cycle_id            → the empty string (Q4Y is cycle-scoped
    but the /me/questions endpoint does not require it).
  • asker_role          → &quot;board&quot;.
  • status              → &quot;open&quot;.

Returns the freshly-inserted row stripped of &#x60;_id&#x60;. Idempotent
only at the test-fixture level (each call mints a fresh id).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _SeedQuestionIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/qa/seed/recent-doc",
    alias: "seed_recent_doc_api_admin_qa_seed_recent_doc_post",
    description: `Idempotently seed (context + doc + user_recent_views) so the
Home / Portfolio &quot;Continue&quot; card has a row to render.

Resulting deep_link shape — exact contract that ContextPortfolio
+ WorkStudio honour together:
    /app/work-studio?doc_id&#x3D;{doc_id}&amp;context_id&#x3D;{context_id}`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RecentDocSeedIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/sandbox/kpi",
    alias: "sandbox_kpi_api_admin_sandbox_kpi_get",
    description: `Aggregate KPIs across every context that captured a Q5 objective.

Returns:
    {
      &quot;totals&quot;: {
        &quot;with_objective&quot;: int,
        &quot;answered&quot;: int,
        &quot;yes&quot;: int, &quot;partial&quot;: int, &quot;no&quot;: int, &quot;skipped&quot;: int,
        &quot;answer_rate_pct&quot;: float,        # answered / (with_objective_eligible)
        &quot;delivery_rate_pct&quot;: float,      # yes / answered
      },
      &quot;by_sector&quot;: [
        {&quot;sector&quot;: str, &quot;with_objective&quot;: int, &quot;yes&quot;: int, &quot;partial&quot;: int,
         &quot;no&quot;: int, &quot;skipped&quot;: int, &quot;answered&quot;: int,
         &quot;delivery_rate_pct&quot;: float},
        ...
      ]
    }`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/admin/sandbox/objectives",
    alias: "sandbox_objectives_list_api_admin_sandbox_objectives_get",
    description: `Most-recent-first list of captured objectives, with answer + note.

Optional query params:
  sector — filter by intake sector
  answer — filter by &#x27;yes&#x27; | &#x27;partial&#x27; | &#x27;no&#x27; | &#x27;skipped&#x27; | &#x27;pending&#x27;`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "sector",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "answer",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/shield/backfill",
    alias: "kick_off_backfill_api_admin_shield_backfill_post",
    description: `Kick off an async back-fill. Returns immediately with &#x60;&#x60;job_id&#x60;&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__admin_shield_backfill__BackfillRequest,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/shield/backfill/:job_id/log",
    alias: "job_log_api_admin_shield_backfill__job_id__log_get",
    description: `Per-chat back-fill log for a job.`,
    requestFormat: "json",
    parameters: [
      {
        name: "job_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(5000).optional().default(200),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/shield/backfill/:job_id/status",
    alias: "job_status_api_admin_shield_backfill__job_id__status_get",
    description: `Per-job summary.`,
    requestFormat: "json",
    parameters: [
      {
        name: "job_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/shield/backfill/status",
    alias: "latest_status_api_admin_shield_backfill_status_get",
    description: `Latest back-fill summary (running or most-recent completed).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/admin/signals/action-heatmap",
    alias: "signal_action_heatmap_api_admin_signals_action_heatmap_get",
    description: `Return per-bucket, per-recommendation pick counts plus share totals.

Shape:
    {
      &quot;by_bucket&quot;: [
        {&quot;bucket&quot;: &quot;risk&quot;, &quot;acted&quot;: 12, &quot;shared&quot;: 7,
         &quot;recommendations&quot;: [
            {&quot;label&quot;: &quot;...&quot;, &quot;picks&quot;: 8},
            {&quot;label&quot;: &quot;...&quot;, &quot;picks&quot;: 3},
            {&quot;label&quot;: &quot;...&quot;, &quot;picks&quot;: 1}]},
        ...
      ],
      &quot;totals&quot;: {&quot;acted&quot;: int, &quot;shared&quot;: int, &quot;share_recipients&quot;: int},
      &quot;recent_actions&quot;: [{...}, ... 25],
    }`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/admin/solva/key-usage",
    alias: "get_key_usage_api_admin_solva_key_usage_get",
    description: `Return a sorted list &#x60;[{key, count}]&#x60; of question-key emission
frequencies, descending. Useful for bank-content maintenance:
keys with high emission counts but only one variant (the generic
fallback) are the priority for variant expansion.`,
    requestFormat: "json",
    parameters: [
      {
        name: "since",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/solva/legacy/orphan-count",
    alias: "orphan_count_api_admin_solva_legacy_orphan_count_get",
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/admin/solva/legacy/restore",
    alias: "restore_one_api_admin_solva_legacy_restore_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ session_id: z.string() }).passthrough(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/solva/legacy/soft-archive",
    alias: "soft_archive_orphans_api_admin_solva_legacy_soft_archive_post",
    description: `Soft-delete legacy &#x60;solva_sessions&#x60; rows that have no
&#x60;context_id&#x60; AND are not already archived. Reversible via
&#x60;/legacy/restore?session_id&#x3D;...&#x60;. Adds an &#x60;archived_at&#x60; timestamp
and &#x60;archived_by_admin_id&#x60; for audit.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/admin/solva/variant-coverage",
    alias: "get_variant_coverage_api_admin_solva_variant_coverage_get",
    description: `Companion endpoint: returns &#x60;[{question_key, variants_seen, total_in_bank}]&#x60;
so analytics can spot users approaching cycle-complete on a key.
When called without &#x60;user_id&#x60; returns global per-key coverage
aggregated across all users.`,
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/synisense/billing",
    alias: "billing_estimate_api_admin_synisense_billing_get",
    description: `Compose a per-consumer + per-purpose USD-estimate roll-up.

Numbers are ILLUSTRATIVE — derived from a code-controlled price
table (&#x60;services/synisense/pricing.py&#x60;). No tokens are recorded
on the Shield audit log yet; the table emits a flat-per-call
USD value per (provider, model) pair. The frontend MUST label
this surface &quot;estimated&quot; prominently.

Filters:
  - &#x60;window_days&#x60;: 1..30. Audit rows since &#x60;now − window_days&#x60;.
  - &#x60;context_id&#x60;: optional. If supplied, narrows the audit query
    to consumers whose audit rows carry this context_id field.`,
    requestFormat: "json",
    parameters: [
      {
        name: "window_days",
        type: "Query",
        schema: z.number().int().gte(1).lte(30).optional().default(7),
      },
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/synisense/cron-health",
    alias: "cron_health_api_admin_synisense_cron_health_get",
    description: `Latest scheduler heartbeat row per registered job.

Returns a list ordered by &#x60;last_run_at&#x60; desc:
  [
    {
      &quot;job_id&quot;: &quot;synisense_engine_hourly&quot;,
      &quot;last_run_at&quot;: &quot;2026-05-21T19:00:00.123456+00:00&quot;,
      &quot;status&quot;: &quot;ok&quot; | &quot;failed&quot;,
      &quot;duration_ms&quot;: 1530,
      &quot;summary&quot;: {...rule-family counts...},
      &quot;hour_bucket&quot;: &quot;20260521-19&quot;,
      &quot;replica_id&quot;: &quot;agent-env-...-3fca028d&quot;,
      &quot;error&quot;: null | &quot;RuntimeError: ...&quot;,
    },
    ...
  ]

Empty list when no scheduled work has run yet (e.g. fresh deploy
pre-top-of-hour). The shape stays the same across job types so a
single read covers every cron the platform owns today.`,
    requestFormat: "json",
    response: z.array(z.object({}).partial().passthrough()),
  },
  {
    method: "get",
    path: "/api/admin/synisense/observability",
    alias: "observability_snapshot_api_admin_synisense_observability_get",
    requestFormat: "json",
    parameters: [
      {
        name: "window_days",
        type: "Query",
        schema: z.number().int().gte(1).lte(90).optional().default(7),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/synisense/perf",
    alias: "get_admin_synisense_perf_api_admin_synisense_perf_get",
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/admin/tenants",
    alias: "list_tenants_api_admin_tenants_get",
    description: `List every context in the system with summary enrichments.

Filters:
  - &#x60;q&#x60;     case-insensitive substring match on context name
  - &#x60;type&#x60;  exact match on context.type`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(50),
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "type",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/tenants/:context_id",
    alias: "get_tenant_api_admin_tenants__context_id__get",
    description: `Read-only drill-down for a single tenant. Returns the
sanitized context + enrichments + the list of memberships
(account-id + role only — no payload content).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/tenants/:context_id/extractions",
    alias:
      "get_tenant_extractions_api_admin_tenants__context_id__extractions_get",
    description: `Phase W.followup.1 — Per-tenant extraction-activity panel feed.

Returns the most-recent extraction runs for one tenant, shape-
compatible with the global /api/admin/extractions endpoint so the
frontend can reuse the OutcomeBadge component verbatim.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(50).optional().default(5),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/users",
    alias: "list_users_api_admin_users_get",
    description: `Paginated list of all users with filters + sort.

Filters compose with AND; &#x60;q&#x60; is a case-insensitive substring
match over email + first_name + logo_name.`,
    requestFormat: "json",
    parameters: [
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).lte(10000).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(50),
      },
      {
        name: "sort",
        type: "Query",
        schema: z
          .string()
          .regex(/^(created_at|last_login_at|cohort_tag|email)$/)
          .optional()
          .default("created_at"),
      },
      {
        name: "order",
        type: "Query",
        schema: z
          .string()
          .regex(/^(asc|desc)$/)
          .optional()
          .default("desc"),
      },
      {
        name: "cohort_tag",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "trial_status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "role",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/users",
    alias: "create_user_api_admin_users_post",
    description: `Create a new account manually (NOT via magic-link).

If &#x60;initial_password&#x60; is provided, the account is password-able
from day 1; otherwise the account is passwordless and the user
must hit the magic-link or password-reset flow to set their own.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UserCreateIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/users/:user_id",
    alias: "get_user_api_admin_users__user_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/users/:user_id/force-reset-password",
    alias:
      "force_reset_password_api_admin_users__user_id__force_reset_password_post",
    description: `Admin-triggered password reset. Generates a single-use reset
token (mirrors Phase S &#x60;password_reset.py&#x60; semantics: 256-bit
URL-safe, 1-hour TTL, single-use). Returns the reset URL so the
superadmin can deliver it out-of-band if email is not configured.

Audit row written. Body schema:
    { &quot;send_email&quot;: true }   # default`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ send_email: z.boolean().default(true) })
          .partial()
          .passthrough(),
      },
      {
        name: "user_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/users/:user_id/restore",
    alias: "restore_user_api_admin_users__user_id__restore_post",
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/users/:user_id/suspend",
    alias: "suspend_user_api_admin_users__user_id__suspend_post",
    description: `Flip account status → suspended. All auth-gated requests for
this account will 401 with &#x60;ACCOUNT_SUSPENDED&#x60; from
&#x60;get_current_account&#x60; (see &#x60;backend/core.py&#x60; Phase V block).`,
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/users/:user_id/timeline",
    alias: "user_timeline_api_admin_users__user_id__timeline_get",
    description: `Per-user activity timeline drawn from &#x60;feature_events&#x60;.

**Data-safety contract:** the response strips the &#x60;payload&#x60; field
from every row. The superadmin sees the event TYPE + WHEN — never
the user-typed content of that event. This invariant is locked
by &#x60;test_phase_v_timeline_strips_payload&#x60; and surfaces in the W7
stock-take #4 verdict.`,
    requestFormat: "json",
    parameters: [
      {
        name: "user_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).lte(1000).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(500).optional().default(100),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/admin/users/export.csv",
    alias: "export_users_csv_api_admin_users_export_csv_get",
    description: `CSV download of the filtered user list (no pagination — caps at 10k).

Columns mirror the &#x60;LIST_FIELDS&#x60; allowlist so the CSV never
surfaces sensitive fields (password_hash, magic_link_token, etc.).`,
    requestFormat: "json",
    parameters: [
      {
        name: "cohort_tag",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "trial_status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "role",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/admin/users/process-deletions",
    alias: "process_pending_deletions_api_admin_users_process_deletions_post",
    description: `Hard-delete every account whose &#x60;deletion_scheduled_for&#x60; is in
the past. Returns per-account cascade counts. Superadmin-only.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/auth/declare-role",
    alias: "declare_role_api_auth_declare_role_post",
    description: `Account-level role declaration (NED / Executive / Dual). Refined during M2 onboarding.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DeclareRoleIn,
      },
    ],
    response: z.union([AccountWrapResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/forgot-password",
    alias: "forgot_password_api_auth_forgot_password_post",
    description: `Issue a reset token + email it. ALWAYS returns 200 to avoid
user-enumeration via timing or status-code probes.

The email send fires in the background; the response returns
immediately so the response time is constant whether or not the
account exists.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ email: z.string().email() }).passthrough(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/login",
    alias: "login_api_auth_login_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: LoginIn,
      },
    ],
    response: z.union([AuthSessionResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/logout",
    alias: "logout_api_auth_logout_post",
    description: `Phase J (2026-05-27) — revoke the current access token&#x27;s JTI
server-side BEFORE clearing the cookies. Once written, the JTI is
rejected by &#x60;get_current_account&#x60; even if an attacker still holds
a copy of the raw token. The &#x60;revoked_jtis&#x60; TTL index auto-cleans
rows after the access-token TTL window.`,
    requestFormat: "json",
    response: z.union([OkResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/auth/magic-link/consume",
    alias: "consume_magic_link_api_auth_magic_link_consume_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ConsumeIn,
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/magic-link/issue",
    alias: "issue_magic_link_api_auth_magic_link_issue_post",
    description: `Admin-only. Idempotent per-application — second call invalidates
the prior token. Returns &#x60;{token, expires_at}&#x60; so the caller (the
/approve action) can embed the raw token in the approval email.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ application_id: z.string().min(1).max(120) })
          .passthrough(),
      },
    ],
    response: z.union([TokenIssueResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/magic-link/preview/:token",
    alias: "preview_magic_link_api_auth_magic_link_preview__token__get",
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([CohortPreviewResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/magic/:token",
    alias: "consume_magic_link_api_auth_magic__token__get",
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "json",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/me",
    alias: "me_api_auth_me_get",
    requestFormat: "json",
    response: z.union([AccountWrapResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/auth/mfa/disable",
    alias: "disable_api_auth_mfa_disable_post",
    description: `Disable MFA. Requires the user to re-prove the password (defense
against a stolen but unlocked session).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ password: z.string().min(1).max(200) })
          .passthrough(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/mfa/enroll/confirm",
    alias: "enroll_confirm_api_auth_mfa_enroll_confirm_post",
    description: `Confirm enrolment with a 6-digit TOTP code. Returns the 10
recovery codes ONCE — they will not be retrievable afterwards.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ code: z.string().min(6).max(8) }).passthrough(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/mfa/enroll/start",
    alias: "enroll_start_api_auth_mfa_enroll_start_post",
    description: `Mint a fresh TOTP secret + return the QR data URL. Idempotent —
calling again rotates the pending secret. Confirm must happen
before the secret becomes active.`,
    requestFormat: "json",
    response: z.union([MfaEnrollStartResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/auth/mfa/recovery/regenerate",
    alias: "regenerate_recovery_api_auth_mfa_recovery_regenerate_post",
    description: `Regenerate the 10 recovery codes. Requires a fresh TOTP code to
prove the user has the authenticator app (defense against burning
everyone&#x27;s recovery codes from a compromised session).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ code: z.string().min(6).max(8) }).passthrough(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/mfa/status",
    alias: "status_api_auth_mfa_status_get",
    description: `Lightweight status endpoint for the frontend to render the
Account → Security panel.`,
    requestFormat: "json",
    response: z.union([MfaStatusResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/auth/mfa/verify",
    alias: "verify_api_auth_mfa_verify_post",
    description: `Verify a TOTP code OR a recovery code. Issues fresh auth tokens
on success (so the post-login JWT carries an &#x60;mfa_verified&#x60; claim).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ code: z.string().min(6).max(14) }).passthrough(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/oauth/google/finish",
    alias: "oauth_google_finish_api_auth_oauth_google_finish_post",
    description: `Exchange the Emergent Auth session_id for the user identity, then
find-or-create the account + mint our JWT.

The frontend POSTs &#x60;{session_id}&#x60; AFTER the browser lands at
&#x60;/oauth/callback#session_id&#x3D;&lt;random&gt;&#x60;. The hash fragment never
leaves the browser — the frontend explicitly forwards the value
here.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FinishIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/oauth/google/start",
    alias: "oauth_google_start_api_auth_oauth_google_start_get",
    description: `Return the Emergent Auth base URL + callback path.

Per the playbook the redirect URL MUST be derived on the client
from &#x60;window.location.origin&#x60; (NEVER hardcoded on the backend),
so this endpoint just returns the building blocks and the
frontend assembles the final URL.

REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR
REDIRECT URLS — THIS BREAKS THE AUTH.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/auth/oauth/microsoft/callback",
    alias: "oauth_microsoft_callback_api_auth_oauth_microsoft_callback_get",
    description: `Stage-2: Microsoft redirected back with &#x60;code&#x60; + &#x60;state&#x60;. Exchange
the code, validate the ID token, upsert the account, mint JWT, set
cookies, redirect to the post-login landing.`,
    requestFormat: "json",
    parameters: [
      {
        name: "code",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "state",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "error",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "error_description",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/oauth/microsoft/finish",
    alias: "oauth_microsoft_finish_api_auth_oauth_microsoft_finish_post",
    description: `Legacy POST endpoint — kept for parity with the Google /finish
pattern. Phase U.2 uses the GET /microsoft/callback redirect flow
instead (Microsoft Identity Platform native), so this returns 410
pointing callers at the canonical entry point.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FinishIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/oauth/microsoft/start",
    alias: "oauth_microsoft_start_api_auth_oauth_microsoft_start_get",
    description: `Stage-1: returns the Microsoft authorize URL. Frontend redirects
the browser there; Microsoft bounces back to /microsoft/callback.

Probe mode: pass &#x60;?probe&#x3D;1&#x60; to avoid burning a state token + audit
entry on a configuration check. Returns just &#x60;{configured: true}&#x60;
when the provider is wired.

Phase P5.3 (2026-02) — &#x60;magic_link_token&#x60; is packed into the state
JWT as the &#x60;mlt&#x60; claim. On the /microsoft/callback round-trip the
state-verified &#x60;mlt&#x60; drives the cohort magic-link consume so the
OAuth sign-in counts as a single-use redemption of the same
invite the applicant received in their approval email.`,
    requestFormat: "json",
    parameters: [
      {
        name: "magic_link_token",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/password/change",
    alias: "change_password_api_auth_password_change_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PasswordChangeIn,
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/refresh",
    alias: "refresh_token_api_auth_refresh_post",
    requestFormat: "json",
    response: z.union([OkResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/auth/register",
    alias: "register_api_auth_register_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__auth__RegisterIn,
      },
    ],
    response: z.union([AuthSessionResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/auth/reset-password/:token",
    alias: "get_reset_token_api_auth_reset_password__token__get",
    description: `Validate token. Returns 200 + {email, valid: true} for the
form to display the masked email. 410 if expired, 401 if not
found / tampered, 410 if previously consumed (also not-found case
since token is cleared on successful set).`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([PasswordResetTokenResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/reset-password/:token",
    alias: "consume_reset_token_api_auth_reset_password__token__post",
    description: `Set the new password + clear the token + revoke prior sessions.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ new_password: z.string().min(10).max(200) })
          .passthrough(),
      },
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/auth/set-password",
    alias: "set_password_api_auth_set_password_post",
    description: `Set a password on an authenticated session.

Use case: a user who arrived via cohort magic-link or OAuth (and
therefore has &#x60;password_hash&#x3D;None&#x60; + &#x60;has_set_password&#x3D;False&#x60;)
needs to set a password to drop the first-login gate. This is the
SAME endpoint that the SPA&#x27;s &#x60;SetPasswordGuard&#x60; posts to.

Side effects:
  • &#x60;accounts.password_hash&#x60; &#x3D; bcrypt(body.password).
  • &#x60;accounts.has_set_password&#x60; &#x3D; True (drops the gate on next
    request; legacy rows where the field is missing/null are
    unaffected — only the strict-bool False gates).
  • Refreshes &#x60;last_activity_at&#x60; so the next request doesn&#x27;t
    idle-timeout right after the set (mirrors P5.5 login fix).
  • Audit row &#x60;account.password_set&#x60;.

Idempotent: re-running while already True rotates the password.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ password: z.string().min(10).max(128) })
          .passthrough(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/billing/checkout",
    alias: "create_checkout_api_billing_checkout_post",
    description: `Coming-Soon stub. The frontend should NEVER reach this endpoint
— the BillingTab UI surfaces the Coming-Soon page directly and has
no Stripe CTA — but if anything (an old SPA build, a stale
bookmark, a curl test) DOES hit it, the response is honest:
&#x60;&#x60;{coming_soon: true, message: &lt;verbatim body&gt;}&#x60;&#x60;.

A receipt is written to the audit log so the operator sees that
someone attempted a checkout.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CheckoutIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/billing/me",
    alias: "get_my_plan_api_billing_me_get",
    description: `Current plan for the authenticated user. Always marks
&#x60;&#x60;coming_soon: true&#x60;&#x60; so the frontend renders the Coming-Soon
surface even if the account already has &#x60;&#x60;plan: pro&#x60;&#x60; from an
earlier preview-period grant.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/billing/plans",
    alias: "list_plans_api_billing_plans_get",
    description: `Read-only plan catalog. The &#x60;&#x60;coming_soon&#x60;&#x60; flag is asserted at
the top level so any frontend that lands here gets the honest
response — no fake &quot;Upgrade now&quot; CTA wiring is possible.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/billing/status/:session_id",
    alias: "get_checkout_status_api_billing_status__session_id__get",
    description: `Coming-Soon stub. The session_id is treated opaquely — no
Stripe call is made. Returns &#x60;&#x60;{coming_soon: true}&#x60;&#x60; so legacy
poll loops degrade gracefully to &quot;still coming soon&quot;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/blog/admin/posts/:slug",
    alias: "get_post_admin_api_blog_admin_posts__slug__get",
    description: `Full post fetch for the admin surface — returns drafts + published alike,
body included. Used by the BlogAdmin &#x27;Copy for Medium&#x27; action.`,
    requestFormat: "json",
    parameters: [
      {
        name: "slug",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/blog/compose",
    alias: "compose_api_blog_compose_post",
    description: `LLM-driven composition for the next Exco360 article. Persists as a
draft. Returns the full draft for review.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ComposeIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/blog/cron/weekly",
    alias: "cron_weekly_api_blog_cron_weekly_post",
    description: `Compose the next Exco360 issue as a DRAFT. Idempotent within a single
ISO week — if a draft already exists for this week&#x27;s topic, returns it
instead of re-composing. Gated by AKKI_CRON_SECRET env var so only the
scheduled-job runner can hit it.`,
    requestFormat: "json",
    parameters: [
      {
        name: "X-Cron-Secret",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/blog/posts",
    alias: "list_posts_api_blog_posts_get",
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(20),
      },
      {
        name: "include_drafts",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/blog/posts/:slug",
    alias: "get_post_api_blog_posts__slug__get",
    requestFormat: "json",
    parameters: [
      {
        name: "slug",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/blog/posts/:slug",
    alias: "delete_post_api_blog_posts__slug__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "slug",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/blog/posts/:slug/publish",
    alias: "publish_post_api_blog_posts__slug__publish_post",
    description: `Publish + fan-out to subscribers. Returns the post enriched with a
&#x60;newsletter&#x60; summary so the admin sees how many were notified.`,
    requestFormat: "json",
    parameters: [
      {
        name: "slug",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/blog/rss",
    alias: "rss_feed_api_blog_rss_get",
    description: `Atom feed of the most recent 30 published posts.`,
    requestFormat: "json",
    response: z.void(),
  },
  {
    method: "post",
    path: "/api/blog/seed/launch-10",
    alias: "seed_launch_articles_api_blog_seed_launch_10_post",
    description: `One-shot seed: composes 10 launch articles across opportunity, risk,
compliance, adoption-management, and growth-as-an-executive (2 each)
using the persona prompt. Returns immediately with how many were
queued; the LLM calls run sequentially and persist as drafts.

Idempotent: skips topics that already have a draft on this server.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/blog/subscribe",
    alias: "subscribe_api_blog_subscribe_post",
    description: `Capture an email subscription for the Exco360 list. Idempotent — same
email re-subscribes silently (no duplicate, no error).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SubscribeIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/blog/subscribers",
    alias: "list_subscribers_api_blog_subscribers_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/chat/models",
    alias: "list_models_api_chat_models_get",
    requestFormat: "json",
    response: z.union([ChatModelsResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/chats",
    alias: "create_chat_api_chats_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ChatCreateIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats",
    alias: "list_chats_api_chats_get",
    description: `List the caller&#x27;s active conversations.

Workstream A.2 (2026-05-10) — &#x60;X-Active-Context&#x60; is now REQUIRED.
The pre-Phase-B legacy escape hatch (no header → account-wide list)
has been retired so non-SPA callers can&#x27;t bypass per-context
isolation. Tests that don&#x27;t send the header will need to be updated.

Workstream B.5 — &#x60;?include_archived&#x3D;true&#x60; switches the filter to
show archived chats too (newest-first by &#x60;last_message_at&#x60;). The
sidebar archive view uses this.`,
    requestFormat: "json",
    parameters: [
      {
        name: "include_archived",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id",
    alias: "get_chat_api_chats__chat_id__get",
    description: `Wave 5 (2026-02 fork-resume) — General RAG default. The chat
MAY be a general chat (&#x60;context_id: None&#x60;); in that case, no
X-Active-Context header is required. Otherwise (context-scoped
chat), the header MUST match the chat&#x27;s context_id.

Workstream B.5 — &#x60;?include_archived&#x3D;true&#x60; lets the archive view
open an archived chat for restore preview.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "include_archived",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/chats/:chat_id",
    alias: "patch_chat_api_chats__chat_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ChatPatchIn,
      },
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/chats/:chat_id",
    alias: "soft_delete_chat_api_chats__chat_id__delete",
    description: `Phase B.1 — soft-delete with a 30-day retention clock.

Sets &#x60;&#x60;status&#x3D;&#x27;archived&#x27;&#x60;&#x60; (legacy field, kept for backward compat
with the existing UI listing filter) AND &#x60;&#x60;deleted_at&#x60;&#x60; (the new
retention clock the daily sweep keys off). The user-visible action
name in the audit log is still &#x60;&#x60;chat.archived&#x60;&#x60; so existing
audit-trail dashboards keep working; the hard-delete sweep writes
its own &#x60;&#x60;chat.hard_deleted&#x60;&#x60; row with the retention metadata.

Workstream A.2 (2026-05-10) — X-Active-Context REQUIRED. The chat
must belong to the active context (so cross-context deletes via
raw chat_id are rejected).

Workstream B.5 (2026-05-10) — when &#x60;?hard&#x3D;true&#x60; is passed and the
chat is already archived, hard-delete immediately. The audit chain
is preserved (chat_audit_log rows stay; only the chat doc + its
chat_messages are removed). The audit row is &#x60;chat.hard_deleted&#x60;
with &#x60;via&#x3D;&#x27;manual&#x27;&#x60; so the daily-sweep telemetry separates manual
purges from time-based ones.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "hard",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/chats/:chat_id/attach",
    alias: "attach_to_chat_api_chats__chat_id__attach_post",
    description: `Ingest a file as a chat attachment. The file is saved as a
document in the chat&#x27;s bound context AND its de-identified text
is made available to the next LLM turn via
&#x60;attached_document_ids&#x60; on the message-send body.

Body: multipart/form-data with one &#x60;file&#x60; part.
Header: &#x60;X-Active-Context&#x60; is consulted defensively — when set,
        the chat&#x27;s &#x60;context_id&#x60; MUST equal it (per-tab role
        binding from Phase A). Mismatch → 403.`,
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ file: z.instanceof(File) }).passthrough(),
      },
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ChatAttachmentResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/audit",
    alias: "get_chat_audit_api_chats__chat_id__audit_get",
    description: `Return the chained audit trail for this chat. Read-only; auditors
can verify the chain by recomputing each row&#x27;s hash from the canonical
JSON of (prev_hash, id, at, account_id, chat_id, action, payload,
ip, ua_sha) and confirming &#x60;row_hash&#x60; matches.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ChatAuditResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/audit-panel",
    alias: "get_audit_panel_api_chats__chat_id__audit_panel_get",
    description: `Returns the natural-language audit panel data for one assistant
message. Resolves the right Shield audit row by indexing into the
chat session&#x27;s &#x60;synisense_audit_ids&#x60; array using the assistant
message&#x27;s position in &#x60;chat_messages&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "message_id",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.union([ChatAuditPanelResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/audit-panel/aggregate",
    alias:
      "get_audit_panel_aggregate_api_chats__chat_id__audit_panel_aggregate_get",
    description: `Rolling aggregate across every Shield invoke this chat made.
Powers the pinned strip at the top of the chat surface.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ChatAuditAggregateResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/audit/export.zip",
    alias: "export_chat_audit_pack_api_chats__chat_id__audit_export_zip_get",
    description: `Bank-grade audit pack — a single zip an auditor can ingest:

    manifest.txt        — schema + verification recipe
    chat.json           — chat metadata
    messages.json       — every message&#x27;s content_sha256, role,
                          created_at, shielding decision (NO raw content)
    audit_chain.json    — full hash-chained log
    verify.py           — pure-stdlib script that recomputes the chain
                          against audit_chain.json and reports any
                          broken links.

Raw message content is NEVER included; only its SHA256 fingerprint.
Auditors prove existence + ordering + integrity without exposure.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/chats/:chat_id/governance/solva-escalation-clicked",
    alias:
      "record_solva_escalation_click_api_chats__chat_id__governance_solva_escalation_clicked_post",
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/chats/:chat_id/messages",
    alias: "send_message_api_chats__chat_id__messages_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MessageSendIn,
      },
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/messages/:msg_id/synisense-runs",
    alias:
      "message_synisense_runs_api_chats__chat_id__messages__msg_id__synisense_runs_get",
    description: `Phase J.2 — per-message Synisense metrics. Returns counts +
layer breakdown scoped to a SINGLE chat message. Used by the chat
UI to render an inline redaction badge per assistant message.

Filter is on (chat_id, message_id) which is reliable once
&#x60;_record_synisense_audit_evidence&#x60; and &#x60;shield_payload_async&#x60;
started threading these fields (Phase J.2).`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "msg_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/chats/:chat_id/messages/stream",
    alias: "stream_message_api_chats__chat_id__messages_stream_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MessageSendIn,
      },
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/chats/:chat_id/messages/synisense-runs/batch",
    alias:
      "messages_synisense_runs_batch_api_chats__chat_id__messages_synisense_runs_batch_post",
    description: `CHAT sprint (2026-05-12) — batched per-message Synisense metrics.

Replaces the N+1 pattern (one HTTP call per assistant message) with
a single aggregation pipeline grouped by &#x60;message_id&#x60;. The UI calls
this once after the message list paints.

Response shape:
  {&quot;items&quot;: { &quot;&lt;msg_id&gt;&quot;: {identifiers_redacted, model_calls,
                           layer_breakdown}, ... }}
Messages with zero shield activity simply aren&#x27;t present in the
map — the UI treats absent as zero.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _BatchMsgIds,
      },
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/chats/:chat_id/permanent",
    alias: "permanent_delete_chat_api_chats__chat_id__permanent_delete",
    description: `Hard delete a chat. Requires &#x60;{&quot;confirm&quot;: true}&#x60; in the body to
guard against accidental cascade.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/privacy-report.pdf",
    alias: "chat_privacy_report_pdf_api_chats__chat_id__privacy_report_pdf_get",
    description: `Generate a privacy-report PDF for one chat. Streams as
&#x60;application/pdf&#x60;. Strict scoping: the chat must belong to the
requesting account.

For each Shield audit row, fetches the matching &#x60;synisense_trust_
receipts&#x60; row WITHOUT excluding &#x60;signature&#x60; / &#x60;payload_hash&#x60; —
those are the fields a tenant uses to self-verify the HMAC chain.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/chats/:chat_id/restore",
    alias: "restore_chat_api_chats__chat_id__restore_post",
    description: `Workstream B.5 — restore a soft-deleted chat to active status.

Clears &#x60;deleted_at&#x60; and &#x60;archived_at&#x60;, sets &#x60;status&#x3D;&#x27;active&#x27;&#x60;. The
30-day retention clock is reset (the chat is back in the active
list). One audit row &#x60;chat.restored&#x60; is appended.

Workstream A.2 — X-Active-Context REQUIRED.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/:chat_id/synisense-metrics",
    alias: "chat_synisense_metrics_api_chats__chat_id__synisense_metrics_get",
    description: `Per-conversation metrics. Scope: chat_id&#x27;s account_id +
chat surfaces + ts &gt;&#x3D; chat.created_at.

QA-2026-05-20 Phase-C-symptom-2 fix: &#x60;chats.created_at&#x60; is stored
as an ISO STRING (historical inconsistency — most other timestamp
columns are BSON Date) while &#x60;synisense_runs.ts&#x60; is a BSON Date
(datetime). MongoDB&#x27;s &#x60;$gte&#x60; comparison between a string and a
datetime falls into different BSON type brackets and silently
matches nothing. That is the literal cause of the 20-May QA
screenshot showing IDENTIFIERS REDACTED &#x3D; 0 / MODEL CALLS &#x3D; 0 /
&quot;Synisense Shield is on standby&quot; topline on a chat that DID run
through Shield (verified — the audit-panel?message_id endpoint
on the same chat returned identifiers_shielded &gt; 0).

Coerce the stored value to a timezone-aware datetime before the
comparison so the type brackets align.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/archived",
    alias: "list_archived_chats_api_chats_archived_get",
    description: `User&#x27;s archived chats, most recently archived first.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(50),
      },
      {
        name: "skip",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/chats/search",
    alias: "search_chats_api_chats_search_get",
    description: `Search chats by substring in title OR turn content, scoped to
the caller&#x27;s active context.

Workstream A.2 (2026-05-10) — &#x60;X-Active-Context&#x60; REQUIRED. No more
account-wide escape hatch.

Returns:
    {
      &quot;items&quot;: [
        {
          &quot;chat&quot;: &lt;chat row&gt;,
          &quot;match_in&quot;: &quot;title&quot; | &quot;message&quot;,
          &quot;snippet&quot;: &lt;~120 chars surrounding the hit&gt;,
          &quot;matched_message_id&quot;: &lt;str | None&gt;,
        },
        ...
      ],
      &quot;count&quot;: N,
    }`,
    requestFormat: "json",
    parameters: [
      {
        name: "q",
        type: "Query",
        schema: z.string().min(2).max(200),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(50),
      },
      {
        name: "include_archived",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/cohort/applications",
    alias: "submit_application_api_cohort_applications_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CohortApplicationIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/cohort/email-events/sendgrid",
    alias: "sendgrid_event_webhook_api_cohort_email_events_sendgrid_post",
    description: `Receive SendGrid Event Webhook batches. Body is a JSON array
of event objects: [{email, event, timestamp, sg_message_id, ...}].`,
    requestFormat: "json",
    parameters: [
      {
        name: "x-twilio-email-event-webhook-signature",
        type: "Header",
        schema: committee_id,
      },
      {
        name: "x-twilio-email-event-webhook-timestamp",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/cohort/waitlist",
    alias: "waitlist_join_api_cohort_waitlist_post",
    description: `Public — accept a single email into the waitlist.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: WaitlistJoinRequest,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts",
    alias: "create_context_api_contexts_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContextCreateIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:cid/documents/:doc_id/extract-events",
    alias:
      "extract_events_from_document_api_contexts__cid__documents__doc_id__extract_events_post",
    description: `Phase I.4.b — LLM-extract time-bound events from a document.

Returns the cleaned + filtered extractions and persists each as
&#x60;status&#x3D;&quot;draft&quot;&#x60;. User reviews / confirms / rejects from the
Events page Extracted tab.

Idempotent on &#x60;(context_id, doc_id, source&#x3D;&quot;doc_extraction&quot;,
status&#x3D;&quot;draft&quot;)&#x60; — re-running on the same doc replaces prior
drafts; confirmed + rejected events are untouched.

Callable on ANY document the caller has access to; the
background auto-trigger on document upload is gated by an
allowlist of &#x60;doc_type&#x60; values (see &#x60;_AUTO_EXTRACT_DOC_TYPES&#x60;).`,
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExtractEventsOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:cid/events",
    alias: "create_event_api_contexts__cid__events_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EventIn,
      },
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: EventOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:cid/events",
    alias: "list_events_api_contexts__cid__events_get",
    description: `List events for a context.

&#x60;status&#x60; filter (I.4.b):
  • None (default) → all non-deleted events (mirrors I.4.a behavior)
  • &quot;draft&quot;        → only extracted drafts awaiting user confirm/reject
  • &quot;confirmed&quot;    → confirmed events ONLY (absence-default included
    via &#x60;$ne:&quot;draft&quot;&#x60;; manual events without a status count)`,
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "upcoming",
        type: "Query",
        schema: z.boolean().optional().default(true),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(50),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: EventsList,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:cid/events/:event_id",
    alias: "get_event_api_contexts__cid__events__event_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "event_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: EventOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:cid/events/:event_id",
    alias: "update_event_api_contexts__cid__events__event_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EventPatch,
      },
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "event_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: EventOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:cid/events/:event_id",
    alias: "delete_event_api_contexts__cid__events__event_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "event_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:cid/events/sync-calendar",
    alias: "sync_calendar_api_contexts__cid__events_sync_calendar_post",
    description: `Pull events from the connected calendar (Google this phase) and
persist them in &#x60;db.events&#x60; as &#x60;source&#x3D;&quot;calendar_sync&quot;&#x60;. Idempotent:
re-syncing replaces prior &#x60;calendar_sync&#x60; rows for matching
&#x60;source_ref&#x60;. Manual + doc_extraction events are NEVER touched.

Window: now → now+90d (wider than Card 5&#x27;s 14d so the Events page
Past/All tabs also see history).`,
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "provider",
        type: "Query",
        schema: z.string().optional().default("google"),
      },
    ],
    response: SyncOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:cid/oauth/calendar/status",
    alias: "calendar_status_api_contexts__cid__oauth_calendar_status_get",
    description: `Aggregated status for the Events surface&#x27;s connection banner.
Currently only Google but the shape is provider-agnostic so a future
Microsoft Graph leg lands without surface changes.`,
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: StatusOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:cid/oauth/google/disconnect",
    alias:
      "oauth_google_disconnect_api_contexts__cid__oauth_google_disconnect_post",
    description: `Soft-delete the credentials row + revoke the token at Google.`,
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:cid/synisense-metrics",
    alias: "context_synisense_metrics_api_contexts__cid__synisense_metrics_get",
    description: `Aggregate metrics for a tenant, windowed by ts. Used in the
Trust Panel rollup row.`,
    requestFormat: "json",
    parameters: [
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "window",
        type: "Query",
        schema: z
          .string()
          .regex(/^(today|7d|30d)$/)
          .optional()
          .default("today"),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id",
    alias: "get_context_api_contexts__context_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id",
    alias: "rename_context_api_contexts__context_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ name: z.string().min(1).max(120) }).passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id",
    alias: "archive_context_api_contexts__context_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/:artefact_type/:artefact_id/comments",
    alias:
      "list_comments_api_contexts__context_id___artefact_type___artefact_id__comments_get",
    requestFormat: "json",
    parameters: [
      {
        name: "artefact_type",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/:artefact_type/:artefact_id/comments",
    alias:
      "create_comment_api_contexts__context_id___artefact_type___artefact_id__comments_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__comments__CommentIn,
      },
      {
        name: "artefact_type",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/activity/recent",
    alias: "list_recent_activity_api_contexts__context_id__activity_recent_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(25),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/agenda-evolution",
    alias:
      "get_agenda_evolution_api_contexts__context_id__agenda_evolution_get",
    description: `Returns:
{
  &quot;last_meeting&quot;: {
    &quot;cycle_name&quot;: &quot;Q1 2026 board pack&quot;,
    &quot;happened_at&quot;: &quot;2026-04-12T...&quot;,
    &quot;report_title&quot;: &quot;Q1 2026 management report&quot;,
    &quot;agenda&quot;: [&quot;Provisioning&quot;, &quot;Capital&quot;, &quot;Cyber&quot;]   # best-effort
  } | None,
  &quot;since_then&quot;: [
    {&quot;actor&quot;: &quot;Ruth Kamau&quot;, &quot;verb&quot;: &quot;answered&quot;, &quot;object&quot;: &quot;5 of 6 audit questions&quot;,
     &quot;at&quot;: &quot;2026-04-25T...&quot;, &quot;tone&quot;: &quot;positive&quot;},
    ...
  ],
  &quot;next_up&quot;: &quot;Q2 2026 audit pack — 1 outstanding response&quot;
}`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/ask",
    alias: "ask_api_contexts__context_id__ask_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ question: z.string().min(1).max(4000) })
          .passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/ask",
    alias: "list_ask_history_api_contexts__context_id__ask_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/audit-log",
    alias: "get_audit_log_api_contexts__context_id__audit_log_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/boardpacks",
    alias: "list_boardpacks_api_contexts__context_id__boardpacks_get",
    description: `List boardpacks for the active context, optionally filtered by
&#x60;cycle_id&#x60;. Default sort: most recent first.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/boardpacks/:bpid",
    alias: "get_boardpack_api_contexts__context_id__boardpacks__bpid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "bpid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/boardpacks/:bpid/regenerate-commentary",
    alias:
      "regenerate_boardpack_commentary_api_contexts__context_id__boardpacks__bpid__regenerate_commentary_post",
    description: `Synthesise FT-voice commentary across the documents in the
boardpack, run it through Synisense (surface&#x3D;briefing for parity
with existing Daily Review approval queue), persist the result.

Real LLM call — uses the universal LLM gateway. ~600-1200
word target. Cached on the row; subsequent reads return cached
output unless this endpoint is called again or &#x60;?refresh&#x3D;true&#x60; is
passed to GET (the refresh flag is currently advisory; explicit
POST is the supported path).`,
    requestFormat: "json",
    parameters: [
      {
        name: "bpid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/briefings",
    alias: "create_briefing_api_contexts__context_id__briefings_post",
    description: `Chunk 2 (DJ-R03) — async pattern.

Returns **202 + &#x60;job_id&#x60;** immediately. The LLM-heavy compose
work runs as a &#x60;BackgroundTasks&#x60; worker; the frontend polls
&#x60;GET /api/jobs/{job_id}&#x60; and consumes &#x60;result&#x60; (the serialised
briefing row) when status → &#x60;completed&#x60;. Sync legacy callers
can still hit &#x60;_create_briefing_worker(...)&#x60; directly.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BriefingCreateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefings",
    alias: "list_briefings_api_contexts__context_id__briefings_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefings/:briefing_id",
    alias: "get_briefing_api_contexts__context_id__briefings__briefing_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "briefing_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/briefings/:briefing_id",
    alias:
      "archive_briefing_api_contexts__context_id__briefings__briefing_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "briefing_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefings/:briefing_id/export",
    alias:
      "export_briefing_api_contexts__context_id__briefings__briefing_id__export_get",
    requestFormat: "json",
    parameters: [
      {
        name: "briefing_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "fmt",
        type: "Query",
        schema: z.string().optional().default("pdf"),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/briefings/:briefing_id/mark-read",
    alias:
      "mark_briefing_read_api_contexts__context_id__briefings__briefing_id__mark_read_post",
    description: `Stamp this briefing as read for the current account. Idempotent —
upserts on (briefing_id, account_id) so repeated calls just refresh
the timestamp + via channel.

&quot;Read&quot; is now a real signal:
  • via&#x3D;&#x27;manual&#x27; — user clicked &quot;Mark as read&quot;
  • via&#x3D;&#x27;scroll&#x27; — frontend reached ≥70% scroll depth
Either is enough to flip the rail badge.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({
            via: z
              .string()
              .regex(/^(manual|scroll)$/)
              .default("manual"),
          })
          .partial()
          .passthrough(),
      },
      {
        name: "briefing_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/briefings/:briefing_id/speaking-notes",
    alias:
      "draft_speaking_notes_api_contexts__context_id__briefings__briefing_id__speaking_notes_post",
    description: `Generate 3 speaker-note bullets per briefing item.

What you would actually *say* when each slide is on screen. Persists onto
briefing.items[i].speaking_notes so subsequent board-deck exports render
them under the slide. Re-calling overwrites the notes for every item.`,
    requestFormat: "json",
    parameters: [
      {
        name: "briefing_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefings/aggregates",
    alias:
      "list_brief_aggregates_api_contexts__context_id__briefings_aggregates_get",
    description: `Phase C.1 — aggregate listing for the Workspace rewire.

Registered BEFORE the &#x60;/{briefing_id}&#x60; route below so FastAPI&#x27;s
in-order matcher resolves &#x60;/aggregates&#x60; to this handler instead of
treating &quot;aggregates&quot; as a briefing id.

Cycle Manager Feel pass (2026-02) added:
  • &#x60;q&#x60; — case-insensitive substring match on the row&#x27;s name.
  • &#x60;status&#x60; ∈ {all, draft, in_progress, compiled, shipped} — filter
    by the derived artefact lifecycle status. &#x60;all&#x60; is a no-op.
  • &#x60;sort&#x60; ∈ {recent, oldest, alpha, type} — recent / oldest sorts
    by meeting_date desc / asc; alpha by name; type by kind then date.
  • &#x60;page&#x60; / &#x60;page_size&#x60; — paginate the post-filter result.
The response now includes &#x60;total&#x60; + &#x60;page&#x60; + &#x60;page_size&#x60; + &#x60;total_pages&#x60;
+ &#x60;counts_by_status&#x60; for ListingShell consumption.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "sort",
        type: "Query",
        schema: z
          .string()
          .regex(/^(recent|oldest|alpha|type)$/)
          .optional()
          .default("recent"),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).lte(1000).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(5),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefings/aggregates/:aggregate_id",
    alias:
      "get_brief_aggregate_api_contexts__context_id__briefings_aggregates__aggregate_id__get",
    description: `Phase C.1 — aggregate detail for the Workspace drawer.

Chunk 6 (2026-05-13, WS-R01 / WS-R17): added explicit dispatch for
&#x60;briefing&#x60;, &#x60;deck&#x60;, and &#x60;report&#x60; kinds. Pre-fix the fall-through
sent every non-cycle kind to &#x60;_detail_cycle_committee_pack&#x60; which
required a &#x60;&lt;committee_id&gt;::&lt;quarter&gt;&#x60; internal id and raised
&#x60;Bad aggregate id.&#x60; 400 for any plain uuid. Net effect: clicking
any deck / report / brief row in Work Studio returned 400. The
drawer also lacked an Open-in-composer CTA; the new handlers
surface &#x60;composer_url&#x60; so the BriefDrawer can wire a working
primary action.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "aggregate_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/briefs",
    alias: "create_brief_api_contexts__context_id__briefs_post",
    description: `On-demand brief. Generates editorial copy via LLM, persists to
&#x60;briefs&#x60; collection, returns the saved doc.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BriefIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefs",
    alias: "list_briefs_api_contexts__context_id__briefs_get",
    description: `Most-recent-first list for the saved-brief history rail.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "kind",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/briefs/:brief_id",
    alias: "get_brief_api_contexts__context_id__briefs__brief_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/briefs/:brief_id",
    alias: "delete_brief_api_contexts__context_id__briefs__brief_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/checklists",
    alias: "list_checklists_api_contexts__context_id__checklists_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/checklists/:cid",
    alias: "edit_checklist_api_contexts__context_id__checklists__cid__patch",
    description: `Executive edits questions / adds a personal note before approving.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ChecklistEdit,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/checklists/dispatch",
    alias:
      "dispatch_checklists_api_contexts__context_id__checklists_dispatch_post",
    description: `Executive approves and dispatches a batch of checklists. AKKI sends
each via Resend (with mailto fallback if not configured), updates the
Question Bank&#x27;s &#x60;times_asked&#x60; + &#x60;last_asked_at&#x60;, and returns send results.

Sender: &#x27;AKKI for &lt;Executive Name&gt; &lt;noreply@akki.ai&gt;&#x27;, reply-to is the
executive&#x27;s real email so reportee replies route back to her naturally.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DispatchIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/checklists/generate",
    alias:
      "generate_checklists_api_contexts__context_id__checklists_generate_post",
    description: `Compose a per-reportee checklist tailored from the open question bank.
Returns drafts in &#x60;pending_approval&#x60; state — nothing is sent yet. The
executive reviews/edits/approves them via /dispatch below.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ChecklistGenerateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/comments/:comment_id",
    alias:
      "delete_comment_api_contexts__context_id__comments__comment_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "comment_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/committees",
    alias: "list_committees_api_contexts__context_id__committees_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/committees",
    alias: "add_committee_api_contexts__context_id__committees_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CommitteeIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/committees/:committee_id",
    alias:
      "update_committee_api_contexts__context_id__committees__committee_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CommitteeIn,
      },
      {
        name: "committee_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/committees/:committee_id",
    alias:
      "delete_committee_api_contexts__context_id__committees__committee_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "committee_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/context-object",
    alias: "get_context_object_api_contexts__context_id__context_object_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/context-object",
    alias:
      "upsert_context_object_api_contexts__context_id__context_object_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContextObjectIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/cycle-assignments/:assignment_id",
    alias:
      "cancel_assignment_api_contexts__context_id__cycle_assignments__assignment_id__delete",
    description: `Cancel a still-pending assignment. Creator-only, only before
the NED has accepted.

The brief&#x27;s submitter can cancel any pending assignment on their
own brief. An admin / chief_of_staff in the same context can cancel
too. Workspace owner can always cancel.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "assignment_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/actions",
    alias: "cycle_manager_actions_api_contexts__context_id__cycle_actions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([CycleActionsResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/agenda",
    alias: "get_agenda_api_contexts__context_id__cycle_agenda_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/agenda",
    alias: "upsert_agenda_api_contexts__context_id__cycle_agenda_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AgendaIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/committees",
    alias:
      "list_cycle_committees_api_contexts__context_id__cycle_committees_get",
    description: `Surface the committees configured on this context so the Cycle UI can
filter Question Bank, Reportees, Checklists, and Reports by committee.
Wraps the existing committees collection — duplicating to a /cycle path
avoids a circular import with the committees router.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([CommitteesResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/contributions",
    alias:
      "list_contributions_api_contexts__context_id__cycle_contributions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([CycleContributionsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/contributions",
    alias:
      "add_contribution_api_contexts__context_id__cycle_contributions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContributionIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([CycleContributionResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/contributions/:contribution_id/score",
    alias:
      "score_contribution_api_contexts__context_id__cycle_contributions__contribution_id__score_post",
    description: `Score a contribution on relevance / fullness / readiness.
If the request omits any dimension, the heuristic backstop fills it
in. (LLM-driven scoring is the future-canonical path; for D1 we
accept manual + heuristic so tests stay deterministic.)

QA-2026-05-16-020 (2026-05-18, Chunk-9): when the contribution
carries a &#x60;source_doc_id&#x60;, the scorer concatenates the document&#x27;s
&#x60;extracted_text&#x60; after the pasted body_text — single combined
string, single rubric pass — so an attachment alone OR pasted
text alone OR both score against the same combined-content
fullness/relevance/readiness rubric.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ScoreIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "contribution_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([CycleContributionResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/draft-compilation",
    alias:
      "draft_compilation_api_contexts__context_id__cycle_draft_compilation_post",
    description: `Chunk 2 (CM-R04) — async pattern.

Returns **202 + &#x60;job_id&#x60;** immediately. The two-pass LLM compile
(drafter Sonnet 4.5 → validator Gemini 2.5 Flash) + brief
persistence + DOCX render runs as a fire-and-forget asyncio task.
Frontend polls &#x60;GET /api/jobs/{job_id}&#x60; until terminal and then
consumes &#x60;result&#x60; (which carries &#x60;redirect_url&#x60;, &#x60;export_id&#x60;,
&#x60;byte_len&#x60;, etc. — the legacy sync response shape preserved).

The pre-flight checks (agenda exists + contributions exist) run
synchronously so the user sees those 400s instantly without a
polling round-trip.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([AsyncJobResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/draft-compilation/stream",
    alias:
      "task_manager_compile_stream_api_contexts__context_id__cycle_draft_compilation_stream_post",
    description: `SSE-wrap of the Task Manager (cycle) compile flow.

Phases (7): Reading the cycle responses → Checking the grounding
contract → Drafting the outline → Composing → Rendering the
compilation → Validating → Almost there.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/follow-ups",
    alias: "list_followups_api_contexts__context_id__cycle_follow_ups_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([CycleFollowUpsResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/follow-ups/:followup_id/approve",
    alias:
      "approve_followup_api_contexts__context_id__cycle_follow_ups__followup_id__approve_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "followup_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/follow-ups/:followup_id/send",
    alias:
      "send_followup_api_contexts__context_id__cycle_follow_ups__followup_id__send_post",
    description: `Phase D.2 — send an approved follow-up via Resend using the
Cycle Manager outbound posture:

  From      :  &#x27;&lt;Executive Name&gt; (via Akki)&#x27; &lt;noreply@cycles.akki.ai&gt;
  Reply-To  :  &lt;account-uuid&gt;@cycles.akki.ai     (opaque alias)

The reply-to alias is deterministic per account (UUIDv5). Inbound
replies hit the Postmark webhook (&#x60;routers/inbound_email.py&#x60;) and
are threaded back to this &#x60;cycle_followups&#x60; row by alias→account
lookup + most-recent-unanswered-followup-to-this-recipient match.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "followup_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/follow-ups/draft",
    alias:
      "draft_followups_api_contexts__context_id__cycle_follow_ups_draft_post",
    description: `Generate restrained follow-up drafts for unmet contributions.
Returns the drafts; nothing is sent.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FollowUpsDraftIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([FollowUpDraftsResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/readiness",
    alias: "get_readiness_api_contexts__context_id__cycle_readiness_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/schedule",
    alias: "get_cycle_schedule_api_contexts__context_id__cycle_schedule_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ScheduleResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/api/contexts/:context_id/cycle/schedule",
    alias: "upsert_cycle_schedule_api_contexts__context_id__cycle_schedule_put",
    description: `Single schedule per context — easier mental model for the executive
than &#x27;manage N schedules&#x27;. To change cadence, just PUT again.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CycleScheduleIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ScheduleResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/cycle/schedule",
    alias:
      "disable_cycle_schedule_api_contexts__context_id__cycle_schedule_delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycle/team",
    alias: "list_team_api_contexts__context_id__cycle_team_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([CycleTeamResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycle/team",
    alias: "upsert_team_member_api_contexts__context_id__cycle_team_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TeamMemberIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/cycle/team/:member_id",
    alias:
      "delete_team_member_api_contexts__context_id__cycle_team__member_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "member_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/cycle/team/:member_id",
    alias:
      "patch_team_member_api_contexts__context_id__cycle_team__member_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TeamMemberPatch,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "member_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles",
    alias: "create_cycle_api_contexts__context_id__cycles_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ title: z.string().min(1).max(200) }).passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycles",
    alias: "list_cycles_api_contexts__context_id__cycles_get",
    description: `Cycle list with ListingShell-shaped pagination envelope.

Cycle Manager Feel pass (Patch 2 of 4, 2026-02): added &#x60;status&#x60;
filter, mirrored Work Studio&#x27;s &#x60;counts_by_status&#x60; envelope, and
extended each row with intel fields for the Cycle Card visual:
&#x60;agenda_count&#x60;, &#x60;team_count&#x60;, &#x60;readiness_pct&#x60;, &#x60;last_activity_at&#x60;,
&#x60;next_action_hint&#x60;.

J2 (2026-05-25, G22 ratified): OR-includes rows where the
requesting account_id is in &#x60;seed_marker_visible_for&#x60; — the
demo-attached user sees the seeded &#x60;DEMO_T5_BACKLOG&#x60; cycle(s)
alongside their own without copying or mutating cross-context
ownership.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "sort",
        type: "Query",
        schema: z
          .string()
          .regex(/^(recent|oldest|alpha|status)$/)
          .optional()
          .default("recent"),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(60).optional().default(10),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycles/:cycle_id",
    alias: "get_cycle_api_contexts__context_id__cycles__cycle_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/activate",
    alias:
      "activate_cycle_api_contexts__context_id__cycles__cycle_id__activate_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/agenda-items/:agenda_item_id/check-team-duplicate",
    alias:
      "check_team_duplicate_api_contexts__context_id__cycles__cycle_id__agenda_items__agenda_item_id__check_team_duplicate_post",
    description: `Return 409 if a team member with the same (name,email) is
already assigned to this agenda_item_id on this cycle_id. Returns
200 otherwise.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CatalogueMemberIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "agenda_item_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycles/:cycle_id/agenda-items/:agenda_item_id/eligible-contributors",
    alias:
      "list_eligible_contributors_api_contexts__context_id__cycles__cycle_id__agenda_items__agenda_item_id__eligible_contributors_get",
    description: `Return team members assigned to a specific agenda item on a
specific cycle. Used to scope the Contributions tab contributor
dropdown per PO decision #2.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "agenda_item_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/apply-template",
    alias:
      "apply_template_api_contexts__context_id__cycles__cycle_id__apply_template_post",
    description: `Seed a draft cycle with a structured template.

Quick Action &quot;Prepare for Main Board&quot; — &#x60;template_key&#x3D;&quot;main_board&quot;&#x60;:
  • Seeds 6 agenda items (in canonical order).
  • Seeds the team from the workspace &#x60;team_catalogue&#x60;, with empty
    role / contribution_description / agenda_assignments.
  • Idempotent — refuses (409, &#x60;cycle_not_empty&#x60;) if the cycle
    already has agenda items.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ template_key: z.string().min(1).max(64) })
          .passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/briefs/:brief_id/assignments",
    alias:
      "create_assignments_api_contexts__context_id__cycles__cycle_id__briefs__brief_id__assignments_post",
    description: `Fan-out one assignment row per NED.

Exactly one of &#x60;ned_ids&#x60; / &#x60;cohort_id&#x60; MUST be set (mutually exclusive).
Cohort resolution snapshots ned ids at assignment time and persists
them on the row so a future cohort membership change doesn&#x27;t retro-
actively affect existing assignments.

Returns: {&quot;assignments&quot;: [AssignmentOut], &quot;count&quot;: N}.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AssignmentCreateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycles/:cycle_id/briefs/:brief_id/assignments",
    alias:
      "list_assignments_api_contexts__context_id__cycles__cycle_id__briefs__brief_id__assignments_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/briefs/:brief_id/submit-for-board",
    alias:
      "submit_brief_for_board_api_contexts__context_id__cycles__cycle_id__briefs__brief_id__submit_for_board_post",
    description: `Mark a brief as submitted for board reporting.

State transition: board_status null|draft -&gt; submitted (idempotent
if already submitted; refuses if already shipped).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: SubmitForBoardOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/close",
    alias: "close_cycle_api_contexts__context_id__cycles__cycle_id__close_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/cycles/:cycle_id/questions",
    alias:
      "list_cycle_questions_api_contexts__context_id__cycles__cycle_id__questions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "asker_role",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "sort",
        type: "Query",
        schema: z.string().optional().default("recent"),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/cycles/:cycle_id/questions",
    alias:
      "raise_question_api_contexts__context_id__cycles__cycle_id__questions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__questions__QuestionIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/decks",
    alias: "list_decks_api_contexts__context_id__decks_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(30),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/decks/:deck_id",
    alias: "get_deck_api_contexts__context_id__decks__deck_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "deck_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/decks/:deck_id/feedback",
    alias: "feedback_api_contexts__context_id__decks__deck_id__feedback_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__decks__FeedbackIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "deck_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/decks/:deck_id/quality_check",
    alias:
      "quality_check_api_contexts__context_id__decks__deck_id__quality_check_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "deck_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/decks/:outline_id/generate",
    alias:
      "generate_deck_api_contexts__context_id__decks__outline_id__generate_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: GenerateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "outline_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/decks/:outline_id/generate/stream",
    alias:
      "decks_generation_stream_api_contexts__context_id__decks__outline_id__generate_stream_post",
    description: `SSE-wrap of the Decks generate handler.

Phases (6): Reading the outline → Checking the grounding contract
→ Composing the deck → Rendering the slides → Validating →
Almost there.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "outline_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/decks/outline",
    alias: "create_outline_api_contexts__context_id__decks_outline_post",
    description: `Plan a deck cheaply; surface gaps; do NOT consume the deck deep slot.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OutlineIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/document-journal",
    alias:
      "get_document_journal_api_contexts__context_id__document_journal_get",
    description: `Listing projection for the Document Journal surface.

Returns docs newest-first with the marker fields the UI renders
inline (sensitivity, data_trust, source_channel, has_commentary).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/document-journal/recent",
    alias:
      "get_document_journal_recent_api_contexts__context_id__document_journal_recent_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(5),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/document-journal/search",
    alias:
      "search_document_journal_api_contexts__context_id__document_journal_search_get",
    description: `Phase E — ranked full-text search across the Document Journal.
Hits include doc body + journal_commentary + name + metadata
(doc_kind, sensitivity_band, source_channel). Scoped to the active
context (Privacy Wall — boundaries respected via the same
require_context_membership dependency every other doc endpoint
uses).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "q",
        type: "Query",
        schema: z.string().optional().default(""),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents",
    alias: "upload_document_api_contexts__context_id__documents_post",
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body_upload_document_api_contexts__context_id__documents_post,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents",
    alias: "list_documents_api_contexts__context_id__documents_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "origin",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "category",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "search",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id",
    alias:
      "get_document_detail_api_contexts__context_id__documents__doc_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/documents/:doc_id",
    alias:
      "update_document_trust_api_contexts__context_id__documents__doc_id__patch",
    description: `Patch trust and/or evolution-chain link.

The endpoint name predates the evolution-link feature (added iter34); the
payload now carries either &#x60;data_trust&#x60;, &#x60;related_doc_id&#x60;, or both.
Passing &#x60;related_doc_id&#x3D;null&#x60; unlinks the document from any predecessor.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DocumentTrustUpdate,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/documents/:doc_id",
    alias:
      "archive_document_api_contexts__context_id__documents__doc_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/briefings/generate",
    alias:
      "generate_briefing_from_document_api_contexts__context_id__documents__doc_id__briefings_generate_post",
    description: `Sprint Z1.5 (2026-05-29) — Generate a briefing scoped to one
document. Replaces the older Drawer behaviour of redirecting to
Solva when the founder clicks &#x60;Generate brief&#x60;.

Flow:
  1. Resolve all signals in &#x60;db.signals&#x60; whose &#x60;sources[].doc_id&#x60;
     matches the document&#x27;s id (&#x60;status&#x3D;active&#x60; only).
  2. If zero, return 400 with the same copy the briefings router
     already uses, so the drawer can surface a clear toast.
  3. Otherwise spawn the existing &#x60;_create_briefing_worker&#x60; via
     &#x60;_create_job&#x60; so the job-poll contract the briefings tab
     already uses works unchanged.

Returns &#x60;{job_id, status: &quot;queued&quot;}&#x60; like the canonical endpoint.
The frontend polls &#x60;/api/jobs/{job_id}&#x60; to discover the new
&#x60;briefing_id&#x60; on completion, then routes the founder to
&#x60;/app/work-studio?tab&#x3D;briefings&amp;highlight&#x3D;{briefing_id}&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([AsyncJobResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/download",
    alias:
      "download_document_api_contexts__context_id__documents__doc_id__download_get",
    description: `Phase E.3 — Direct document download in PDF / DOCX / PPTX.
Drafts ship with a diagonal DRAFT watermark embedded into the
exported bytes. Committed exports have no watermark. If
watermarking fails (lib error / malformed input), the export is
blocked with HTTP 503 — preserving the original spec&#x27;s hard rule
that no draft ships without its watermark.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "format",
        type: "Query",
        schema: z.string().optional().default("pdf"),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/engagement",
    alias:
      "get_engagement_api_contexts__context_id__documents__doc_id__engagement_get",
    description: `Returns the engagement summary for one document:

{
  &quot;view_count&quot;: int,                  # total views (all readers, all days)
  &quot;unique_readers&quot;: int,              # distinct accounts (excl. owner)
  &quot;readers&quot;: [{name, email, last_viewed_at, view_count}],
  &quot;share_count&quot;: int,
  &quot;shares&quot;: [{shared_with_name, shared_with_email, shared_by_name, created_at}],
  &quot;linked_count&quot;: int,
  &quot;linked_documents&quot;: [{id, name, relation, created_at}]
}`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([DocumentEngagementResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/evolution-diff",
    alias:
      "document_evolution_diff_api_contexts__context_id__documents__doc_id__evolution_diff_post",
    description: `LLM-powered &quot;what changed&quot; between this doc and its immediate
predecessor. Used by the NED Document Evolution panel to surface drift
in recurring reports across cycles.

Returns:
    {
      &quot;previous_doc&quot;: {id, name, created_at} | null,
      &quot;diff&quot;: {
        &quot;what_changed&quot;: &quot;&lt;2-3 sentences: the headline of the drift&gt;&quot;,
        &quot;added_or_strengthened&quot;: [&quot;&lt;bullet&gt;&quot;, ...],
        &quot;weakened_or_removed&quot;:   [&quot;&lt;bullet&gt;&quot;, ...],
        &quot;questions_for_management&quot;: [&quot;&lt;bullet&gt;&quot;, &quot;&lt;bullet&gt;&quot;]
      } | null
    }

Cached on the doc record; pass ?refresh&#x3D;true to regenerate.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([DiffResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/evolution-diff/async",
    alias:
      "evolution_diff_async_api_contexts__context_id__documents__doc_id__evolution_diff_async_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([StatusKindResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/export-guard",
    alias:
      "check_export_guard_api_contexts__context_id__documents__doc_id__export_guard_get",
    description: `Phase E.3 — DRAFT export guard. Per E.3 scope-compliance
(2026-05-26): drafts ARE exportable now — the download endpoint
embeds a visible DRAFT watermark before serving the bytes. The
guard returns &#x60;can_export: True&#x60; plus &#x60;watermark_required: True&#x60;
on drafts so callers can confirm a stamp will be applied.

The spec-compliant block-on-failure path still lives inside the
download endpoint: if watermarking actually fails, the export is
refused with HTTP 503 + &#x60;code: DRAFT_WATERMARK_FAILED&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ExportPolicyResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/extract",
    alias:
      "trigger_extraction_api_contexts__context_id__documents__doc_id__extract_post",
    description: `Spawn LLM extraction for this document. Returns 202 Accepted
immediately; the actual extraction happens in the background.
Caller can verify completion later via the &#x60;extractions_log&#x60;
collection or by polling the target collections.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExtractTriggerIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([DocumentExtractResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/intelligence",
    alias:
      "get_document_intelligence_api_contexts__context_id__documents__doc_id__intelligence_get",
    description: `Phase E.3 — returns the cached intelligence envelope. When no
cache row exists OR the cached hash mismatches the current doc,
returns &#x60;{status: &quot;pending&quot;}&#x60; so the drawer renders the skeleton.
Frontend then POSTs /intelligence/regenerate to kick off the async
extraction.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/intelligence/regenerate",
    alias:
      "regenerate_document_intelligence_api_contexts__context_id__documents__doc_id__intelligence_regenerate_post",
    description: `Phase E.3 — kick off async intelligence extraction. Returns
immediately with &#x60;{status: &quot;queued&quot;}&#x60;. The drawer polls
/intelligence until status becomes &quot;ready&quot;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([IntelligenceRegenerateResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/journal-commentary",
    alias:
      "journal_commentary_api_contexts__context_id__documents__doc_id__journal_commentary_post",
    description: `Generate (or return cached) Akki commentary on a single document.

~400 word target, FT-voice, dry, specific. Cached on the row;
subsequent calls return cached unless &#x60;?refresh&#x3D;true&#x60;.

Phase 1 (2026-05-05): the generation logic lives in
&#x60;document_commentary_service.generate_journal_commentary&#x60; so the
backfill script (&#x60;scripts/backfill_journal_commentary.py&#x60;) calls
the exact same function. The pre-Phase-1 surface mis-label
(&#x60;synisense_pipeline.run(... surface&#x3D;&quot;briefing&quot;)&#x60;) is fixed in
that shared service and surfaced here through the same import.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([JournalCommentaryResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/journal-commentary/async",
    alias:
      "generate_commentary_async_api_contexts__context_id__documents__doc_id__journal_commentary_async_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([StatusKindResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/paragraphs",
    alias:
      "get_document_paragraphs_api_contexts__context_id__documents__doc_id__paragraphs_get",
    description: `Return the paragraph anchors for this document. Lazy-computes on
first read; subsequent reads return the cached array. The doc row is
updated in-place with &#x60;paragraphs[]&#x60;, &#x60;paragraphs_computed_at&#x60;, and
&#x60;paragraphs_version&#x60;.

Response shape:
    {
      &quot;doc_id&quot;: str,
      &quot;paragraphs&quot;: [...],
      &quot;page_count&quot;: int,
      &quot;computed_at&quot;: str (iso),
      &quot;version&quot;: int
    }`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ParagraphsResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/paragraphs/:pid/original",
    alias:
      "get_paragraph_original_api_contexts__context_id__documents__doc_id__paragraphs__pid__original_get",
    description: `Phase 12.2 ITEM B — server-side shield_map reversal for a single
paragraph. Members of the context can read the un-redacted original
via this endpoint as long as the per-paragraph shield map hasn&#x27;t
expired (24h default TTL). Never returns the shield_map itself or
any encrypted bytes — only the plain-text reversal. Per-request
audit row written via &#x60;synisense.unshield&#x60;. After TTL expiry, the
shield_map is gone and the endpoint returns 410.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "pid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/related",
    alias:
      "list_related_documents_api_contexts__context_id__documents__doc_id__related_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/share",
    alias:
      "share_document_api_contexts__context_id__documents__doc_id__share_post",
    description: `Record a share intent for the document. The actual email send is
deferred (mirrors the /shares router pattern); for now we persist
the share record so the engagement panel can report it.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DocumentShareIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([IdResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/summary",
    alias:
      "generate_document_summary_api_contexts__context_id__documents__doc_id__summary_post",
    description: `AKKI summary of a single document for the Document Journal.

Returns:
    - tldr: 2-3 sentence executive summary
    - highlights: list of 4-7 important points the reader should know
    - questions: list of 2-3 questions the reader should bring back

Cached on the document so opening it twice doesn&#x27;t re-burn the LLM.
Pass ?refresh&#x3D;true to regenerate.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/summary/async",
    alias:
      "generate_summary_async_api_contexts__context_id__documents__doc_id__summary_async_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "refresh",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.union([StatusKindResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/:doc_id/thread",
    alias:
      "document_thread_api_contexts__context_id__documents__doc_id__thread_get",
    description: `Return the thread of linked documents for this doc — ancestors (the
chain of related_doc_id pointers back to the origin) plus descendants
(anything that points TO this doc).`,
    requestFormat: "json",
    parameters: [
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ThreadAncestryResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/:doc_id/view",
    alias: "record_view_api_contexts__context_id__documents__doc_id__view_post",
    description: `Record (or refresh) a read-receipt for the current account on this
document. Idempotent across a single UTC day.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/documents/drafts",
    alias:
      "list_draft_documents_api_contexts__context_id__documents_drafts_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
    ],
    response: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/generate-meta",
    alias:
      "generate_document_meta_api_contexts__context_id__documents_generate_meta_post",
    description: `Given a filename and optional preview text, ask the LLM to propose a
short display name and ≤300-char description. Used by the upload modal.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DocumentMetaGenerateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([DocumentMetaResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/generate-meta/async",
    alias:
      "generate_meta_async_api_contexts__context_id__documents_generate_meta_async_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([StatusKindResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/documents/manual-create",
    alias:
      "manual_create_document_api_contexts__context_id__documents_manual_create_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ManualCreateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/events/sync-calendar/stream",
    alias:
      "events_calendar_sync_stream_api_contexts__context_id__events_sync_calendar_stream_post",
    description: `SSE-wrap of the Calendar sync handler.

Phases (5): Reaching Google Calendar → Reading your calendar list
→ Fetching the upcoming events → Mapping to your context →
Almost there.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "provider",
        type: "Query",
        schema: z.string().optional().default("google"),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/exco-teams",
    alias: "create_exco_team_api_contexts__context_id__exco_teams_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExcoCreateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExcoTeamOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/exco-teams",
    alias: "list_exco_teams_api_contexts__context_id__exco_teams_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "include_archived",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.array(ExcoTeamOut),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/exco-teams/:team_id",
    alias: "get_exco_team_api_contexts__context_id__exco_teams__team_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "team_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExcoTeamOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/exco-teams/:team_id",
    alias:
      "update_exco_team_api_contexts__context_id__exco_teams__team_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExcoUpdateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "team_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExcoTeamOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/exco-teams/:team_id",
    alias:
      "archive_exco_team_api_contexts__context_id__exco_teams__team_id__delete",
    description: `Soft delete — sets status&#x3D;&#x27;archived&#x27;. Never hard-deletes.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "team_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExcoTeamOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/exco-teams/:team_id/members",
    alias:
      "add_exco_member_api_contexts__context_id__exco_teams__team_id__members_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ account_id: z.string() }).passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "team_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExcoTeamOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/exco-teams/:team_id/members/:member_id",
    alias:
      "remove_exco_member_api_contexts__context_id__exco_teams__team_id__members__member_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "team_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "member_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: ExcoTeamOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/export",
    alias: "export_context_api_contexts__context_id__export_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/home/coming-up",
    alias: "home_coming_up_api_contexts__context_id__home_coming_up_get",
    description: `Aggregate upcoming items for the active context.

Currently surfaces only cycle close dates (the sole wired
sub-source). Other sub-sources are tracked in
HOME_CLEANUP_LOG.md and will surface here once their data
sources land — additive, no client-side changes required.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "days",
        type: "Query",
        schema: z.number().int().optional().default(14),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/home/insights",
    alias: "home_insights_api_contexts__context_id__home_insights_get",
    description: `Returns leading-insight counts for the active context in one shot.
Side-effect: records the visit so the next &quot;What&#x27;s new&quot; query has
an anchor timestamp.

Phase B Home cleanup (2026-05-26): added &#x60;drafts_ready&#x60; +
&#x60;documents_to_review&#x60; to back the new 5-tile plate. Legacy
counts (compile_ready, pulse_critical, open_questions,
cycles_closing, signoffs_needed, solva_waiting, new_documents)
remain so existing consumers + tests stay green.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/home/whats-new",
    alias: "home_whats_new_api_contexts__context_id__home_whats_new_get",
    description: `Returns a chronological feed of context activity since &#x60;since&#x60;
(ISO timestamp). If &#x60;since&#x60; is omitted, uses the user&#x27;s previous
recorded visit on this context.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "since",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/inbound-queue",
    alias: "list_inbound_queue_api_contexts__context_id__inbound_queue_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: z.string().optional().default("pending_review"),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/inbound-queue/:queue_id",
    alias:
      "get_inbound_queue_item_api_contexts__context_id__inbound_queue__queue_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "queue_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/inbound-queue/:queue_id/accept",
    alias:
      "accept_inbound_queue_item_api_contexts__context_id__inbound_queue__queue_id__accept_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AcceptIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "queue_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/inbound-queue/:queue_id/reject",
    alias:
      "reject_inbound_queue_item_api_contexts__context_id__inbound_queue__queue_id__reject_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RejectIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "queue_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/influence-map",
    alias: "get_influence_map_api_contexts__context_id__influence_map_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "days",
        type: "Query",
        schema: z.number().int().gte(1).lte(365).optional().default(30),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/influence-map/digest",
    alias:
      "send_influence_digest_now_api_contexts__context_id__influence_map_digest_post",
    description: `Send the Influence Digest email for THIS context to the calling user
immediately. Used by the admin tile and as the unit of work the cron
calls per context.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/invitations",
    alias: "create_invitation_api_contexts__context_id__invitations_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: InvitationIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/invitations",
    alias: "list_invitations_api_contexts__context_id__invitations_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/invitations/:invitation_id",
    alias:
      "revoke_invitation_api_contexts__context_id__invitations__invitation_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "invitation_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/leave",
    alias: "leave_context_api_contexts__context_id__leave_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/lens/coach/sessions",
    alias:
      "start_coach_session_api_contexts__context_id__lens_coach_sessions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CoachStartIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/lens/coach/sessions",
    alias:
      "list_coach_sessions_api_contexts__context_id__lens_coach_sessions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/lens/coach/sessions/:sid",
    alias:
      "get_coach_session_api_contexts__context_id__lens_coach_sessions__sid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/lens/coach/sessions/:sid",
    alias:
      "archive_coach_session_api_contexts__context_id__lens_coach_sessions__sid__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/lens/coach/sessions/:sid/messages",
    alias:
      "post_coach_message_api_contexts__context_id__lens_coach_sessions__sid__messages_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CoachMessageIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/lens/run",
    alias: "run_lens_api_contexts__context_id__lens_run_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: LensRunIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/lens/runs",
    alias: "list_lens_runs_api_contexts__context_id__lens_runs_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "lens",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/lens/runs/:run_id",
    alias: "get_lens_run_api_contexts__context_id__lens_runs__run_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "run_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/lens/runs/:run_id",
    alias:
      "archive_lens_run_api_contexts__context_id__lens_runs__run_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "run_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/llm/probe",
    alias: "llm_probe_api_contexts__context_id__llm_probe_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: LLMProbeIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/members",
    alias: "list_members_api_contexts__context_id__members_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/members/:account_id",
    alias:
      "remove_member_api_contexts__context_id__members__account_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "account_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/mentions",
    alias: "list_my_mentions_api_contexts__context_id__mentions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "unread_only",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/mentions/:mention_id/read",
    alias:
      "mark_mention_read_api_contexts__context_id__mentions__mention_id__read_post",
    requestFormat: "json",
    parameters: [
      {
        name: "mention_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/minutes",
    alias: "list_minutes_api_contexts__context_id__minutes_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/minutes/:doc_id/extract",
    alias:
      "extract_minutes_api_contexts__context_id__minutes__doc_id__extract_post",
    description: `LLM-extract structured minutes data from the document.

Pulls: meeting_date, attendees[], decisions[], actions[], questions[].
Caches the result on the document under &#x60;minutes_meta&#x60; so the structured
view loads instantly on subsequent reads.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/minutes/:doc_id/narrative",
    alias:
      "minutes_narrative_api_contexts__context_id__minutes__doc_id__narrative_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/minutes/:doc_id/to_cycle",
    alias:
      "minutes_to_cycle_api_contexts__context_id__minutes__doc_id__to_cycle_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/monitor",
    alias: "get_monitor_api_contexts__context_id__monitor_get",
    description: `Returns the role-adaptive Monitor payload.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "function",
        type: "Query",
        schema: z
          .string()
          .regex(/^(ceo|cfo|coo|commercial|ned|other)$/)
          .optional()
          .default("ceo"),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/monitor/:kind",
    alias: "list_items_api_contexts__context_id__monitor__kind__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "owner",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "owner_role",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(5),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/monitor/:kind",
    alias: "create_item_api_contexts__context_id__monitor__kind__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/monitor/:kind/:rid",
    alias: "get_item_api_contexts__context_id__monitor__kind___rid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/monitor/:kind/:rid",
    alias: "update_item_api_contexts__context_id__monitor__kind___rid__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/monitor/:kind/:rid",
    alias: "delete_item_api_contexts__context_id__monitor__kind___rid__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/monitor/:kind/:rid/update-status",
    alias:
      "update_status_assessment_api_contexts__context_id__monitor__kind___rid__update_status_post",
    description: `Akki-driven status reassessment (non-overridable).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: StatusAssessmentBody,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/monitor/auto-suggest-objectives",
    alias:
      "auto_suggest_objectives_api_contexts__context_id__monitor_auto_suggest_objectives_get",
    description: `Suggest objectives derived from active cycles and Solva sessions.

QA-2026-05-16-046 — filter out candidates whose source cycle/session
is already represented in the existing objectives collection (i.e.
a previous accept-suggestion already minted an objective from that
source). Pre-fix, refetching after accept always returned the same
suggestion because the seeding loop didn&#x27;t know what had been
materialised.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/monitor/auto-suggest-projects",
    alias:
      "auto_suggest_projects_api_contexts__context_id__monitor_auto_suggest_projects_get",
    description: `Suggest projects from active cycles.

QA-2026-05-16-046 — see auto_suggest_objectives for the dedup
pattern; identical logic against the &#x60;project&#x60; collection.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/monitor/owner-roles",
    alias:
      "list_owner_role_counts_api_contexts__context_id__monitor_owner_roles_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/pipeline/events",
    alias: "list_pipeline_events_api_contexts__context_id__pipeline_events_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "pipeline_run_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pipeline/run",
    alias: "pipeline_run_api_contexts__context_id__pipeline_run_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PipelineRunIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/pulse/across-boards",
    alias:
      "pulse_across_boards_api_contexts__context_id__pulse_across_boards_get",
    description: `Return cross-board metadata patterns visible from the active
context&#x27;s perspective. Privacy Wall:
  • Reads ONLY db.context_metadata_signatures.
  • Filters out the active context&#x27;s own rows from the OTHER-BOARDS
    count.
  • NEVER returns source_artefact_id, context_id-of-source, or any
    identifier of the originating tenant.
  • Active-board&#x27;s OWN signatures are surfaced as &#x60;active_board_count&#x60;
    so the user sees their board&#x27;s match alongside the others&#x27;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "window_days",
        type: "Query",
        schema: z.number().int().optional().default(30),
      },
      {
        name: "min_other_boards",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/pulse/feed",
    alias: "pulse_feed_api_contexts__context_id__pulse_feed_get",
    description: `Same-context Twitter-style signal feed.

Phase G additions:
  • &#x60;state&#x60; query (default &#x27;active&#x27;) filters by db.signals.state ∈
    {active, bookmarked, resolved, archived}. Falls back to legacy
    &#x60;status&#x60; field for un-migrated rows.
  • &#x60;show_low&#x3D;true&#x60; opts in to low-confidence signals on the
    Active tab. Other tabs always include all confidence levels.
  • &#x60;confidence&#x3D;high|medium|low&#x60; is an explicit filter.
  • Default landing limit is 7 for Active (spec §6 volume restraint).
    Other states default to 50.
  • Cards carry &#x60;comments[]&#x60; inline (G.5 closes PL-01) and
    &#x60;reasoning&#x60; so the drawer can render the spec&#x27;s Reasoning
    section without a second roundtrip.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "type",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "freshness",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "state",
        type: "Query",
        schema: state,
      },
      {
        name: "show_low",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
      {
        name: "confidence",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "origin",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: limit,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/bookmark",
    alias:
      "pulse_bookmark_api_contexts__context_id__pulse_signals__signal_id__bookmark_post",
    description: `Phase G.1 + QA brief E-04 — Bookmarks as first-class state.
Sets state&#x3D;&#x27;bookmarked&#x27; on the signal AND records a per-user
saved row on signal_actions so per-user bookmark history
(multi-NED context) is preserved.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/comment",
    alias:
      "pulse_comment_api_contexts__context_id__pulse_signals__signal_id__comment_post",
    description: `Phase G.5 — comments are now first-class on the signal row.

Persists to BOTH &#x60;db.signal_actions&#x60; (audit trail, preserves the
QA-brief PL-01 historical record) AND &#x60;db.signals.comments[]&#x60;
(the surface the drawer reads from on every revisit). Comments
are private per-account: the feed/drawer only surfaces comments
where &#x60;account_id&#x60; matches the caller.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ note: z.string().min(1).max(2000) }).passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/comments/:comment_id",
    alias:
      "pulse_comment_delete_api_contexts__context_id__pulse_signals__signal_id__comments__comment_id__delete",
    description: `Remove a comment from the signal. Only the comment&#x27;s author
can delete their own comment.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "comment_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/resolve",
    alias:
      "pulse_resolve_api_contexts__context_id__pulse_signals__signal_id__resolve_post",
    description: `Phase G.1 — mark signal resolved. Sets &#x60;state&#x3D;&#x27;resolved&#x27;&#x60; plus
legacy &#x60;status&#x3D;&#x27;resolved&#x27;&#x60; for back-compat. Optional resolution_note
on body is shown in the Resolved tab card.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ResolveIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/save",
    alias:
      "pulse_save_api_contexts__context_id__pulse_signals__signal_id__save_post",
    description: `LEGACY toggle — flips between bookmark/unbookmark.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/share",
    alias:
      "pulse_share_api_contexts__context_id__pulse_signals__signal_id__share_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__pulse__ShareIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/take-to-solva",
    alias:
      "pulse_take_to_solva_api_contexts__context_id__pulse_signals__signal_id__take_to_solva_post",
    description: `Record the action AND mint a Solva v2 session whose intent is
derived from the signal headline+summary. Returns the new
session_id; the frontend then navigates to
/app/solva/session/&lt;session_id&gt;.

We re-use the canonical solva_v2 entrypoint via a programmatic
construct on db.solva_v2_sessions so we don&#x27;t run an HTTP roundtrip
against ourselves. The session is tagged &#x60;from_signal&#x3D;&lt;sid&gt;&#x60; so the
Solva surface can render the framing chip.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/unbookmark",
    alias:
      "pulse_unbookmark_api_contexts__context_id__pulse_signals__signal_id__unbookmark_post",
    description: `Phase G.1 — remove bookmark; returns to Active state.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/pulse/signals/:signal_id/unresolve",
    alias:
      "pulse_unresolve_api_contexts__context_id__pulse_signals__signal_id__unresolve_post",
    description: `Phase G.1 — recover from accidental resolve. Per QA brief E-02:
the user resolved in error and wants the signal back on the
Active tab. Returns state&#x3D;&#x27;active&#x27;; clears resolved metadata.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/questions",
    alias: "list_questions_api_contexts__context_id__questions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "category",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions",
    alias: "add_question_api_contexts__context_id__questions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__cycle__QuestionIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/questions/:qid",
    alias: "patch_question_api_contexts__context_id__questions__qid__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: QuestionPatch,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "qid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/questions/:question_id",
    alias: "get_question_api_contexts__context_id__questions__question_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "question_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions/:question_id/answer",
    alias:
      "answer_question_api_contexts__context_id__questions__question_id__answer_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ text: z.string().min(1).max(4000) }).passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "question_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions/:question_id/link-response",
    alias:
      "link_response_doc_api_contexts__context_id__questions__question_id__link_response_post",
    description: `Attach a response document to the question. The document
must live in the same &#x60;context_id&#x60; (cross-tenant blocked by
&#x60;require_context_membership&#x60;; cross-context blocked here).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ document_id: z.string().min(1).max(200) })
          .passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "question_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions/:question_id/mark-answered",
    alias:
      "mark_question_answered_api_contexts__context_id__questions__question_id__mark_answered_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MarkAnsweredIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "question_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions/:question_id/reopen",
    alias:
      "reopen_question_api_contexts__context_id__questions__question_id__reopen_post",
    description: `Flip Answered → Open. Idempotent on already-Open (200 no-op,
no new audit row). Guards against reopening a question that
was never closed in the first place — that returns 400.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "question_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions/:question_id/share",
    alias:
      "share_question_api_contexts__context_id__questions__question_id__share_post",
    description: `Record a share event on the question. Phase B3 captures the
audit + recipient list; actual email delivery is deferred until
the SendGrid Inbound Parse blocker is unblocked (USER-BLOCKED in
MASTER_STATE Section 5).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__questions__ShareIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "question_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/questions/seed-from-briefings",
    alias:
      "seed_questions_from_briefings_api_contexts__context_id__questions_seed_from_briefings_post",
    description: `Pull &#x27;questions to take into the room&#x27; from every briefing in this
context and persist them as open questions. Idempotent — dedupes by text.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/quick-actions/:action_key/clicked",
    alias:
      "record_quick_action_click_api_contexts__context_id__quick_actions__action_key__clicked_post",
    description: `Increment click count for (context, account, action_key).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "action_key",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/quick-actions/order",
    alias:
      "get_quick_action_order_api_contexts__context_id__quick_actions_order_get",
    description: `Return the 4 canonical action keys ordered by per-account click
count DESC, then last_used_at DESC, with the canonical default
order as the stable tiebreaker for never-clicked keys.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: QuickActionOrderOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/reportees",
    alias: "list_reportees_api_contexts__context_id__reportees_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/reportees",
    alias: "add_reportee_api_contexts__context_id__reportees_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ReporteeIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/reportees/:rid",
    alias: "remove_reportee_api_contexts__context_id__reportees__rid__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/reports",
    alias: "list_reports_api_contexts__context_id__reports_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/reports/:rid",
    alias: "get_report_api_contexts__context_id__reports__rid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/reports/:rid",
    alias: "patch_report_api_contexts__context_id__reports__rid__patch",
    description: `Edit body/title. Author may edit while in &#x60;draft&#x60;; current reviewer may
edit while &#x60;in_review&#x60;. Other tiers — even members — cannot edit, only read.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ReportPatchIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/reports/:rid/export.deck.pdf",
    alias:
      "export_report_deck_pdf_api_contexts__context_id__reports__rid__export_deck_pdf_get",
    description: `Landscape slide-deck export of a finalised report — one page per
section, designed to be projected. Reuses the briefings_service deck
renderer by mapping the report&#x27;s H2 sections to deck items.

Iter32 implementation: minimal viable deck (cover + sections + sources).
Future polish: rich speaker notes per slide and section-level evidence.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/reports/:rid/export.pdf",
    alias:
      "export_report_pdf_api_contexts__context_id__reports__rid__export_pdf_get",
    description: `Download the finalised report as a board-secretariat-ready PDF with a
chain-of-custody back page. Available to context members, the named
author, and any reviewer on the chain — same access surface as &#x60;get&#x60;.
Allowed for &#x60;finalised&#x60; reports; also allowed for &#x60;in_review&#x60; so reviewers
can preview the artefact before approving.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/reports/:rid/polish",
    alias: "polish_report_api_contexts__context_id__reports__rid__polish_post",
    description: `LLM-polish the report body. Only callable by the author in &#x60;draft&#x60; or
the current reviewer in &#x60;in_review&#x60;. Returns the polished body — does NOT
auto-save, so the executive can review the change before committing.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PolishIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/reports/:rid/review",
    alias: "review_report_api_contexts__context_id__reports__rid__review_post",
    description: `Current reviewer approves or sends back. On approve, the next reviewer
becomes pending; if there is no next reviewer, the report is finalised.
On send_back, the entire chain rolls back to the author and they can
revise + send up again.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ReviewActionIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/reports/:rid/send_up",
    alias:
      "send_report_up_api_contexts__context_id__reports__rid__send_up_post",
    description: `Author flips draft → in_review. Notifies the next reviewer via Resend
(or a mailto fallback if Resend is unconfigured). Each call advances the
chain by one position when invoked by the current reviewer; sending from
&#x60;draft&#x60; advances from author (tier 0) to first reviewer (tier 1).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "rid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/reports/compose",
    alias: "compose_report_api_contexts__context_id__reports_compose_post",
    description: `Compose a draft report from this cycle&#x27;s submissions and define the
review chain. Report starts in &#x60;draft&#x60; — author can edit freely, nothing
is sent up until they &#x60;send_up&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ReportComposeIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/shares",
    alias: "create_share_api_contexts__context_id__shares_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ShareCreateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/signals",
    alias: "list_signals_api_contexts__context_id__signals_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/signals/:signal_id",
    alias:
      "dismiss_signal_api_contexts__context_id__signals__signal_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/signals/:signal_id/actions",
    alias:
      "create_signal_action_api_contexts__context_id__signals__signal_id__actions_post",
    description: `Log an action taken on a signal. Idempotent only at the audit-trail
level — a user can act twice and we record both, so the indicator shows
the latest attribution while the audit shows the full history.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SignalActionIn,
      },
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/signals/:signal_id/actions",
    alias:
      "list_signal_actions_api_contexts__context_id__signals__signal_id__actions_get",
    description: `Return the action log for a signal so the card can render indicators
(&#x27;Acted on: &lt;label&gt;&#x27; / &#x27;Shared with N people&#x27;). Most-recent first.`,
    requestFormat: "json",
    parameters: [
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/signals/:signal_id/recommendations",
    alias:
      "get_signal_recommendations_api_contexts__context_id__signals__signal_id__recommendations_get",
    requestFormat: "json",
    parameters: [
      {
        name: "signal_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/signals/generate",
    alias: "generate_signals_api_contexts__context_id__signals_generate_post",
    description: `Chunk 2 — async pattern.

Returns **202 Accepted** with a &#x60;job_id&#x60; immediately. The actual
LLM work runs in a &#x60;BackgroundTasks&#x60; worker that updates the
&#x60;db.async_jobs&#x60; row. Frontend should poll
&#x60;GET /api/jobs/{job_id}&#x60; every 2–3 s and consume the row&#x27;s
&#x60;result&#x60; payload when &#x60;status &#x3D;&#x3D; &quot;completed&quot;&#x60;.

The &#x60;result&#x60; payload mirrors the legacy sync response shape so
the frontend&#x27;s downstream logic (toast, list refresh) keeps
working unchanged.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SignalGenerateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/simulate",
    alias: "simulate_api_contexts__context_id__simulate_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SimulateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/simulations",
    alias: "list_simulations_api_contexts__context_id__simulations_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "committee_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/simulations/:simulation_id",
    alias:
      "get_simulation_api_contexts__context_id__simulations__simulation_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "simulation_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/simulations/:simulation_id",
    alias:
      "archive_simulation_api_contexts__context_id__simulations__simulation_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "simulation_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/solva/v2/sessions",
    alias: "create_session_api_contexts__context_id__solva_v2_sessions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CreateSessionIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/solva/v2/sessions",
    alias: "solva_phase_d_list_sessions",
    description: `Strict context+account scoping.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(200).optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id",
    alias: "solva_phase_d_get_session",
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/answer",
    alias:
      "submit_answer_api_contexts__context_id__solva_v2_sessions__session_id__answer_post",
    description: `Advance the state machine by one answer.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ answer_text: z.string().min(2).max(4000) })
          .passthrough(),
      },
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/attach-document",
    alias:
      "attach_document_api_contexts__context_id__solva_v2_sessions__session_id__attach_document_post",
    description: `Mid-session document anchor.

Two modes, dispatched by Content-Type:
  - multipart/form-data with &#x60;file&#x3D;...&#x60; → upload pipeline runs
    (ClamAV → extract_text → storage save → documents row insert)
    and the resulting doc is anchored.
  - application/json with &#x60;{&quot;document_id&quot;: &quot;...&quot;}&#x60; → link an
    existing doc by id (context-scoped) and anchor it.`,
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/attachments",
    alias:
      "list_session_attachments_api_contexts__context_id__solva_v2_sessions__session_id__attachments_get",
    description: `List anchors currently bound to a session. Lightweight view —
excludes the full &#x60;excerpt&#x60; field so the UI list stays small.`,
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/audit-panel/timeline",
    alias:
      "audit_panel_timeline_api_contexts__context_id__solva_v2_sessions__session_id__audit_panel_timeline_get",
    description: `Compose a per-session privacy-provenance timeline.

Reads the session&#x27;s &#x60;synisense_audit_ids&#x60; array, fetches each
&#x60;synisense_audit_log&#x60; row, and groups by purpose (layer label).
Returns ONE step per audit row plus an aggregate footer.`,
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/framing",
    alias:
      "submit_framing_api_contexts__context_id__solva_v2_sessions__session_id__framing_post",
    description: `Submit initial framing → kicks off Layer 0 (silent FAR) → Layer 1.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ framing_text: z.string().min(20).max(4000) })
          .passthrough(),
      },
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/refuse",
    alias:
      "refuse_session_api_contexts__context_id__solva_v2_sessions__session_id__refuse_post",
    description: `Operator-driven refusal path. Sets status&#x3D;refused without
running the weighting engine.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RefuseIn,
      },
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/solva/v2/sessions/:session_id/title",
    alias:
      "update_session_title_api_contexts__context_id__solva_v2_sessions__session_id__title_patch",
    description: `Save a user-edited session title.

Strict ownership: the underlying &#x60;_get_session&#x60; already enforces
&#x60;account_id &#x3D;&#x3D; ctx.account.id&#x60; AND &#x60;context_id &#x3D;&#x3D; ctx.context.id&#x60;
so cross-tenant overwrites are impossible. Stores &#x60;title_source &#x3D;
&quot;user&quot;&#x60; so a future re-run of &#x60;submit_framing&#x60; won&#x27;t clobber the
user&#x27;s choice (see the idempotency guard there).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ title: z.string().min(1).max(80) }),
      },
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/strategic-goals",
    alias: "list_goals_api_contexts__context_id__strategic_goals_get",
    description: `List all goals on this context. Optional &#x60;department&#x60; filter restricts
to a single function (cfo|coo|commercial|ceo|board).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "department",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/strategic-goals",
    alias: "create_goal_api_contexts__context_id__strategic_goals_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: GoalIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/strategic-goals/:goal_id",
    alias:
      "update_goal_api_contexts__context_id__strategic_goals__goal_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: GoalPatch,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "goal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/strategic-goals/:goal_id",
    alias:
      "delete_goal_api_contexts__context_id__strategic_goals__goal_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "goal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/strategic-goals/:goal_id/evolution",
    alias:
      "goal_evolution_api_contexts__context_id__strategic_goals__goal_id__evolution_get",
    description: `Aggregate every time-series signal for one goal into a single
chronological feed.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "goal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/strategic-goals/:goal_id/update",
    alias:
      "update_strategic_goal_api_contexts__context_id__strategic_goals__goal_id__update_post",
    description: `Akki-driven strategic-goal reassessment.

QA-2026-05-16-049 — replaces the manual &quot;Edit this goal&quot; flow.
Returns shapes:
  • Success path:
    {goal_id, kind: &quot;strategic_goal&quot;, updated: True,
     status, current_score, probability,
     last_akki_update: {assessed_at, audit_id, rationale, ...}}
  • No-data path (no relevant evidence OR LLM said relevant&#x3D;false):
    {goal_id, kind: &quot;strategic_goal&quot;, updated: False,
     no_data: True, message: &lt;verbatim spec copy&gt;,
     last_akki_update: {assessed_at, audit_id, rationale, ...}}

QA-2026-05-16-048 — RBAC defence-in-depth carries over: NED
accounts cannot trigger this (read-only on strategic goals).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: StrategicGoalUpdateIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "goal_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/strategic-goals/extract",
    alias:
      "extract_from_document_api_contexts__context_id__strategic_goals_extract_post",
    description: `Reads the document&#x27;s extracted_text and asks Claude to return board-level
strategic goals as a structured array, then upserts them.

QA-2026-05-16-048 — server-enforced RBAC. NED accounts CANNOT
generate strategic goals (the spec is unambiguous: &quot;the two CTAs
are Exec-only&quot;). The frontend already hides the CTAs but a NED
could still POST directly via curl; this guard closes that gap.
Returns 403 with a clear message so the frontend can surface it
intelligibly if anything bypasses the hide-logic.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExtractFromDocIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/studio/:kind/:artefact_id/engagement",
    alias:
      "get_engagement_api_contexts__context_id__studio__kind___artefact_id__engagement_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/studio/:kind/:artefact_id/rescore",
    alias:
      "rescore_sensitivity_api_contexts__context_id__studio__kind___artefact_id__rescore_post",
    description: `Re-score an artefact&#x27;s sensitivity. &#x60;use_llm&#x3D;true&#x60; invokes the LLM
tiebreaker (iter66) — only escalates when regex returns the ambiguous
&#x27;internal&#x27; band; never downgrades. Costs one standard-tier LLM call
when triggered.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "use_llm",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/studio/:kind/:artefact_id/share",
    alias:
      "record_share_api_contexts__context_id__studio__kind___artefact_id__share_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__studio__ShareIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/studio/:kind/:artefact_id/share-email",
    alias:
      "share_artefact_by_email_api_contexts__context_id__studio__kind___artefact_id__share_email_post",
    description: `Email an artefact with a tracked deep link. Recipient clicks →
records a view (external reader) + redirects to the in-app surface.
External readers increment unique_readers and feed into exposure score.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ShareEmailIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/studio/:kind/:artefact_id/view",
    alias:
      "record_view_api_contexts__context_id__studio__kind___artefact_id__view_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/studio/backfill_sensitivity",
    alias:
      "backfill_sensitivity_api_contexts__context_id__studio_backfill_sensitivity_post",
    description: `One-shot backfill — score every deck + briefing in a context that
doesn&#x27;t already carry a sensitivity record. Idempotent: artefacts
that already have &#x60;sensitivity&#x60; are skipped. Useful after iter64 ships
so the UI can render the strip on day-1 without waiting for a regen.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/studio/history",
    alias: "studio_history_api_contexts__context_id__studio_history_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(30),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/submissions",
    alias: "list_submissions_api_contexts__context_id__submissions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "cycle_name",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/tasks-initiatives",
    alias:
      "list_tasks_initiatives_api_contexts__context_id__tasks_initiatives_get",
    description: `Paginated list of tasks/initiatives for this context.

Filters:
  - &#x60;owner&#x60;               → owner_role exact match (or &#x60;&quot;null&quot;&#x60; for
                            unassigned rows).
  - &#x60;status&#x60;              → status enum exact match.
  - &#x60;parent_objective_id&#x60; → returns ONLY rows under this goal
                            (or &#x60;&quot;null&quot;&#x60; for standalone rows).
  - &#x60;search&#x60;              → case-insensitive substring on &#x60;title&#x60;.

Pagination:
  - Default page_size 50; capped at 200.

Response:
  &#x60;{rows: [...], page, page_size, total}&#x60;`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "owner",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "parent_objective_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "search",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/tasks-initiatives",
    alias:
      "create_task_initiative_api_contexts__context_id__tasks_initiatives_post",
    description: `Manual create. LLM-extracted rows are written directly by
AA-slice-2 (the extraction service) so they can carry
&#x60;extracted_by&#x3D;&quot;llm&quot;&#x60; + the source_document_id. Manual creates
always carry &#x60;extracted_by&#x3D;&quot;manual&quot;&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TaskInitiativeIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/tasks-initiatives/:ti_id",
    alias:
      "get_task_initiative_api_contexts__context_id__tasks_initiatives__ti_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "ti_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/tasks-initiatives/:ti_id",
    alias:
      "patch_task_initiative_api_contexts__context_id__tasks_initiatives__ti_id__patch",
    description: `Partial update. &#x60;updated_at&#x60; + &#x60;last_reassessed_at&#x60; always
refreshed server-side. Immutable fields (&#x60;extracted_by&#x60;,
&#x60;source_document_id&#x60;) are silently ignored even if the caller
smuggles them in — those fields belong to the create path only.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TaskInitiativePatch,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "ti_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/tasks-initiatives/:ti_id",
    alias:
      "delete_task_initiative_api_contexts__context_id__tasks_initiatives__ti_id__delete",
    description: `Soft-delete — flips &#x60;status_active&#x60; to False + writes an audit
row. The collection is never physically purged (cohort retention
+ legal hold).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "ti_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/team-catalogue",
    alias: "list_catalogue_api_contexts__context_id__team_catalogue_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/team-catalogue",
    alias: "add_catalogue_member_api_contexts__context_id__team_catalogue_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CatalogueMemberIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/team-catalogue/:member_id",
    alias:
      "patch_catalogue_member_api_contexts__context_id__team_catalogue__member_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CatalogueMemberPatch,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "member_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/team-catalogue/:member_id",
    alias:
      "soft_delete_catalogue_member_api_contexts__context_id__team_catalogue__member_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "member_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/artefacts",
    alias:
      "create_work_studio_artefact_api_contexts__context_id__work_studio_artefacts_post",
    description: `Create a draft Deck or Report from one of three sources.

The artefact row is inserted into the same kind-aware collection
(&#x60;db.decks&#x60; / &#x60;db.reports&#x60;) the block composer reads from. The
response carries a &#x60;redirect_url&#x60; pointing at the composer surface
so the frontend can hard-redirect after the toast.

422 paths:
  - &#x60;kind&#x60; is not deck/report (briefing is handled elsewhere)
  - &#x60;source&#x60; is not blank/brief/external_document
  - &#x60;source&#x3D;brief&#x60; with no &#x60;source_brief_id&#x60;
  - &#x60;source&#x3D;external_document&#x60; with no &#x60;source_document_id&#x60;

404 paths:
  - &#x60;source_brief_id&#x60; doesn&#x27;t resolve in this account/context
  - &#x60;source_document_id&#x60; doesn&#x27;t resolve in this context`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CreateArtefactRequest,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ArtefactRedirectResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/artefacts/from-solva",
    alias:
      "create_artefact_from_solva_api_contexts__context_id__work_studio_artefacts_from_solva_post",
    description: `Create a Work Studio brief artefact pre-populated with a Phase D
Solva session&#x27;s synthesis. Strict scoping: session must belong to
the active context AND the requesting account.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ session_id: z.string().min(1).max(120) })
          .passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/compilations",
    alias:
      "create_compilation_api_contexts__context_id__work_studio_compilations_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CompilationCreate,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/compilations",
    alias:
      "list_compilations_api_contexts__context_id__work_studio_compilations_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "artefact_type",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/compilations/:compilation_id",
    alias:
      "get_compilation_api_contexts__context_id__work_studio_compilations__compilation_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "compilation_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/compilations/:compilation_id/start",
    alias:
      "start_compilation_api_contexts__context_id__work_studio_compilations__compilation_id__start_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "compilation_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([CompilationStartResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/documents",
    alias: "list_documents_api_contexts__context_id__work_studio_documents_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(20),
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id",
    alias:
      "get_document_api_contexts__context_id__work_studio_documents__artefact_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id",
    alias:
      "patch_document_api_contexts__context_id__work_studio_documents__artefact_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DocumentPatchIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id",
    alias:
      "delete_draft_document_api_contexts__context_id__work_studio_documents__artefact_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([IdResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/commit",
    alias:
      "commit_document_api_contexts__context_id__work_studio_documents__artefact_id__commit_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/create-new-version",
    alias:
      "create_new_version_api_contexts__context_id__work_studio_documents__artefact_id__create_new_version_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/move-to-review",
    alias:
      "move_to_review_api_contexts__context_id__work_studio_documents__artefact_id__move_to_review_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([IdResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/render",
    alias:
      "render_compiled_document_api_contexts__context_id__work_studio_documents__artefact_id__render_get",
    description: `Server-produced render in DOCX / PDF / PPTX (G6 ratified).

Authorisation: the caller must be a member of &#x60;context_id&#x60;; the
require_context_membership dependency enforces that. The artefact
must belong to the same context.

422 paths:
  - &#x60;format&#x60; not in {docx, pdf, pptx}

404 paths:
  - artefact not found in this context

409 paths:
  - artefact has no &#x60;structured_content&#x60; yet (e.g. fresh Draft
    created via T3.1 D5 that hasn&#x27;t been compiled)`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "format",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/revise",
    alias:
      "revise_document_api_contexts__context_id__work_studio_documents__artefact_id__revise_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ReviseIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ArtefactRedirectResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/save",
    alias:
      "save_document_api_contexts__context_id__work_studio_documents__artefact_id__save_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SaveIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([SnapshotResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/versions",
    alias:
      "get_versions_api_contexts__context_id__work_studio_documents__artefact_id__versions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/versions/:version_id",
    alias:
      "get_version_detail_api_contexts__context_id__work_studio_documents__artefact_id__versions__version_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "version_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/:artefact_id/versions/:version_id/restore",
    alias:
      "restore_version_api_contexts__context_id__work_studio_documents__artefact_id__versions__version_id__restore_post",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "version_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/documents/save-draft",
    alias:
      "save_draft_api_contexts__context_id__work_studio_documents_save_draft_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _SaveDraftIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([DraftLifecycleResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/enhance/:kind",
    alias:
      "start_enhance_api_contexts__context_id__work_studio_enhance__kind__post",
    description: `Phase C.3 — start a Work Studio enhance run. Same persistence
shape as export (rows in db.work_studio_exports with source&#x3D;&#x27;enhance&#x27;).`,
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema:
          Body_start_enhance_api_contexts__context_id__work_studio_enhance__kind__post,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ExportStartResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/enhance/:kind/stream",
    alias:
      "work_studio_enhance_stream_api_contexts__context_id__work_studio_enhance__kind__stream_post",
    description: `SSE-wrap of the Work Studio Enhance flow.

Phases (5): Reading the artefact → Checking the grounding contract
→ Composing the refinement → Validating → Almost there.

Inline runner: resolves source → inserts row → runs &#x60;_run_enhance&#x60;
in-process so SSE phases bracket the actual two-pass LLM work.
The &#x60;complete&#x60; event carries the final export row (status,
download_token, continue_chat_id, etc.).`,
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema:
          Body_work_studio_enhance_stream_api_contexts__context_id__work_studio_enhance__kind__stream_post,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/export/:kind",
    alias:
      "start_export_api_contexts__context_id__work_studio_export__kind__post",
    description: `Phase C.2 — start a Work Studio export. Returns 202 immediately
with the export_id. The actual LLM + render run in the background.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExportRequestIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ExportStartResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/exports/:export_id",
    alias:
      "get_export_status_api_contexts__context_id__work_studio_exports__export_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "export_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ExportStartResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/exports/:export_id/download",
    alias:
      "download_export_api_contexts__context_id__work_studio_exports__export_id__download_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "export_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "token",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "inline",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/contexts/:context_id/work-studio/exports/:export_id/stream",
    alias:
      "stream_export_progress_api_contexts__context_id__work_studio_exports__export_id__stream_get",
    description: `Phase L.a (2026-05-27) — SSE observer for an active export.

The &#x60;POST /export/{kind}&#x60; endpoint kicks off a BackgroundTasks
worker (&#x60;_run_export&#x60;) and returns 202 immediately. This endpoint
OBSERVES that worker by polling &#x60;db.work_studio_exports.{phase_index}&#x60;
at 500ms cadence and emits SSE &#x60;phase&#x60; events when the marker
advances. When the row flips to &#x60;status&#x3D;complete&#x60;, the final
&#x60;complete&#x60; event carries the same payload the legacy
&#x60;GET /exports/{eid}&#x60; endpoint returns. On &#x60;status&#x3D;failed&#x60;, an
&#x60;error&#x60; event is emitted. The frontend &#x60;StreamingLogScene&#x60; reads
these events via &#x60;useStreamingProgress&#x60;.

Auth: same membership check as the polling endpoint. Same
cross-account narrowing.

Why &quot;observer&quot; pattern (not synchronous SSE):
  The legacy POST→202+poll architecture is preserved so existing
  clients (Cycle.jsx + ExportModal polling code paths) keep
  working unchanged. The stream endpoint is purely additive.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "export_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/from-document",
    alias:
      "create_work_studio_from_document_api_contexts__context_id__work_studio_from_document_post",
    description: `Create a Draft Work Studio artefact seeded from a Document
Journal item.

422 paths:
  - &#x60;kind&#x60; not in the D5 5-kind set (Pydantic Literal blocks first)

404 paths:
  - &#x60;source_doc_id&#x60; doesn&#x27;t resolve in this context`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FromDocumentRequest,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ArtefactRedirectResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/contexts/:context_id/work-studio/from-source",
    alias:
      "create_from_source_api_contexts__context_id__work_studio_from_source_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FromSourceRequest,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([ArtefactRedirectResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/cron/paragraph-anchors-sweep",
    alias: "cron_paragraph_anchors_sweep_api_cron_paragraph_anchors_sweep_post",
    description: `Nightly batch sweep — compute paragraphs[] for any docs that are
missing them or have stale &#x60;paragraphs_version&#x60;. Designed for the
APScheduler entry registered in server.py @ 03:00 UTC.

Gated by &#x60;X-Cron-Secret&#x60; matching the &#x60;AKKI_CRON_SECRET&#x60; env var.
Anonymous callers get 401; missing env var fails closed with 503.
Per-doc timeout is enforced by an asyncio.wait_for at the caller.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
      {
        name: "X-Cron-Secret",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/cron/weekly-digest",
    alias: "cron_weekly_digest_api_cron_weekly_digest_post",
    description: `Internal cron endpoint — called by APScheduler every Monday 08:00
UTC. Iterates every active executive role across every context,
builds the previous-7-day digest, and emails each executive their
own roll-up.

Authenticated via the &#x60;AKKI_CRON_SECRET&#x60; shared header. Mirrors the
blog cron so the same secret rotates the lot.`,
    requestFormat: "json",
    parameters: [
      {
        name: "x-cron-secret",
        type: "Header",
        schema: z.string().optional().default(""),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/csrf",
    alias: "csrf_api_csrf_get",
    description: `Mint (or refresh) the per-session CSRF token. Idempotent — call
on app boot, after sign-in, or whenever the existing cookie has
expired. The frontend axios wrapper calls this before any
state-changing request when its in-memory token cache is empty.

The token is returned in the JSON body so clients without cookie
access (mobile app builds, server-side rendering) can still pull
it; the cookie is the primary delivery channel for browsers.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/cycle/cron/run-schedules",
    alias: "cron_run_schedules_api_cycle_cron_run_schedules_post",
    description: `Cron-protected. Iterates all enabled schedules whose next_run_at has
passed, drafts pending_approval checklists for each, then advances
next_run_at. Designed to run hourly — idempotent because we update
next_run_at atomically.`,
    requestFormat: "json",
    parameters: [
      {
        name: "X-Cron-Secret",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/decks/:deck_id/context",
    alias: "resolve_deck_context_api_decks__deck_id__context_get",
    requestFormat: "json",
    parameters: [
      {
        name: "deck_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/docs/bundle.zip",
    alias: "download_doc_bundle_api_docs_bundle_zip_get",
    description: `Stream a zip containing PRODUCT.md + DEVELOPMENT.md as
AKKI_PRODUCT.md and AKKI_DEVELOPMENT.md respectively.

Builds in-memory (&#x60;io.BytesIO&#x60;) — no disk artefact, no temp file.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/docs/development",
    alias: "download_development_doc_api_docs_development_get",
    description: `Stream DEVELOPMENT.md as an attachment.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/docs/product",
    alias: "download_product_doc_api_docs_product_get",
    description: `Stream PRODUCT.md as an attachment.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/documents/:doc_id/attachments",
    alias: "create_document_attachment_api_documents__doc_id__attachments_post",
    description: `Create an explicit attachment from &#x60;doc_id&#x60; (source) to
&#x60;target_doc_id&#x60;. Symmetric — the Related-docs endpoint surfaces
the link from either side.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AttachmentCreateBody,
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/documents/:doc_id/attachments/:attachment_id",
    alias:
      "delete_document_attachment_api_documents__doc_id__attachments__attachment_id__delete",
    description: `Remove an attachment. The caller must own at least one side of
the link (no cross-account stitching).`,
    requestFormat: "json",
    parameters: [
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "attachment_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/documents/:doc_id/lineage",
    alias: "patch_document_lineage_api_documents__doc_id__lineage_patch",
    description: `Mark &#x60;doc_id&#x60; as derived from &#x60;parent_doc_id&#x60;. Set
&#x60;parent_doc_id: null&#x60; to unlink.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: LineagePatchBody,
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/documents/:doc_id/prompted-edit",
    alias: "prompted_edit_api_documents__doc_id__prompted_edit_post",
    description: `Phase E.3 — prompted-edit pipeline. Returns proposed new body
WITHOUT committing. Caller (the drawer) then renders a diff
preview and POSTs a PATCH to commit if the user accepts.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ prompt: z.string().min(1).max(2000) }).passthrough(),
      },
      {
        name: "doc_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/early-access/register",
    alias: "register_api_early_access_register_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__early_access__RegisterIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/early-access/registrations",
    alias: "list_registrations_api_early_access_registrations_get",
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/enterprise/interest",
    alias: "record_interest_api_enterprise_interest_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EnterpriseInterestIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/enterprise/interest/me",
    alias: "my_latest_interest_api_enterprise_interest_me_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/events",
    alias: "record_event_api_events_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TelemetryEventIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/feedback",
    alias: "submit_feedback_api_feedback_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__feedback__FeedbackIn,
      },
      {
        name: "send",
        type: "Query",
        schema: z.number().int().gte(0).lte(1).optional().default(1),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/health",
    alias: "health_api_health_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/health/composite",
    alias: "composite_health_api_health_composite_get",
    description: `Public composite health probe. 30s cache.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/healthz/clamav",
    alias: "healthz_clamav_api_healthz_clamav_get",
    description: `Read-only ClamAV daemon health-status snapshot. No auth —
designed for Kubernetes liveness/readiness probes + ops
dashboards.

ALWAYS returns HTTP 200. Probes that want a strict gate should
branch on &#x60;&#x60;clamd_daemon&#x60;&#x60; in the body (&#x60;&#x60;alive&#x60;&#x60; is the only
healthy state).`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/healthz/shield",
    alias: "healthz_shield_api_healthz_shield_get",
    description: `Read-only Shield readiness snapshot. No auth — designed for
Kubernetes &#x60;&#x60;readinessProbe&#x60;&#x60; / external monitors.

Returns the warmup snapshot from
&#x60;&#x60;deidentifier.get_warmup_state()&#x60;&#x60;. If &#x60;&#x60;ready&#x3D;false&#x60;&#x60;, HTTP
code is 503 so probes mark the pod unhealthy; otherwise 200.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/help/features",
    alias: "get_help_features_api_help_features_get",
    description: `Return the product spec as JSON envelope for the React
&#x60;/help&#x60; page to render.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/help/features.md",
    alias: "get_help_features_raw_api_help_features_md_get",
    description: `Same content, served as raw &#x60;text/markdown&#x60; for direct browser
download / sharing. Keeps the route family consistent with
&#x60;/api/product-features.md&#x60;.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ideas/digest/:week_iso",
    alias: "get_specific_digest_api_ideas_digest__week_iso__get",
    requestFormat: "json",
    parameters: [
      {
        name: "week_iso",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/ideas/digest/current",
    alias: "get_current_digest_api_ideas_digest_current_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ideas/digest/history",
    alias: "get_digest_history_api_ideas_digest_history_get",
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(12),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ideas/digest/regenerate",
    alias: "regenerate_current_digest_api_ideas_digest_regenerate_post",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ideas/preferences",
    alias: "get_preferences_endpoint_api_ideas_preferences_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "put",
    path: "/api/ideas/preferences",
    alias: "put_preferences_endpoint_api_ideas_preferences_put",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PreferencesPutRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/inbound/address",
    alias: "get_inbound_address_api_inbound_address_get",
    description: `Return the user&#x27;s forwarding address (and a context-scoped variant).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/inbound/postmark",
    alias: "receive_postmark_inbound_api_inbound_postmark_post",
    description: `DEPRECATED (2026-05-26) — Postmark inbound has been replaced by
SendGrid Inbound Parse. This route returns 410 Gone with a migration
note. Re-point the inbound webhook in your provider dashboard to
&#x60;/api/inbound/sendgrid&#x60; (multipart/form-data, optional HTTP Basic
Auth). Will be removed in the next release cycle.`,
    requestFormat: "json",
    parameters: [
      {
        name: "secret",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/inbound/sendgrid",
    alias: "receive_sendgrid_inbound_api_inbound_sendgrid_post",
    description: `SendGrid Inbound Parse webhook receiver.

Reads multipart/form-data, normalizes to the internal Postmark-shape
payload, and dispatches via &#x60;_dispatch_inbound_payload&#x60;.

Phase P5.8.1 (2026-02) — gated behind &#x60;INBOUND_PROVIDER&#x60;. Default
is &#x60;sendgrid&#x60; (sole accepting provider); &#x60;postmark&#x60; re-routes
inbound to the legacy endpoint (which itself returns 410 unless
its own retired-flag is lifted); &#x60;both&#x60; accepts here AND on the
legacy endpoint for transition windows.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/inbox/messages/:message_id/preview",
    alias: "preview_source_message_api_inbox_messages__message_id__preview_get",
    description: `Tenant-scoped read-only preview of the inbox message that
seeded a routed item visible to this caller.

Tenant resolution: a message is visible to the caller iff
  • the caller is a superadmin, OR
  • the message&#x27;s &#x60;classification.target_hint.account_id&#x60;
    matches the caller&#x27;s &#x60;account_id&#x60;.

Any other state → 404. We DO NOT 403 on cross-tenant access —
that would leak existence; 404 is the only correct response.`,
    requestFormat: "json",
    parameters: [
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/invitations/:token/accept",
    alias: "accept_invitation_api_invitations__token__accept_post",
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/invitations/by-token/:token",
    alias: "preview_invitation_api_invitations_by_token__token__get",
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/jobs/:job_id",
    alias: "poll_job_api_jobs__job_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "job_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/learn/research",
    alias: "learn_research_api_learn_research_post",
    description: `Synthesise a short governance-framed article on any topic the user asks
about. When &#x60;context_id&#x60; is supplied and the user is a member of that
context, the LLM is asked to weight the piece to that context&#x27;s sector
and jurisdiction — so a Kenyan NED researching &#x27;vendor AI oversight&#x27;
gets CBK-flavoured sources, not generic SEC ones.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: LearnResearchIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/lens/catalog",
    alias: "lens_catalog_api_lens_catalog_get",
    description: `Public-to-authenticated catalog of available lenses.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/llm/quota",
    alias: "quota_api_llm_quota_get",
    description: `Return today&#x27;s deep-tier usage for a surface (or all surfaces).`,
    requestFormat: "json",
    parameters: [
      {
        name: "surface",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/active-context",
    alias: "set_active_context_api_me_active_context_post",
    description: `Validate that the caller has an active membership at
&#x60;context_id&#x60;. On success: write a &#x60;context.switched&#x60; audit row
and return the verbatim memo switch-modal payload. On failure:
&#x60;403 MEMBERSHIP_REVOKED&#x60;.

The server is **stateless** about active context — it does NOT
persist &quot;the user&#x27;s current active context&quot; anywhere. The SPA
holds that state per-tab in &#x60;sessionStorage&#x60; (D-004). This
endpoint is purely a validation + audit + UI-payload step.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ActiveContextIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/boards-to-watch",
    alias: "boards_to_watch_api_me_boards_to_watch_get",
    description: `Rank the user&#x27;s boards by an AI-composite of:
  * 7-day new signals             (weight 0.5)
  * 14-day upcoming briefings     (weight 0.3)
  * Open at-risk tasks            (weight 0.2)

Each component is normalized to [0,1] across the user&#x27;s portfolio
so a single board with 5 signals doesn&#x27;t always win.

Reasons[] surface the dominant contributor in human-readable form.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(10).optional().default(3),
      },
    ],
    response: BoardsToWatchOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/company-home/attention",
    alias: "attention_api_me_company_home_attention_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: z.string().min(4).max(120),
      },
    ],
    response: AttentionOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/company-home/readiness",
    alias: "readiness_api_me_company_home_readiness_get",
    description: `Weighted-average task readiness across open tasks for the
active context. &#x60;state&#x3D;&#x27;active&#x27;&#x60; is the only &quot;open&quot; task state in
this codebase (verified 2026-05-27 — DB distinct produces
[&#x27;active&#x27;,&#x27;closed&#x27;]). Drafts also qualify as open if the team
introduces that state later — &#x60;$nin: [&#x27;closed&#x27;]&#x60; is the future-
safe filter, but for now &#x60;&#x27;active&#x27;&#x60; is exhaustive.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: z.string().min(4).max(120),
      },
    ],
    response: ReadinessOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/company-home/top-signals",
    alias: "top_signals_api_me_company_home_top_signals_get",
    description: `Right-rail Top Signals chip data feed. 60s cache per
(account, context, chip). Severity sort applies on the Pulse
chip; the Monitor + Documents chips have severity&#x3D;null on every
row and fall back to timestamp-desc sort.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: z.string().min(4).max(120),
      },
      {
        name: "chip",
        type: "Query",
        schema: z.string().optional().default("pulse"),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(50).optional().default(10),
      },
    ],
    response: TopSignalsOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/contexts",
    alias: "list_my_contexts_api_me_contexts_get",
    description: `Return ONLY contexts where the caller has an active membership.

Each row carries the per-(user, context) role so the company
switcher can render the role badge (&quot;Ubora · Executive&quot;,
&quot;Mara · NED&quot;). Contexts the user is NOT a member of are not
listed — there is no leakage of context identity.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/copy/:slot",
    alias: "get_user_visible_copy_api_me_copy__slot__get",
    description: `Frontend &#x60;EarlyAccessOptIn&#x60; + day-16 banner read their copy
overrides via this endpoint. Returns &#x60;{slot, fields, values}&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "slot",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/delete-account",
    alias: "request_account_deletion_api_me_delete_account_post",
    description: `Request soft-delete with a 30-day grace window.

The caller MUST submit their own email in &#x60;confirm&#x60; — defensive
second-step to prevent muscle-memory mis-clicks. The endpoint
returns the scheduled hard-delete timestamp so the UI can
display the cooling-off period.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ confirm: z.string() }).passthrough(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/delete-account/cancel",
    alias: "cancel_account_deletion_api_me_delete_account_cancel_post",
    description: `Cancel a pending soft-delete. 400 if the account isn&#x27;t
pending deletion (idempotent caller protection).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/depth-status",
    alias: "get_depth_status_api_me_depth_status_get",
    requestFormat: "json",
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
  },
  {
    method: "post",
    path: "/api/me/depth-status/dismiss",
    alias: "dismiss_offer_api_me_depth_status_dismiss_post",
    description: `Sticky dismissal — flag persists until manually cleared from
&#x60;db.accounts.{id}.depth_offer_dismissed_at&#x60;. For v1 we don&#x27;t re-offer
after dismissal; future work can ratchet the offer on a new threshold
milestone.`,
    requestFormat: "json",
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
  },
  {
    method: "post",
    path: "/api/me/early-access-opt-in",
    alias: "post_early_access_opt_in_api_me_early_access_opt_in_post",
    description: `Record the user&#x27;s early-access opt-in request. Idempotent —
a second submission updates &#x60;note&#x60; + &#x60;updated_at&#x60; but keeps the
original &#x60;requested_at&#x60;. This is the ONLY endpoint a hard-locked
user can hit (besides auth + this status read) until the founder
converts them via the cohort console.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EarlyAccessIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/first-session",
    alias: "get_first_session_api_me_first_session_get",
    requestFormat: "json",
    response: z.union([StateOnlyResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/me/first-session/choose-door",
    alias: "choose_door_api_me_first_session_choose_door_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ door: z.string().min(1).max(16) }).passthrough(),
      },
    ],
    response: z.union([StateOnlyResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/first-session/complete",
    alias: "complete_first_session_api_me_first_session_complete_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CompleteIn,
      },
    ],
    response: z.union([StateOnlyResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/first-session/intake",
    alias: "submit_intake_api_me_first_session_intake_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: IntakeIn,
      },
    ],
    response: z.union([StateOnlyResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/first-session/skip",
    alias: "skip_first_session_api_me_first_session_skip_post",
    requestFormat: "json",
    response: z.union([StateOnlyResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/me/first-session/start",
    alias: "start_first_session_api_me_first_session_start_post",
    requestFormat: "json",
    response: z.union([StateOnlyResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/me/governance",
    alias: "governance_panel_api_me_governance_get",
    requestFormat: "json",
    response: z.union([GovernancePanelResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/me/governance/audit",
    alias: "governance_audit_api_me_governance_audit_get",
    requestFormat: "json",
    parameters: [
      {
        name: "action",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "since",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "until",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(500).optional().default(100),
      },
      {
        name: "cursor",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/governance/audit/export",
    alias: "governance_audit_export_api_me_governance_audit_export_post",
    description: `Zip-streamed CSV of audit entries for the requested filter window.

Mirrors the pattern from &#x60;routers/chat.py#/chats/{id}/audit/export.zip&#x60;
— one-shot, no persistent download URL, auditor ingests the raw bytes.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExportIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/home/stream",
    alias: "aggregated_stream_api_me_home_stream_get",
    description: `Return a merged, weighted stream of recent changes across every
active context the user is a member of. Each item carries
&#x60;context_id&#x60; + &#x60;context_name&#x60; so the UI can render the context badge.

Phase 2b (2026-05-05) — every cross-context row is now projected
through &#x60;services.privacy_wall.project_for_pulse(...)&#x60; so only
metadata-class fields cross the boundary. Content fields (signal
&#x60;headline&#x60;/&#x60;summary&#x60;, boardpack &#x60;commentary&#x60;/&#x60;title&#x60;, document
&#x60;name&#x60;/&#x60;extracted_text&#x60;, inbound subject/sender) are dropped.

Response shape (additive — v1 callers still work):
    {
      &quot;signals&quot;: [...],      # metadata only — id, context_id, status, type, ...
      &quot;briefings&quot;: [...],    # metadata only
      &quot;contexts&quot;: [...],
      &quot;documents&quot;: [...],    # metadata only
      &quot;approvals&quot;: [...],    # metadata only — no headline/subject/sender
      &quot;next_cursor&quot;: str | None,
    }
A &#x60;x-privacy-wall-projected-keys&#x60; debug header lists the union of
keys that survived projection per row-type, so a tester can
verify the wall is in front of this surface. The header is
informational only and slated for removal in Phase 4.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(30),
      },
      {
        name: "cursor",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/inbound-queue/counts",
    alias: "my_inbound_queue_counts_api_me_inbound_queue_counts_get",
    requestFormat: "json",
    response: z.union([ByContextSummaryResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/me/last-action",
    alias: "last_action_api_me_last_action_get",
    description: `Return the user&#x27;s most recent meaningful action across the
app, as the source for the &quot;Where you left off&quot; resume card.

Reads from &#x60;user_recent_views&#x60; (populated by &#x60;POST /api/me/recent-views&#x60;
on most surface mounts). Returns an empty / null shape when no
recent activity exists (frontend renders the empty state).

Phase H.4 (2026-05-27) — When the recent-view row was written
with &#x60;deep_link&#x60;/&#x60;artefact_id&#x60;/&#x60;artefact_kind&#x60; fields, surface
them so the frontend can jump straight into the artefact
(doc/task/chat) instead of bouncing off the surface index.
Legacy rows (pre-H.4 writes) fall back to surface_path
classification, preserving the H.3 contract.`,
    requestFormat: "json",
    response: LastActionOut,
  },
  {
    method: "get",
    path: "/api/me/onboarding-briefs",
    alias: "get_onboarding_briefs_api_me_onboarding_briefs_get",
    description: `Return the onboarding-briefs state + locked slide list.

The modal consumes:
  - &#x60;shown_at: Optional[str]&#x60; — ISO timestamp; null means SHOW THE MODAL.
  - &#x60;slides: List[Slide]&#x60; — 6 slides with founder overrides applied.`,
    requestFormat: "json",
    response: z.union([OnboardingBriefsResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/me/onboarding-briefs/complete",
    alias: "complete_onboarding_briefs_api_me_onboarding_briefs_complete_post",
    description: `Mark the briefs as shown so the modal doesn&#x27;t re-surface.

Idempotent: re-calling stamps a fresh &#x60;shown_at&#x60; but the modal
consumes the FIRST &#x60;shown_at !&#x3D;&#x3D; null&#x60; check and never re-renders
in the same session.`,
    requestFormat: "json",
    response: z.union([OkResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/me/portfolio",
    alias: "me_portfolio_api_me_portfolio_get",
    description: `One row per active membership the calling account holds.`,
    requestFormat: "json",
    response: z.union([ItemsListResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/me/portfolio-metrics",
    alias: "portfolio_metrics_api_me_portfolio_metrics_get",
    description: `Aggregate counts across all the user&#x27;s company contexts.

Signals + briefings are scoped to the last 30 days to keep the
Portfolio Landing surface focused on &quot;what&#x27;s relevant now&quot;.
Documents + companies are all-time totals.`,
    requestFormat: "json",
    response: PortfolioMetricsOut,
  },
  {
    method: "get",
    path: "/api/me/profile",
    alias: "get_my_profile_api_me_profile_get",
    requestFormat: "json",
    response: ProfileOut,
  },
  {
    method: "patch",
    path: "/api/me/profile",
    alias: "patch_my_profile_api_me_profile_patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ProfilePatchIn,
      },
    ],
    response: ProfileOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/questions",
    alias: "my_questions_api_me_questions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "status",
        type: "Query",
        schema: z.string().optional().default("open"),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().optional().default(1),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().optional().default(10),
      },
      {
        name: "asker_role",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "sort",
        type: "Query",
        schema: z.string().optional().default("recent"),
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/recent-views",
    alias: "post_recent_view_api_me_recent_views_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RecentViewIn,
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/recent-views",
    alias: "get_recent_views_api_me_recent_views_get",
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(3),
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/review-queue",
    alias: "list_review_queue_api_me_review_queue_get",
    description: `Aggregate pending items across all of the user&#x27;s contexts.

&#x60;cursor&#x60; is an opaque iso-datetime string — items strictly older
than &#x60;cursor&#x60; are returned. &#x60;limit&#x60; is capped at 100.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(50),
      },
      {
        name: "cursor",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([ItemsListResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/review-queue/counts",
    alias: "review_queue_counts_api_me_review_queue_counts_get",
    requestFormat: "json",
    response: z.union([ByContextSummaryResponse, z.null()]),
  },
  {
    method: "post",
    path: "/api/me/review-queue/items/:kind/:item_id/approve",
    alias:
      "approve_review_item_api_me_review_queue_items__kind___item_id__approve_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema:
          approve_review_item_api_me_review_queue_items__kind___item_id__approve_post_Body,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "item_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/review-queue/items/:kind/:item_id/edit",
    alias:
      "edit_review_item_api_me_review_queue_items__kind___item_id__edit_post",
    description: `Returns a deep-link to the existing edit surface for this kind.
The UI navigates there in-place (or opens it in an overlay).

Phase 15.1: solva_cycle_action accepts an optional body with
&#x60;questions: [...]&#x60; to persist edits and then approve in one step
(per build brief decision #5).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema:
          edit_review_item_api_me_review_queue_items__kind___item_id__edit_post_Body,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "item_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/review-queue/items/:kind/:item_id/reject",
    alias:
      "reject_review_item_api_me_review_queue_items__kind___item_id__reject_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema:
          reject_review_item_api_me_review_queue_items__kind___item_id__reject_post_Body,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "item_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/role-probe",
    alias: "role_probe_api_me_role_probe_get",
    description: `Any-role probe. Returns the active context + role for the
caller after going through the full RBAC pipeline (header read +
membership lookup + audit write). The SPA calls this on boot to
confirm the cached &#x60;X-Active-Context&#x60; is still valid (membership
might have been revoked since the last tab session).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/role-probe/executive",
    alias: "role_probe_executive_api_me_role_probe_executive_get",
    description: `Executive-only probe. Used by Phase A acceptance #5. NEDs
hitting this with their NED-context header in the active slot
should receive &#x60;403 ROLE_FORBIDDEN&#x60;.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/role-probe/ned",
    alias: "role_probe_ned_api_me_role_probe_ned_get",
    description: `NED-only probe. Mirror of the executive one. Useful for the
contrapositive test (executive at A, switching to NED at B,
confirming B&#x27;s NED role grants this endpoint).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/shares/inbox",
    alias: "shares_inbox_api_me_shares_inbox_get",
    requestFormat: "json",
    parameters: [
      {
        name: "include_revoked",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
    ],
    response: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/shares/outbox",
    alias: "shares_outbox_api_me_shares_outbox_get",
    requestFormat: "json",
    parameters: [
      {
        name: "include_revoked",
        type: "Query",
        schema: z.boolean().optional().default(true),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(100),
      },
    ],
    response: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/me/special-ask",
    alias: "get_my_special_ask_api_me_special_ask_get",
    description: `Return the user&#x27;s special-ask row (if any) + the founder-saved
&#x60;special_ask&#x60; copy slot overrides (or defaults). Frontend modal
reads this on first mount of the trigger.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/me/special-ask",
    alias: "put_my_special_ask_api_me_special_ask_post",
    description: `Persist the user&#x27;s submission. Status flips to &#x60;complete&#x60; only
when referral_name + referral_email are both filled; otherwise
&#x60;partial&#x60; (any other field filled) or &#x60;pending&#x60; (nothing).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SpecialAskIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/me/special-ask/dismiss",
    alias: "dismiss_my_special_ask_api_me_special_ask_dismiss_post",
    description: `&#x60;Remind me later&#x60; action. Does NOT change the row&#x27;s status —
the modal will re-surface on the next session because the row
stays &#x60;pending&#x60;. Just emits the &#x60;special_ask.dismissed&#x60; event so
the cohort console can show &quot;asked but dismissed&quot; patterns.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/me/special-ask/surface-ack",
    alias: "ack_my_special_ask_surfaced_api_me_special_ask_surface_ack_post",
    description: `Frontend pings this on modal mount so the funnel records the
surfacing event exactly once per session.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/submitted-briefs",
    alias: "my_submitted_briefs_api_me_submitted_briefs_get",
    description: `List briefs I have submitted for board reporting, with a rollup
of assignment statuses for each. Used by the submitter inbox view.`,
    requestFormat: "json",
    response: z.union([BriefsCountResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/me/trial-status",
    alias: "get_my_trial_status_api_me_trial_status_get",
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/me/trial-status/by-account/:account_id",
    alias:
      "admin_get_trial_status_api_me_trial_status_by_account__account_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ned/assignments/:assignment_id/accept",
    alias: "accept_assignment_api_ned_assignments__assignment_id__accept_post",
    description: `Idempotent accept. Privacy-Wall-enforced ingest into NED record.

Concretely: ONLY the Brief artefact (resolved via brief_id) lands
in the NED&#x27;s durable record. NO Exec-internal fields cross the wall
here — we never read from db.cycle_agendas, db.cycle_contributions,
db.cycle_team, db.cycle_followups.`,
    requestFormat: "json",
    parameters: [
      {
        name: "assignment_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: AcceptOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ned/assignments/:assignment_id/decline",
    alias:
      "decline_assignment_api_ned_assignments__assignment_id__decline_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DeclineIn,
      },
      {
        name: "assignment_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/ned/committee/:context_id/:committee",
    alias:
      "committee_through_line_api_ned_committee__context_id___committee__get",
    description: `Returns reverse-chrono meetings + decisions + positions across the
NED&#x27;s tenure on this (context, committee) — STRICTLY scoped by
account_id. The NED sees only their own engagement.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "committee",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/ned/inbox/assignments",
    alias: "ned_inbox_api_ned_inbox_assignments_get",
    description: `Pending + accepted + declined assignments for the authenticated
NED. Strict field whitelist; no Exec-internal payload.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ned/landing",
    alias: "ned_landing_api_ned_landing_get",
    description: `Cross-board landing per spec §4.

Returns four sections:
  • this_week — meetings within the next 7 days
  • next_two_weeks — meetings days 7-21 ahead
  • outstanding — open follow-ups + unanswered questions, all boards
  • patterns_url — pointer to the active context&#x27;s E.0.3 aggregator
    endpoint (the landing renders patterns from there client-side
    with the active context as scope)`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/ned/meetings",
    alias: "create_meeting_api_ned_meetings_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MeetingCreate,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/ned/meetings/:meeting_id",
    alias: "get_meeting_api_ned_meetings__meeting_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/ned/meetings/:meeting_id",
    alias: "patch_meeting_api_ned_meetings__meeting_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MeetingPatch,
      },
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/ned/meetings/:meeting_id",
    alias: "delete_meeting_api_ned_meetings__meeting_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ned/meetings/:meeting_id/followups",
    alias: "draft_followup_api_ned_meetings__meeting_id__followups_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FollowupDraft,
      },
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ned/meetings/:meeting_id/followups/:fid/send",
    alias: "ned_cycle_send_followup",
    description: `Reuse Phase D.2 email infrastructure with a NED posture (peer-toned
&#x27;From &lt;NED Name&gt; via Akki&#x27;). The send path mirrors &#x60;cycle_manager.py&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "fid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ned/meetings/:meeting_id/notes",
    alias: "add_note_api_ned_meetings__meeting_id__notes_post",
    description: `In-phase note insert. SPEC §5.2.1: no real-time AI, no transcription.
This endpoint MUST NOT call any LLM. Pure DB insert. The marker comment
below is a build-time guardrail — do not add LLM calls here.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: NoteCreate,
      },
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/ned/meetings/:meeting_id/notes/:note_id",
    alias: "delete_note_api_ned_meetings__meeting_id__notes__note_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "note_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/ned/meetings/:meeting_id/positions",
    alias: "register_position_api_ned_meetings__meeting_id__positions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PositionCreate,
      },
      {
        name: "meeting_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/ned/search",
    alias: "personal_memory_search_api_ned_search_get",
    description: `Cross-board search across the NED&#x27;s OWN meetings/notes/positions/
followups. STRICTLY scoped by account_id — never queries other NEDs
or other accounts. Privacy Wall holds by construction (account_id
filter on every query).`,
    requestFormat: "json",
    parameters: [
      {
        name: "q",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().optional().default(25),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/news",
    alias: "get_news_api_news_get",
    description: `Return curated news items, diversified by source, region-filtered.

The aggregator (services/news_aggregator.py) populates &#x60;news_items&#x60;
every ~30 min via an asyncio task started at app boot. If the
collection is empty (cold start), this endpoint returns
&#x60;{items: [], total: 0}&#x60; — the frontend renders an editorial
fallback line.`,
    requestFormat: "json",
    parameters: [
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(50).optional().default(10),
      },
      {
        name: "since",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "source",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "region",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "diversify",
        type: "Query",
        schema: z.boolean().optional().default(true),
      },
      {
        name: "include_all_regions",
        type: "Query",
        schema: z.boolean().optional().default(false),
      },
      {
        name: "quality",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "Accept-Language",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: NewsFeedOut,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/notify-billing-launch",
    alias: "notify_billing_launch_api_notify_billing_launch_post",
    description: `Records the authenticated account&#x27;s interest in being notified
when billing actually ships. Idempotent — second POST does NOT
duplicate the row; instead the &#x60;&#x60;already_subscribed&#x60;&#x60; flag is set.

The Mongo collection &#x60;&#x60;billing_launch_interest&#x60;&#x60; carries:
    - account_id   : the user&#x27;s account id
    - account_email: cached email at signup time (audit only)
    - subscribed_at: ISO UTC timestamp of first subscription
    - source       : &quot;notify_billing_launch&quot; (literal, future-
                     proof if we ever add other notify-me funnels)`,
    requestFormat: "json",
    response: NotifyOut,
  },
  {
    method: "get",
    path: "/api/oauth/google/callback",
    alias: "oauth_google_callback_api_oauth_google_callback_get",
    description: `Stage-2 of the OAuth dance — Google redirected back. We exchange
the auth code for tokens, persist them encrypted, then HTTP-302 the
user to the Events page with a success flag.`,
    requestFormat: "json",
    parameters: [
      {
        name: "code",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "state",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "error",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/oauth/google/connect",
    alias: "oauth_google_connect_api_oauth_google_connect_get",
    description: `Stage-1 of the OAuth dance — returns the Google consent URL. The
frontend redirects the user there; Google bounces back to the
callback endpoint below.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.object({ authorize_url: z.string() }).passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/observability/reasoning_velocity",
    alias: "reasoning_velocity_api_observability_reasoning_velocity_get",
    requestFormat: "json",
    parameters: [
      {
        name: "window",
        type: "Query",
        schema: z
          .string()
          .regex(/^(7d|30d)$/)
          .optional()
          .default("7d"),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/prepare/brief-kinds",
    alias: "list_brief_kinds_api_prepare_brief_kinds_get",
    description: `Static list of brief kinds — used to populate the kind picker
on /app/prepare. Open to any authenticated request.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/presets/industries",
    alias: "list_industries_api_presets_industries_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/presets/jurisdictions",
    alias: "list_jurisdictions_api_presets_jurisdictions_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/product-features",
    alias: "product_features_inline_api_product_features_get",
    description: `Return markdown inline (browser will preview as text).`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/product-features.md",
    alias: "product_features_download_api_product_features_md_get",
    description: `Return markdown as a download (Content-Disposition: attachment).`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/public/observability/reasoning_velocity",
    alias:
      "public_reasoning_velocity_api_public_observability_reasoning_velocity_get",
    requestFormat: "json",
    parameters: [
      {
        name: "window",
        type: "Query",
        schema: z.string().regex(/^30d$/).optional().default("30d"),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/public/studio/read/:token",
    alias: "public_read_share_api_public_studio_read__token__get",
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/public/studio/sensitivity-demo",
    alias: "public_sensitivity_demo_api_public_studio_sensitivity_demo_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ text: z.string().min(4).max(4000) }).passthrough(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/public/studio/track/:token",
    alias: "public_track_share_api_public_studio_track__token__get",
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/reports/inbox",
    alias: "reports_inbox_api_reports_inbox_get",
    description: `Cross-context: every report in the platform where this user is the
current pending reviewer. Powers the &#x27;awaiting your review&#x27; Home card.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/respond/:token",
    alias: "get_checklist_for_token_api_respond__token__get",
    description: `Public — reportee fetches their own checklist via emailed link.`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/respond/:token",
    alias: "submit_response_api_respond__token__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SubmissionIn,
      },
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox-gen/sessions",
    alias: "post_session_api_sandbox_gen_sessions_post",
    description: `Create a sandbox session and enqueue the generation job.
Returns immediately with &#x60;{session_id, status}&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FormPayload,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox-gen/sessions/:sid",
    alias: "sandbox_gen_get_session",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/sandbox-gen/sessions/:sid",
    alias: "delete_session_api_sandbox_gen_sessions__sid__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/cleanup/expired",
    alias: "cleanup_expired_sandboxes_api_sandbox_cleanup_expired_post",
    description: `Sweep sandboxes past &#x60;hard_delete_at&#x60;. Gated by an &#x60;X-Cron-Secret&#x60;
header that matches the &#x60;AKKI_CRON_SECRET&#x60; env var (shared with the
scheduled-job runner). Anonymous callers are rejected.

If &#x60;AKKI_CRON_SECRET&#x60; is unset in the environment we fail closed — the
endpoint returns 503 so a misconfigured deploy can&#x27;t be abused.`,
    requestFormat: "json",
    parameters: [
      {
        name: "X-Cron-Secret",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/contexts/:context_id/capture-email",
    alias: "capture_email_api_sandbox_contexts__context_id__capture_email_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ email: z.string().email() }).passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/contexts/:context_id/objective-check",
    alias:
      "get_objective_check_api_sandbox_contexts__context_id__objective_check_get",
    description: `Frontend hits this on home load. Returns whether the follow-up should
be shown (eligible&#x3D;True only when ≥24h after generation, an objective
was captured, and the user hasn&#x27;t already answered or dismissed).`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/contexts/:context_id/objective-check",
    alias:
      "answer_objective_check_api_sandbox_contexts__context_id__objective_check_post",
    description: `Persist the user&#x27;s answer. &#x60;skip&#x60; flips dismissed&#x3D;True so we never
re-show; yes/partial/no record the answer + optional free-text note.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ObjectiveCheckAnswerIn,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/contexts/:context_id/sample-doc",
    alias:
      "sandbox_sample_doc_api_sandbox_contexts__context_id__sample_doc_get",
    description: `Return a tailored sample document the prospect can accept-upload.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/contexts/:context_id/sample-doc/accept",
    alias:
      "sandbox_sample_doc_accept_api_sandbox_contexts__context_id__sample_doc_accept_post",
    description: `Materialise the sample as a real document in the sandbox context.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SandboxSampleAccept,
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/contexts/:context_id/tutorial",
    alias: "sandbox_tutorial_api_sandbox_contexts__context_id__tutorial_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/contexts/:context_id/tutorial/dismiss",
    alias:
      "dismiss_tutorial_api_sandbox_contexts__context_id__tutorial_dismiss_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ dismissed: z.boolean().default(true) })
          .partial()
          .passthrough(),
      },
      {
        name: "context_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/contexts/seeded",
    alias: "create_seeded_context_api_sandbox_contexts_seeded_post",
    description: `Create a real (non-sandbox) context for the authenticated user, then
optionally seed it with the same sector-template artefacts the public
sandbox uses. Returns the new context id so the frontend can switch into it.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SeededContextIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/convert",
    alias: "convert_sandbox_api_sandbox_convert_post",
    description: `Migrate the caller&#x27;s sandbox account into a real, persistent account.

After conversion:
  · Disposable email is rewritten to the real one + password updated.
  · The &#x60;is_sandbox&#x60; flag and sandbox_session_id are stripped from account.
  · Each of the user&#x27;s sandbox-typed contexts is flipped to a real type
    (ned_personal / executive_personal based on the membership role),
    &#x60;sandbox_metadata.converted_at&#x60; is stamped, and expires_at /
    read_only_until / hard_delete_at are cleared so the sweeper skips it.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SandboxConvertIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/generate",
    alias: "start_generation_api_sandbox_generate_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SandboxIntakeIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/generate/:session_id/status",
    alias: "generation_status_api_sandbox_generate__session_id__status_get",
    requestFormat: "json",
    parameters: [
      {
        name: "session_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/templates",
    alias: "list_templates_api_sandbox_templates_get",
    description: `Surface which sectors have polished templates vs fall back to generic.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/sandbox/v2/sessions",
    alias: "sandbox_v2_create_session_api_sandbox_v2_sessions_post",
    description: `Create the Sandbox v2 session AND mint a disposable account + JWT
so the visitor can call the (auth-gated) Solva v2 endpoints in Step 1
without ever signing up.

The disposable account is flagged &#x60;&#x60;is_sandbox&#x3D;True&#x60;&#x60; and tied to the
sandbox v2 session id via &#x60;&#x60;sandbox_v2_session_id&#x60;&#x60;. It does not get a
Mongo &#x60;contexts&#x60; row (Sandbox v2 doesn&#x27;t seed a workspace; Step 1 uses
the unattached Solva flow with &#x60;&#x60;context_id&#x3D;None&#x60;&#x60;). The TTL on
&#x60;&#x60;sandbox_v2_sessions.expires_at&#x60;&#x60; (7 days) is the only thing keeping
the session alive for resume.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SandboxV2WelcomeIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid",
    alias: "sandbox_v2_get_session_api_sandbox_v2_sessions__sid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/sandbox/v2/sessions/:sid",
    alias: "sandbox_v2_patch_session_api_sandbox_v2_sessions__sid__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SandboxV2PatchIn,
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid/composed-draft",
    alias:
      "sandbox_v2_composed_draft_api_sandbox_v2_sessions__sid__composed_draft_get",
    description: `Step 3 — the verbatim 4-paragraph composed draft for the user&#x27;s
routed (role, org_type).`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid/cycle-snapshot",
    alias:
      "sandbox_v2_cycle_snapshot_api_sandbox_v2_sessions__sid__cycle_snapshot_get",
    description: `Step 4 read-only Cycle Manager snapshot (brief §7).`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/v2/sessions/:sid/exit",
    alias: "sandbox_v2_exit_session_api_sandbox_v2_sessions__sid__exit_post",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid/fallback-situation",
    alias:
      "sandbox_v2_fallback_situation_api_sandbox_v2_sessions__sid__fallback_situation_get",
    description: `Empty-framing fallback (brief §4.5).`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid/opening-question",
    alias:
      "sandbox_v2_opening_question_api_sandbox_v2_sessions__sid__opening_question_get",
    description: `Return a calibrated Solva opening question for the visitor (Step 1).`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid/pulse-signals",
    alias:
      "sandbox_v2_pulse_signals_api_sandbox_v2_sessions__sid__pulse_signals_get",
    description: `Step 2 Pulse signals — content ingested now per Phase D.2&#x27;s
forthcoming UI. Pack §&quot;Inter-connection within a context&quot;: signals&#x27;
citations resolve to Step 3 source documents.`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/v2/sessions/:sid/save-and-send",
    alias:
      "sandbox_v2_save_and_send_api_sandbox_v2_sessions__sid__save_and_send_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ email: z.string().email() }).passthrough(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/sandbox/v2/sessions/:sid/studio-sources",
    alias:
      "sandbox_v2_studio_sources_api_sandbox_v2_sessions__sid__studio_sources_get",
    description: `Pre-loaded Step 3 source-material chips.`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/sandbox/v2/sessions/:sid/studio/add-sentence",
    alias:
      "sandbox_v2_add_sentence_api_sandbox_v2_sessions__sid__studio_add_sentence_post",
    description: `Accept the user-typed sentence iff its tokens overlap with the
keywords of any loaded source chip; refuse otherwise.

Refusal voice is per-context: the Bank context uses the pack&#x27;s
verbatim refusal copy; other contexts use the same FT cadence
parameterised in &#x60;sandbox_v2_corpus.pick_provenance_refusal&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ sentence: z.string().min(2).max(400) })
          .passthrough(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/search",
    alias: "federated_search_api_search_get",
    requestFormat: "json",
    parameters: [
      {
        name: "q",
        type: "Query",
        schema: z.string().min(2).max(200),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(25),
      },
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "surface",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).lte(10000).optional().default(0),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/search/cross-context-open",
    alias: "cross_context_open_api_search_cross_context_open_post",
    description: `Write an audit row immediately BEFORE the SPA performs a
cross-context switch-and-open from a search result.

The actual context switch is still performed by the existing
POST /api/me/active-context endpoint; this endpoint exists only to
record the cross-context-open event with both context_ids and the
surface/result_id pair.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/shares/:share_id",
    alias: "get_share_api_shares__share_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "share_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/shares/:share_id",
    alias: "revoke_share_api_shares__share_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "share_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/briefing/state",
    alias: "get_state_api_solva_briefing_state_get",
    description: `Return current visit_count + suppressed for (user, area).

Side-effect-free; safe to call on every deck render.`,
    requestFormat: "json",
    parameters: [
      {
        name: "area",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/briefing/state",
    alias: "mutate_state_api_solva_briefing_state_post",
    description: `Mutate (user, area) state. Idempotent within a single deck open
only for &#x60;suppress&#x60; / &#x60;unsuppress&#x60;; &#x60;increment&#x60; always bumps.

Returns the post-mutation snapshot in the same shape as
GET /state so the frontend can short-circuit without re-fetching.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _PostBody,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/sessions/:sid/v2/chair_notes",
    alias: "get_v2_chair_notes_api_solva_sessions__sid__v2_chair_notes_get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/sessions/:sid/v2/export.pptx",
    alias: "export_v2_pptx_api_solva_sessions__sid__v2_export_pptx_get",
    description: `Stream a native .pptx file rendered from the 16-element
artefact schema.

Auth + feature-flag gates mirror &#x60;/v2/payload&#x60; exactly. On every
successful export, write a &#x60;solva_v2_pptx_export&#x60; row to
&#x60;db.audit_log&#x60; carrying session id + account id + slide count.`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/sessions/:sid/v2/payload",
    alias: "get_v2_artefact_payload_api_solva_sessions__sid__v2_payload_get",
    description: `Return the Slice 1 &#x60;ArtefactPayload&#x60; for this session as JSON.

Gates:
  • Session must exist + belong to the authenticated account
  • Feature flag must be ON for this account (or globally via env)
  • All 4 integrity validators must pass; if not, HTTP 422 with
    offender list

Response shape:
  {
    &quot;schema_version&quot;: &quot;solva.v2.artefact.1.0&quot;,
    &quot;session_id&quot;: &quot;...&quot;,
    &quot;payload&quot;: &lt;ArtefactPayload as JSON&gt;,
    &quot;validator_passes&quot;: true,
  }`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/sessions/:sid/v2/stream",
    alias: "stream_v2_reasoning_api_solva_sessions__sid__v2_stream_get",
    description: `Server-Sent-Events stream of Solva&#x27;s 5-layer reasoning pass.

For complete sessions, replays the deterministic synthesized event
sequence in a 4-second rapid-burst so the founder gets the visceral
&quot;watch it think&quot; experience whenever they open the artefact.

For in-flight sessions (status !&#x3D; &quot;completed&quot;), the stream returns
only the events that have happened so far + closes — live-mode
instrumentation lands in Slice 3a.next when the 5-layer engine
pipeline is wired to a per-session asyncio.Queue. Today the engines
write to the audit log synchronously inside their long-op endpoints,
so a parallel stream would need a refactor that&#x27;s outside the
Slice 3a scope.

Wire format (one SSE event per emitted SolvaStreamEvent):
    event: solva.reasoning
    data:  &lt;SolvaStreamEvent JSON&gt;

Closes with:
    event: complete
    data:  {&quot;total_events&quot;: N}`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/cron/stale-session-sweep",
    alias: "stale_session_sweep_api_solva_v2_cron_stale_session_sweep_post",
    requestFormat: "json",
    parameters: [
      {
        name: "X-Cron-Secret",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/intent/classify",
    alias: "classify_intent_api_solva_v2_intent_classify_post",
    description: `Phase 15.2 — soft-suggest the most-fitting sub-module for a user&#x27;s
intent. Single tier&#x3D;fast LLM call. Returns
    {submodule: &lt;one of 4&gt;, confidence: 0.0-1.0, reason: str}
Front-end shows the chip when confidence &gt;&#x3D; 0.6 and hides otherwise.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ intent: z.string().min(20).max(1200) })
          .passthrough(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/seed",
    alias: "fetch_take_to_solva_seed_api_solva_v2_seed_get",
    requestFormat: "json",
    parameters: [
      {
        name: "kind",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "id",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions",
    alias: "start_session_api_solva_v2_sessions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: StartV2In,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions",
    alias: "list_sessions_api_solva_v2_sessions_get",
    description: `List sessions for the caller, **strictly scoped to one workspace context**.

Privacy fix (WS-R16, 2026-05-13) — &#x60;context_id&#x60; is now a REQUIRED
query parameter. Previously this endpoint filtered by &#x60;account_id&#x60;
only, which meant a user with active memberships in multiple
workspaces (companies / boards) saw Solva sessions from ALL of their
contexts mixed together. Concretely, the Generate-Brief-from-Solva
picker (&#x60;components/studio/SourceStep.jsx&#x60;) surfaced sessions from
every context the user had ever logged into, not the workspace they
were currently in. That is a data-segregation violation.

Defense-in-depth applied here:
  1. &#x60;context_id&#x60; is required (FastAPI raises 422 if missing).
  2. The caller must have an **active membership** in &#x60;context_id&#x60;.
     A 403 is returned if not — protects against a user passing
     a workspace id they&#x27;re not a member of.
  3. The Mongo find filter combines &#x60;account_id&#x60; AND &#x60;context_id&#x60;.
     Belt-and-braces — even if membership lookup is bypassed by a
     future bug, the data filter still scopes correctly.
  4. Sessions whose stored &#x60;context_id&#x60; is null / missing are
     **excluded** from the response (legacy/orphan data — see
     SYSTEM_STATE §7 entry for the follow-up cleanup task).

Wave 3.3 (UAT pack) — &#x60;q&#x60; substring filter against &#x60;intent&#x60;
(case-insensitive) is preserved.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "status",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "q",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid",
    alias: "get_session_api_solva_v2_sessions__sid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/abandon",
    alias: "abandon_session_api_solva_v2_sessions__sid__abandon_post",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid/artefact-reasoning",
    alias:
      "artefact_reasoning_api_solva_v2_sessions__sid__artefact_reasoning_get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/attach-document",
    alias:
      "attach_session_document_api_solva_v2_sessions__sid__attach_document_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ document_id: z.string().min(1).max(120) })
          .passthrough(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/solva/v2/sessions/:sid/attached-documents/:document_id",
    alias:
      "detach_session_document_api_solva_v2_sessions__sid__attached_documents__document_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "document_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/continue-chat",
    alias:
      "solva_continue_in_chat_api_solva_v2_sessions__sid__continue_chat_post",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid/export.docx",
    alias: "export_session_docx_api_solva_v2_sessions__sid__export_docx_get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid/export.pdf",
    alias: "export_session_pdf_api_solva_v2_sessions__sid__export_pdf_get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/fork",
    alias: "fork_session_api_solva_v2_sessions__sid__fork_post",
    description: `Phase 15.2 — fork a session into a new sub-module.

Inherits intent + accumulated user turns from the parent. Sets
parent_session_id on the child so the lineage is auditable. Starts at
framing layer with status&#x3D;active. Does NOT abandon the parent — the
user can keep walking the parent if they want to.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ForkV2In,
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/frame-audit",
    alias: "run_frame_audit_api_solva_v2_sessions__sid__frame_audit_post",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "stream",
        type: "Query",
        schema: z.number().int().optional().default(0),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/frame-audit-decision",
    alias:
      "frame_audit_decision_api_solva_v2_sessions__sid__frame_audit_decision_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ decision: z.string().regex(/^(proceed|get_more|pause)$/) })
          .passthrough(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/handoff/cycle",
    alias:
      "handoff_cycle_via_review_api_solva_v2_sessions__sid__handoff_cycle_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: HandoffCycleIn,
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid/reasoning-log",
    alias: "get_reasoning_log_api_solva_v2_sessions__sid__reasoning_log_get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid/reasoning-log/summary",
    alias:
      "reasoning_log_summary_api_solva_v2_sessions__sid__reasoning_log_summary_get",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/solva/v2/sessions/:sid/synisense-breakdown",
    alias:
      "get_synisense_breakdown_api_solva_v2_sessions__sid__synisense_breakdown_get",
    description: `SOLVA sprint (2026-05-12) — per-section Synisense breakdown.

Returns the total identifier count + three-layer breakdown grouped
by Solva reasoning surface (framing / grounding / hypothesis /
synthesis / reflection). Powers the per-section badge on the
artefact UI.

Filter is on (session_id, surface) which is reliable once the
pipeline started threading session_id forward (SOLVA sprint).
Older sessions that pre-date the threading return an empty list —
the UI degrades gracefully to &quot;—&quot; badges. We also accept the
surface-by-time-window approximation for that historical bucket by
reading the session&#x27;s account_id + creation/update window.`,
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/take-to-cycle",
    alias: "take_to_cycle_api_solva_v2_sessions__sid__take_to_cycle_post",
    requestFormat: "json",
    parameters: [
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/turn",
    alias: "post_turn_api_solva_v2_sessions__sid__turn_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ user_text: z.string().min(2).max(4000) })
          .passthrough(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/solva/v2/sessions/:sid/turn/stream",
    alias:
      "solva_synthesis_stream_api_solva_v2_sessions__sid__turn_stream_post",
    description: `SSE-wrap of the synchronous Solva session-turn handler.

Phases (6): Reading the layer ingest → Checking the grounding
contract → Weighing the probability rail → Composing → Validating
→ Almost there.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
      {
        name: "sid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/approve",
    alias: "approve_composed_api_studio__kind___artefact_id__approve_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: routers__studio_blocks__ApproveIn,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/studio/:kind/:artefact_id/blocks",
    alias: "list_blocks_api_studio__kind___artefact_id__blocks_get",
    requestFormat: "json",
    parameters: [
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/blocks",
    alias: "create_block_api_studio__kind___artefact_id__blocks_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BlockCreateIn,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/studio/:kind/:artefact_id/blocks/:block_id",
    alias:
      "patch_block_api_studio__kind___artefact_id__blocks__block_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ content: z.object({}).partial().passthrough() })
          .passthrough(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "block_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/api/studio/:kind/:artefact_id/blocks/:block_id",
    alias:
      "delete_block_api_studio__kind___artefact_id__blocks__block_id__delete",
    requestFormat: "json",
    parameters: [
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "block_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/blocks/:block_id/move",
    alias:
      "move_block_api_studio__kind___artefact_id__blocks__block_id__move_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ to_order: z.number().int().gte(0) }).passthrough(),
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "block_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/blocks/reorder",
    alias: "reorder_blocks_api_studio__kind___artefact_id__blocks_reorder_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ReorderIn,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/studio/:kind/:artefact_id/lifecycle",
    alias: "get_lifecycle_api_studio__kind___artefact_id__lifecycle_get",
    requestFormat: "json",
    parameters: [
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/send",
    alias: "send_composed_api_studio__kind___artefact_id__send_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SendIn,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/submit-review",
    alias:
      "submit_for_review_api_studio__kind___artefact_id__submit_review_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SubmitReviewIn,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/synisense-accept",
    alias:
      "accept_synisense_preview_api_studio__kind___artefact_id__synisense_accept_post",
    description: `Persist the user&#x27;s first-save acceptance of the Synisense
preview. After this call, subsequent saves redact silently and the
PreviewDrawer only reopens when *new* entity types are detected
(see &#x60;synisense_drawer_reopen&#x60; on &#x60;_persist_and_project&#x60;).

The accept is a state-transition only — the redacted projection
has already been persisted by the most recent save. We mark the
transition timestamp and snapshot the entity histogram the user
accepted so we know what &#x27;new sensitive content&#x27; means next time.`,
    requestFormat: "json",
    parameters: [
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/studio/:kind/:artefact_id/upload-image",
    alias: "upload_image_api_studio__kind___artefact_id__upload_image_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ImageUploadIn,
      },
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/synisense/dryrun",
    alias: "synisense_dryrun_api_synisense_dryrun_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DryrunIn,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/synisense/status",
    alias: "get_synisense_status_api_synisense_status_get",
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/tasks",
    alias: "create_task_api_tasks_post",
    description: `Create a task (state&#x3D;draft or state&#x3D;active). Active tasks fire
the contributor-added audit row per team member.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _TaskIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks",
    alias: "list_tasks_api_tasks_get",
    description: `List tasks scoped to the caller. Filter by state (Active /
Draft / Closed) — used by the 3-tab listing surface.

Phase P5.17 (2026-02) — added &#x60;?origin&#x3D;email_akki|manual&#x60; filter.
&#x60;email_akki&#x60; narrows to tasks that carry the P5.17 origin
envelope with &#x60;source &#x3D;&#x3D; &quot;email_akki&quot;&#x60;; &#x60;manual&#x60; excludes those.
Default (no &#x60;origin&#x60; query) → returns everything.`,
    requestFormat: "json",
    parameters: [
      {
        name: "state",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "origin",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/:task_id",
    alias: "get_task_api_tasks__task_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/tasks/:task_id",
    alias: "patch_task_api_tasks__task_id__patch",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _TaskPatch,
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/:task_id/compile",
    alias: "get_compile_state_api_tasks__task_id__compile_get",
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/circulation/close",
    alias:
      "close_compile_circulation_api_tasks__task_id__compile_circulation_close_post",
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/circulation/send",
    alias:
      "send_compile_circulation_api_tasks__task_id__compile_circulation_send_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _CirculationSendIn,
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/commit",
    alias: "commit_compile_api_tasks__task_id__compile_commit_post",
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/draft",
    alias: "start_compile_drafting_api_tasks__task_id__compile_draft_post",
    description: `Kicks off Stage 1 (Drafting). Synchronous if the output_spec is
single-section; runs in the background for multi-section packs.`,
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/final-production/apply-comment",
    alias:
      "apply_final_comment_api_tasks__task_id__compile_final_production_apply_comment_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ApplyCommentIn,
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/final-production/complete",
    alias:
      "complete_final_production_stage_api_tasks__task_id__compile_final_production_complete_post",
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/compile/review/complete",
    alias:
      "complete_review_stage_api_tasks__task_id__compile_review_complete_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ skip_circulation: z.boolean().default(false) })
          .partial()
          .passthrough(),
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/tasks/:task_id/contributions/:contributor_id",
    alias:
      "patch_contribution_api_tasks__task_id__contributions__contributor_id__patch",
    description: `Update a single contributor row&#x27;s status. Status changes trigger
a readiness recompute + audit row. Notifications fire on
approve / request-revision when contribution_mode is &#x60;akki_account&#x60;
or &#x60;email_reply&#x60; (live email send is wired in F.5; today we write
the audit row as the durable record).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ContributionPatchIn,
      },
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "contributor_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([TaskHashResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/contributors/:contributor_id/reinvite",
    alias:
      "reinvite_contributor_api_tasks__task_id__contributors__contributor_id__reinvite_post",
    description: `Re-fire the invitation email for one contributor. Rotates the
magic-link token if applicable (revokes the previous one so old
links go dead).`,
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "contributor_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/:task_id/drafts",
    alias: "list_task_drafts_api_tasks__task_id__drafts_get",
    description: `Documents linked to this task (via &#x60;documents.task_id&#x60;).
Returns both Akki-generated drafts AND contributor uploads.`,
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([
      z.array(z.object({}).partial().passthrough()),
      z.null(),
    ]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/:task_id/intelligence",
    alias: "get_task_intelligence_api_tasks__task_id__intelligence_get",
    description: `Returns the cached intelligence row keyed by (task_id, task_hash).
Cache MISS → returns {status: &quot;pending&quot;} and triggers a synchronous
build (small enough to run inline; LLM Recommendations are best-
effort with rule-based fallback).`,
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:task_id/intelligence/regenerate",
    alias:
      "regenerate_task_intelligence_api_tasks__task_id__intelligence_regenerate_post",
    description: `Force a fresh build. Drops the cache row for the current task_hash
and triggers a background rebuild. Returns {status:&quot;queued&quot;}; the
UI polls /intelligence to pick up the new payload.`,
    requestFormat: "json",
    parameters: [
      {
        name: "task_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([TaskHashResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:tid/close",
    alias: "close_task_api_tasks__tid__close_post",
    description: `Flip an Active task to Closed. Idempotent. Audit-logged.`,
    requestFormat: "json",
    parameters: [
      {
        name: "tid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/:tid/commission",
    alias: "commission_task_api_tasks__tid__commission_post",
    description: `Flip a Draft task to Active. Idempotent. Audit-logged.`,
    requestFormat: "json",
    parameters: [
      {
        name: "tid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/agent-prefill",
    alias: "agent_prefill_api_tasks_agent_prefill_post",
    description: `Agent pre-fill for the wizard&#x27;s Step 1. Returns suggested
&#x60;{objective, success_criteria, source}&#x60; strings. Source is
&#x60;&quot;template&quot;&#x60; (static shelf hit) or &#x60;&quot;llm&quot;&#x60; (Shield-bounded
rewrite) or &#x60;&quot;none&quot;&#x60; (no match + LLM failure).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ name: z.string().min(1).max(200) }).passthrough(),
      },
    ],
    response: z.union([ObjectiveSourceResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/circulation/:token",
    alias: "circulation_view_api_tasks_circulation__token__get",
    description: `Public — no auth. Magic-link token is the only credential.`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([TaskCirculationResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/circulation/:token/comment",
    alias: "circulation_comment_api_tasks_circulation__token__comment_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _CirculationCommentIn,
      },
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/contribute/:token",
    alias: "contributor_view_api_tasks_contribute__token__get",
    description: `Public — no auth header. Magic-link token IS the credential.
Returns task summary + this contributor&#x27;s specific contribution
+ peers (names + roles only, no emails) + docs already uploaded
under this token.`,
    requestFormat: "json",
    parameters: [
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([TaskContributeResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/contribute/:token/comment",
    alias: "contributor_comment_api_tasks_contribute__token__comment_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z
          .object({ comment: z.string().min(1).max(4000) })
          .passthrough(),
      },
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/contribute/:token/submit",
    alias: "contributor_submit_api_tasks_contribute__token__submit_post",
    description: `Flip the contributor&#x27;s status to &#x60;submitted&#x60; + fire audit.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: _ContributorSubmitIn,
      },
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/tasks/contribute/:token/upload",
    alias: "contributor_upload_api_tasks_contribute__token__upload_post",
    description: `Accepts a file upload from a magic-link contributor. Creates a
document row with &#x60;task_id&#x60; + &#x60;contributor_token&#x60; set + &#x60;origin&#x3D;
&quot;magic_link&quot;&#x60;.`,
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema:
          Body_contributor_upload_api_tasks_contribute__token__upload_post,
      },
      {
        name: "token",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([OkResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/tasks/counts",
    alias: "tasks_counts_api_tasks_counts_get",
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/trust-center/activity",
    alias: "activity_api_trust_center_activity_get",
    description: `Cross-conversation aggregate. Strict context-scope filter is
applied SERVER-SIDE — the response only contains data from
contexts the caller is an active member of.`,
    requestFormat: "json",
    parameters: [
      {
        name: "from",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "to",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "model",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "pii_class",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "user_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(500).optional().default(100),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/trust-center/activity/export",
    alias: "activity_export_api_trust_center_activity_export_get",
    description: `JSON bundle export. Same scoping rules as the activity
endpoint. Includes the raw Shield audit rows so an auditor can
verify the HMAC chain independently.`,
    requestFormat: "json",
    parameters: [
      {
        name: "from",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "to",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "model",
        type: "Query",
        schema: committee_id,
      },
      {
        name: "pii_class",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/trust-center/reasoning",
    alias: "reasoning_api_trust_center_reasoning_get",
    requestFormat: "json",
    parameters: [
      {
        name: "window",
        type: "Query",
        schema: z
          .string()
          .regex(/^(7d|30d)$/)
          .optional()
          .default("7d"),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/trust-center/session/:chat_id",
    alias: "session_api_trust_center_session__chat_id__get",
    description: `Single-conversation Trust Center summary + per-turn list.
Strict context-scope check applied.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/trust-center/session/:chat_id/turn/:message_id",
    alias:
      "session_turn_api_trust_center_session__chat_id__turn__message_id__get",
    description: `Full evidence for one turn. Surfaces the four hash/tokens
visible to bankers: input hash, what Synisense sent to the LLM,
what the LLM returned, what the user saw post-rehydration.

Conservative-storage policy: NONE of the tokenized texts are
persisted by Shield (the audit log keeps only request/response
hashes — verifiable but not viewable). The Trust Center re-runs
the **deterministic** &#x60;&#x60;deidentifier.deidentify()&#x60;&#x60; function on
the saved plaintext to reproduce exactly what Shield sent to the
LLM. Same regex + dict + spaCy pipeline → identical output. Any
auditor can run the same call independently and verify.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/trust-center/session/:chat_id/turn/:message_id/plaintext",
    alias:
      "session_turn_plaintext_api_trust_center_session__chat_id__turn__message_id__plaintext_get",
    description: `The ONLY Trust Center surface that returns raw plaintext.

Auth: context-scope check PLUS chat-owner OR superadmin-in-context.
Writes &#x60;&#x60;trust_center.plaintext_viewed&#x60;&#x60; audit row.`,
    requestFormat: "json",
    parameters: [
      {
        name: "chat_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "message_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/users/me/onboarding-status",
    alias: "get_onboarding_status_api_users_me_onboarding_status_get",
    description: `Read-only — used by AppShell to decide which banner / tooltips
to render.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/users/me/onboarding-status/acknowledge",
    alias:
      "acknowledge_reintro_api_users_me_onboarding_status_acknowledge_post",
    description: `Permanently lock off the re-intro banner. Sets
&#x60;&#x60;shield_v1_intro_acknowledged_at&#x60;&#x60; and also marks the Trust
Center tooltip dismissed (the user has now provably seen the
Trust Center surface).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/users/me/onboarding-status/dismiss",
    alias: "dismiss_reintro_api_users_me_onboarding_status_dismiss_post",
    description: `Increment the re-intro dismissals counter. Caps at
&#x60;&#x60;MAX_DISMISSALS&#x3D;3&#x60;&#x60;; further calls return the capped state.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/users/me/onboarding-status/first-chat-seen",
    alias:
      "mark_first_chat_seen_api_users_me_onboarding_status_first_chat_seen_post",
    description: `J4 (2026-05-25, ratified spec §3 Stage 6) — Mark that the
user has seen the chat composer at least once. Idempotent.
Flips &#x60;accounts.{id}.first_session.first_chat_seen &#x3D; true&#x60; with
an ISO timestamp.

Called on first mount of the Solva Phase D framing surface. The
flag gates the onboarding completion celebration: J-sprint is
considered complete once &#x60;first_chat_seen &#x3D;&#x3D; true&#x60; AND
&#x60;trust_center_introduced &#x3D;&#x3D; true&#x60; (the latter set by the J3
tour-dismiss endpoint).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/users/me/onboarding-status/tooltips/help/dismiss",
    alias:
      "dismiss_help_tooltip_api_users_me_onboarding_status_tooltips_help_dismiss_post",
    description: `Hide the Help top-bar tooltip permanently.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/users/me/onboarding-status/tooltips/trust-center/dismiss",
    alias:
      "dismiss_trust_center_tooltip_api_users_me_onboarding_status_tooltips_trust_center_dismiss_post",
    description: `Hide the Trust Center top-bar tooltip permanently. Does NOT
affect the re-intro banner (those are independent).`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "post",
    path: "/api/users/me/onboarding-status/trust-center-tour/dismiss",
    alias:
      "dismiss_trust_center_tour_api_users_me_onboarding_status_trust_center_tour_dismiss_post",
    description: `J3 (2026-05-25, ratified spec §3 Stage 5) — Mark the Trust
Center introduction tour as completed. Idempotent. Once
dismissed, the tour does NOT re-appear on subsequent visits.

Flips &#x60;accounts.{id}.first_session.trust_center_introduced&#x60; to
True with an ISO timestamp; the &#x60;_compute_status&#x60; reader gates
&#x60;trust_center_tour.show&#x60; on this flag.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
  },
  {
    method: "get",
    path: "/api/ux-advisories",
    alias: "ux_advisories_inline_api_ux_advisories_get",
    description: `Return ux-advisories-v1.md inline (rules doc; mirror of homepage-positioning-v1).`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ux-advisories.md",
    alias: "ux_advisories_download_api_ux_advisories_md_get",
    description: `Return ux-advisories-v1.md as a download.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ux-audit",
    alias: "ux_audit_inline_api_ux_audit_get",
    description: `Return UX_ADVISORIES_AUDIT.md inline (browser will preview as text).`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/ux-audit.md",
    alias: "ux_audit_download_api_ux_audit_md_get",
    description: `Return UX_ADVISORIES_AUDIT.md as a download.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/v1/engine/admin/derive",
    alias: "derive_api_v1_engine_admin_derive_post",
    description: `Runs all 6 derivation rules against the caller&#x27;s Mongo data and
persists &#x60;derived_from_*&#x60; signals. If derivation produces zero
signals, gracefully falls back to the Phase A seeder.

Superadmins MAY pass &#x60;?tenant_id&#x3D;…&#x60; to derive for another tenant
(useful for bank-QA reproducing customer-side traces). Non-admins
always target their own &#x60;account_id&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "tenant_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/engine/admin/reseed",
    alias: "reseed_api_v1_engine_admin_reseed_post",
    requestFormat: "json",
    response: z.unknown(),
    errors: [
      {
        status: 403,
        description: `Disabled in production`,
        schema: ErrorEnvelope,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/engine/signal_types",
    alias: "get_signal_types_api_v1_engine_signal_types_get",
    requestFormat: "json",
    response: SignalTypeCatalogue,
  },
  {
    method: "post",
    path: "/api/v1/engine/signals/query",
    alias: "query_signals_api_v1_engine_signals_query_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SignalQueryRequest,
      },
    ],
    response: SignalQueryResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/engine/subscriptions",
    alias: "create_subscription_api_v1_engine_subscriptions_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SubscriptionRequest,
      },
    ],
    response: SubscriptionResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/shield/audit/:audit_id",
    alias: "get_audit_api_v1_shield_audit__audit_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "audit_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 401,
        description: `Unauthorized`,
        schema: ErrorEnvelope,
      },
      {
        status: 404,
        description: `Not Found`,
        schema: ErrorEnvelope,
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/shield/llm/invoke",
    alias: "invoke_api_v1_shield_llm_invoke_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ShieldInvokeRequest,
      },
    ],
    response: ShieldInvokeResponse,
    errors: [
      {
        status: 401,
        description: `AUTH_DENIED`,
        schema: ErrorEnvelope,
      },
      {
        status: 422,
        description: `PURPOSE_INVALID`,
        schema: ErrorEnvelope,
      },
      {
        status: 451,
        description: `GOVERNANCE_REFUSED`,
        schema: ErrorEnvelope,
      },
      {
        status: 503,
        description: `SERVICE_UNAVAILABLE`,
        schema: ErrorEnvelope,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/shield/receipt/:audit_id",
    alias: "get_receipt_api_v1_shield_receipt__audit_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "audit_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 401,
        description: `Unauthorized`,
        schema: ErrorEnvelope,
      },
      {
        status: 404,
        description: `Not Found`,
        schema: ErrorEnvelope,
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/walkin",
    alias: "walkin_question_api_walkin_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: WalkinIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/walkin/regenerate",
    alias: "walkin_regenerate_api_walkin_regenerate_post",
    description: `Force a fresh question (clears cache, then calls walkin_question).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: WalkinIn,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/webhook/stripe",
    alias: "stripe_webhook_api_webhook_stripe_post",
    description: `Coming-Soon stub. Stripe isn&#x27;t wired in this release — any
inbound webhook is recorded to the audit log + dead-lettered into
&#x60;&#x60;stripe_dead_letter&#x60;&#x60; for operator visibility, then a
&#x60;&#x60;{coming_soon: true, accepted: false}&#x60;&#x60; response is returned.

A &#x60;&#x60;200&#x60;&#x60; (not &#x60;&#x60;400&#x60;&#x60;) is intentional — Stripe will keep
retrying on 4xx; we want them to stop. The dead-letter row is
sufficient for the operator to manually replay later once
billing actually ships.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/website/contact",
    alias: "submit_contact_api_website_contact_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ContactSubmission,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/website/early-access",
    alias: "submit_early_access_api_website_early_access_post",
    description: `Record an application + notify ops + acknowledge applicant.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EarlyAccessApplication,
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/artefacts/:kind/:artefact_id/synisense-breakdown",
    alias:
      "get_studio_synisense_breakdown_api_work_studio_artefacts__kind___artefact_id__synisense_breakdown_get",
    description: `STUDIO sprint (2026-05-12) — per-artefact Synisense breakdown.

Returns the total identifier count + three-layer breakdown grouped
by Work Studio surface (briefing / deck / report / brief / minutes /
enhance). Powers the inline badge on the artefact detail drawer and
the redaction-count line stamped on exports.

Filter is on &#x60;artefact_id&#x60; (post-sprint sessions) with a fallback to
account_id + surface family when no artefact_id is present (legacy
artefacts created before the threading).`,
    requestFormat: "json",
    parameters: [
      {
        name: "kind",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "artefact_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/briefs/:brief_id",
    alias: "get_brief_meta_api_work_studio_briefs__brief_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/work_studio/briefs/:brief_id/enhance",
    alias: "enhance_brief_api_work_studio_briefs__brief_id__enhance_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EnhanceRequest,
      },
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "X-Active-Context",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/briefs/:brief_id/revisions",
    alias:
      "list_brief_revisions_api_work_studio_briefs__brief_id__revisions_get",
    requestFormat: "json",
    parameters: [
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/briefs/:brief_id/revisions/:revision_id/diff",
    alias:
      "diff_brief_revision_api_work_studio_briefs__brief_id__revisions__revision_id__diff_get",
    description: `Diff &#x60;revision_id&#x60; (the right-hand side) against &#x60;against&#x60;
(the left-hand side, defaults to revision&#x27;s parent_revision_id, or
the original revision_0 if &#x60;revision_id&#x60; is the original).`,
    requestFormat: "json",
    parameters: [
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "revision_id",
        type: "Path",
        schema: z.string(),
      },
      {
        name: "against",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/work_studio/briefs/:brief_id/set_active",
    alias: "set_active_api_work_studio_briefs__brief_id__set_active_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ revision_id: z.string().min(1) }).passthrough(),
      },
      {
        name: "brief_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/work_studio/exports",
    alias: "create_export_api_work_studio_exports_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ExportRequest,
      },
      {
        name: "X-Active-Context",
        type: "Header",
        schema: committee_id,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/exports/:export_id",
    alias: "get_export_meta_api_work_studio_exports__export_id__get",
    requestFormat: "json",
    parameters: [
      {
        name: "export_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/exports/:export_id/download",
    alias: "download_export_api_work_studio_exports__export_id__download_get",
    requestFormat: "json",
    parameters: [
      {
        name: "export_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/work_studio/picker",
    alias: "get_picker_api_work_studio_picker_get",
    description: `Return the depth/fidelity/format options each with a one-line
FT-toned insight string. The Work Studio UI renders this directly.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/workbook/analyses",
    alias: "list_analyses_api_workbook_analyses_get",
    requestFormat: "json",
    response: z.union([ItemsListResponse, z.null()]),
  },
  {
    method: "get",
    path: "/api/workbook/analyses/:aid",
    alias: "get_analysis_api_workbook_analyses__aid__get",
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/analyses/:aid/anomalies",
    alias: "anomalies_endpoint_api_workbook_analyses__aid__anomalies_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AnomaliesRequest,
      },
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([AnomaliesResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/analyses/:aid/forecast",
    alias: "forecast_endpoint_api_workbook_analyses__aid__forecast_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ForecastRequest,
      },
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/workbook/analyses/:aid/report.docx",
    alias: "report_docx_endpoint_api_workbook_analyses__aid__report_docx_get",
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/workbook/analyses/:aid/report.pptx",
    alias: "report_endpoint_api_workbook_analyses__aid__report_pptx_get",
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/workbook/analyses/:aid/report.xlsx",
    alias: "report_xlsx_endpoint_api_workbook_analyses__aid__report_xlsx_get",
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/analyses/:aid/signals/extract",
    alias:
      "extract_signals_endpoint_api_workbook_analyses__aid__signals_extract_post",
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([SignalsResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/analyses/:aid/simulate",
    alias: "simulate_endpoint_api_workbook_analyses__aid__simulate_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SimulateRequest,
      },
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/upload",
    alias: "upload_workbook_api_workbook_upload_post",
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ file: z.instanceof(File) }).passthrough(),
      },
    ],
    response: z.union([IdResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/upload-multi",
    alias: "upload_workbook_multi_api_workbook_upload_multi_post",
    description: `Multi-file upload → creates ONE &#x60;Analysis&#x60; row with N source
refs. Per Pre-Read: accepts 1+ files in one request; 250MB cap
PER FILE.

Track A Phase 2 (2026-06-04) — accepts an optional &#x60;objective&#x60;
text that is captured at the top of the Analyze drawer.`,
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body_upload_workbook_multi_api_workbook_upload_multi_post,
      },
    ],
    response: z.union([IdResponse, z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/workbook/v2/analyses",
    alias: "list_analyses_v2_api_workbook_v2_analyses_get",
    description: `List the current account&#x27;s Analyses. Tenant-scoped via
&#x60;account_id&#x60;. Optional &#x60;context_id&#x60; filter for the in-context
journal view.`,
    requestFormat: "json",
    parameters: [
      {
        name: "context_id",
        type: "Query",
        schema: committee_id,
      },
    ],
    response: z.union([z.array(WorkbookAnalysisResponse), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/workbook/v2/analyses/:aid",
    alias: "get_analysis_v2_api_workbook_v2_analyses__aid__get",
    description: `Read endpoint for the new &#x60;Analysis&#x60; entity. Tenant-scoped:
cross-tenant returns 404 (no existence leak).

Track A Phase 6 (2026-06-04) — strips legacy top-level BC mirror
fields (&#x60;narration&#x60;, &#x60;notes&#x60;, &#x60;notes_updated_at&#x60;) from the
response so callers must consume &#x60;runs[-1]&#x60; / &#x60;notes_history[]&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/v2/analyses/:aid/notes",
    alias: "post_analysis_note_api_workbook_v2_analyses__aid__notes_post",
    description: `Append a note to the Analysis. Auto-saved; FE typically
sends one note per save-debounce window. Tenant-scoped.

Track A Phase 4 (2026-06-04) — notes are append-only history.
Idempotency: if the most-recent note&#x27;s body equals the new
body, no new entry is appended (autosave debounce safe — a
double-fire on identical content is a no-op). On every accepted
append, top-level &#x60;notes&#x60; + &#x60;notes_updated_at&#x60; mirror the
latest entry for backwards-compat with consumers reading the
simple shape. &#x60;notes&#x60; mirror removal scheduled for Phase 5 —
see MASTER_STATE Section 4.

Track A Phase 4 iter-2 (2026-06-04) — empty-body deletion
contract: an empty-body POST appends &#x60;{body: &quot;&quot;}&#x60; as an explicit
history event (NOT a 422). The BC mirror &#x60;notes&#x60; is set to &#x60;&quot;&quot;&#x60;
on empty append (divergence from G6 &#x60;documents.notes&#x60; which
clears to &#x60;null&#x60; on empty PATCH — analyses.notes_history is
append-only and never null; the empty string IS the event).
See Tightening 5 in sprints/TRACK_A_PHASE_4_*.md.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ body: z.string().min(0).max(4000) }).passthrough(),
      },
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "patch",
    path: "/api/workbook/v2/analyses/:aid/objective",
    alias:
      "patch_analysis_objective_api_workbook_v2_analyses__aid__objective_patch",
    description: `Save the drawer&#x27;s &quot;objective&quot; text. Auto-save target; FE
debounces on the client side. Tenant-scoped; cross-tenant
returns 404.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ objective: z.string().max(4000) }).passthrough(),
      },
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/v2/analyses/:aid/session-close",
    alias:
      "session_close_endpoint_api_workbook_v2_analyses__aid__session_close_post",
    description: `Delete the excel binary on session close; retain the
Analysis row + sources + (Phase 3) observations + notes.`,
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/workbook/v2/analyses/:aid/synthesize",
    alias:
      "synthesize_v2_endpoint_api_workbook_v2_analyses__aid__synthesize_post",
    description: `Track A Phase 3 (2026-06-04) — Solva v2 Analyze narration.

Loads the new &#x60;Analysis&#x60; entity (&#x60;ana-*&#x60;), runs deterministic
analyzers on the source blobs, asks Claude Sonnet via Shield
for a headline-first narration, validates citations against
the deterministic citation pool, persists to the entity.

Idempotent — re-call with unchanged content returns the
cached narration via &#x60;narration.cache_key&#x60;.

Bug #30 — uses &#x60;autopick_forecast_columns&#x60; so workbooks with
valid (date, value) pairs no longer trip
&#x60;forecast_invalid: need at least 3 (date, value) pairs&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "aid",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.union([z.object({}).partial().passthrough(), z.null()]),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const api = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
