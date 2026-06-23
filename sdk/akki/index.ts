// AUTO-GENERATED — do not edit by hand.
// Source: backend/openapi-sdk/akki.openapi.json
// Regenerate via: python scripts/build_sdk.py

// ── Schemas ──
export interface AcceptIn {
  note?: string | unknown;
}

export interface AcceptOut {
  accepted_at: string;
  assignment_id: string;
  brief_id: string;
  status: string;
}

export interface AccountUpdateIn {
  declared_role?: "ned" | "executive" | "dual" | "undeclared" | unknown;
  name?: string | unknown;
  preferences?: Record<string, unknown> | unknown;
}

export interface AccountWrapResponse {
  account?: Record<string, unknown> | unknown;
  contexts?: Array<unknown> | unknown;
}

export interface ActiveContextIn {
  context_id: string;
  from_context_id?: string | unknown;
}

export interface AdminAuthEventsResponse {
  by_credential?: unknown | unknown;
  by_failure_reason?: unknown | unknown;
  dual_credentials_mismatched?: number | unknown;
  dual_credentials_seen?: number | unknown;
  failure?: number | unknown;
  failure_rate_pct?: number | unknown;
  recent?: Array<unknown> | unknown;
  sampled_events?: number | unknown;
  success?: number | unknown;
  top_paths?: unknown | unknown;
  window_hours?: number | unknown;
}

export interface AgendaIn {
  items?: Array<AgendaItemIn>;
  title: string;
}

export interface AgendaItemIn {
  id?: string | unknown;
  label: string;
  owner_label?: string | unknown;
}

export interface ApplyTemplateIn {
  template_key: string;
}

export interface ArtefactIn {
  id: string;
  kind: string;
}

export interface ArtefactRedirectResponse {
  active_revision_id?: string | unknown;
  artefact_id?: string | unknown;
  brief_id?: string | unknown;
  document_id?: string | unknown;
  kind?: string | unknown;
  redirect_url?: string | unknown;
  title?: string | unknown;
}

export interface AssignmentCreateIn {
  cohort_id?: string | unknown;
  ned_ids?: Array<string> | unknown;
  note?: string | unknown;
}

export interface AsyncJobResponse {
  job_id?: string | unknown;
  kind?: string | unknown;
  status?: string | unknown;
}

export interface AttachmentCreateBody {
  note?: string | unknown;
  target_doc_id: string;
}

export interface AttentionOut {
  drafts: CardDrafts;
  events: CardEvents;
  pulse: CardPulse;
  questions: CardQuestions;
  reports: CardReports;
}

export interface AuthSessionResponse {
  access_token?: string | unknown;
  account?: Record<string, unknown> | unknown;
  contexts?: Array<unknown> | unknown;
}

export interface BlockCreateIn {
  after_block_id?: string | unknown;
  content?: Record<string, unknown>;
  kind: string;
}

export interface BlockMoveIn {
  to_order: number;
}

export interface BlockPatchIn {
  content: Record<string, unknown>;
}

export interface BoardToWatchOut {
  context_id: string;
  name: string;
  reasons: Array<string>;
  score: number;
}

export interface BoardsToWatchOut {
  items: Array<BoardToWatchOut>;
}

export interface Body_attach_to_chat_v1_akki_d69f53af {
  file: string;
}

export interface Body_contributor_upload_v1_akki_4ab7db09 {
  file: string;
  note?: string | unknown;
}

export interface Body_start_enhance_v1_akki_4b34062a {
  file?: string | unknown;
  instructions: string;
  output_format?: string;
  source_artefact_id?: string | unknown;
}

export interface Body_upload_document_v1_akki_e2ad96ea {
  category?: string | unknown;
  data_trust?: string | unknown;
  description?: string | unknown;
  display_name?: string | unknown;
  file: string;
  mentioned_account_ids?: string | unknown;
  related_doc_id?: string | unknown;
  relation_type?: string | unknown;
}

export interface Body_work_studio_enhance_stream_v1_akki_f414e802 {
  file?: string | unknown;
  instructions: string;
  output_format?: string;
  source_artefact_id?: string | unknown;
}

export interface BriefIn {
  deep?: boolean;
  kind: string;
  objective: string;
}

export interface BriefingCreateIn {
  signal_ids?: Array<string> | unknown;
  title?: string | unknown;
}

export interface BriefsCountResponse {
  briefs?: Array<unknown> | unknown;
  count?: number | unknown;
}

export interface ByContextSummaryResponse {
  by_context?: Array<unknown> | unknown;
  by_kind?: Array<unknown> | unknown;
  total?: number | unknown;
  total_pending?: number | unknown;
}

export interface CadencePayload {
  interval?: string | unknown;
  scheduled_at?: string | unknown;
}

export interface CardDrafts {
  count: number;
  oldest_days?: number | unknown;
  subtext: string;
}

export interface CardEvents {
  count: number;
  subtext: string;
}

export interface CardPulse {
  count: number;
  critical: number;
  opportunities: number;
  subtext: string;
}

export interface CardQuestions {
  count: number;
  decomposition: QuestionsDecomposition;
  subtext: string;
}

export interface CardReports {
  count: number;
  subtext: string;
}

export interface CatalogueMemberIn {
  email: string;
  name: string;
}

export interface CatalogueMemberPatch {
  email?: string | unknown;
  name?: string | unknown;
}

export interface ChatAttachmentResponse {
  char_len?: number | unknown;
  chat_id?: string | unknown;
  context_id?: string | unknown;
  created_at?: string | unknown;
  document_id?: string | unknown;
  mime_type?: string | unknown;
  name?: string | unknown;
  original_filename?: string | unknown;
  sensitivity?: unknown | unknown;
  size_bytes?: number | unknown;
  storage_key?: string | unknown;
}

export interface ChatAuditAggregateResponse {
  average_dilution?: number | unknown;
  average_exposure_reduction?: number | unknown;
  headline_prose?: string | unknown;
  identifiers_shielded?: number | unknown;
  llm_calls?: number | unknown;
  message_count?: number | unknown;
}

export interface ChatAuditPanelResponse {
  audit_id?: string | unknown;
  message_id?: string | unknown;
  protective_event?: unknown | unknown;
  protective_layer_prose?: string | unknown;
  provider_prose?: string | unknown;
  references?: unknown | unknown;
  scores?: unknown | unknown;
  shielding_prose?: string | unknown;
}

export interface ChatAuditResponse {
  chat_id?: string | unknown;
  rows?: Array<unknown> | unknown;
  verification_note?: string | unknown;
}

export interface ChatCreateIn {
  context_id?: string | unknown;
  linked_context?: LinkedContextIn | unknown;
  model_id?: string;
  shielding_policy?: "auto" | "always" | "off";
  title?: string | unknown;
}

export interface ChatModelsResponse {
  default_model_id?: string | unknown;
  models?: Array<unknown> | unknown;
}

export interface ChatPatchIn {
  clear_linked_context?: boolean | unknown;
  context_id?: string | unknown;
  linked_context?: LinkedContextIn | unknown;
  model_id?: string | unknown;
  shielding_policy?: "auto" | "always" | "off" | unknown;
  title?: string | unknown;
}

export interface ChecklistEdit {
  note_to_reportee?: string | unknown;
  questions: Array<Record<string, unknown>>;
}

export interface ChecklistGenerateIn {
  committee_id?: string | unknown;
  cycle_name: string;
  deadline_date: string;
  reportee_ids?: Array<string> | unknown;
}

export interface CheckoutIn {
  origin_url: string;
  plan_id: "free" | "pro" | "team";
}

export interface CoachMessageIn {
  lens: string;
  message: string;
}

export interface CoachStartIn {
  lens: string;
  subject: string;
}

export interface CohortApplicationIn {
  email: string;
  name: string;
  organisation: string;
  referral_source?: string | unknown;
  role: string;
  use_case: string;
}

export interface CohortPreviewResponse {
  expires_at?: string | unknown;
  first_name?: string | unknown;
  organisation?: string | unknown;
}

export interface CommitteeIn {
  name: string;
  your_role?: string | unknown;
}

export interface CommitteesResponse {
  committees?: Array<unknown> | unknown;
}

export interface CompilationCreate {
  artefact_type: string;
  cadence_kind: string;
  cadence_payload?: CadencePayload;
  contributor_ids?: Array<string>;
  formats?: Array<string>;
  source_ids?: Array<string>;
  template_key?: string;
  title: string;
}

export interface CompilationStartResponse {
  compilation_id?: string | unknown;
  export_id?: string | unknown;
  idempotent?: boolean | unknown;
  status?: string | unknown;
}

export interface CompleteIn {
  artefact: ArtefactIn;
}

export interface ComposeIn {
  audience_hint?: string | unknown;
  topic: string;
}

export interface ConnectOut {
  authorize_url: string;
}

export interface ConsumeIn {
  mode: string;
  oauth_code?: string | unknown;
  password?: string | unknown;
  token: string;
}

export interface ContactSubmission {
  company?: string | unknown;
  message: string;
  name: string;
  work_email: string;
}

export interface ContextCreateIn {
  industry?: string | unknown;
  jurisdiction?: string | unknown;
  name: string;
  sector?: string | unknown;
  type?: "ned_personal" | "ned_sponsored" | "executive_personal" | "executive_enterprise";
}

export interface ContextObjectIn {
  answers?: Record<string, unknown>;
  completed?: boolean;
  industry?: string | unknown;
  jurisdiction?: string | unknown;
  role?: "ned" | "executive" | "reportee" | unknown;
  sector?: string | unknown;
  step?: number;
}

export interface ContextRenameIn {
  name: string;
}

export interface ContributionIn {
  agenda_item_id?: string | unknown;
  body_text?: string | unknown;
  kind?: string;
  source_doc_id?: string | unknown;
  team_member_id?: string | unknown;
  title?: string | unknown;
}

export interface CopyOverrideIn {
  fields?: Record<string, unknown>;
}

export interface CreateArtefactRequest {
  kind: "deck" | "report";
  source: "blank" | "brief" | "external_document";
  source_brief_id?: string | unknown;
  source_document_id?: string | unknown;
  title: string;
}

export interface CycleActionsResponse {
  as_of?: string | unknown;
  context_id?: string | unknown;
  counts?: unknown | unknown;
  sections?: unknown | unknown;
}

export interface CycleContributionResponse {
  agenda_id?: string | unknown;
  agenda_item_id?: string | unknown;
  body_text?: string | unknown;
  context_id?: string | unknown;
  created_at?: string | unknown;
  cycle_id?: string | unknown;
  id?: string | unknown;
  kind?: string | unknown;
  scored_at?: string | unknown;
  scored_by?: string | unknown;
  scores?: unknown | unknown;
  source_doc_id?: string | unknown;
  status?: string | unknown;
  team_member_id?: string | unknown;
  title?: string | unknown;
}

export interface CycleContributionsListResponse {
  agenda_id?: string | unknown;
  contributions?: Array<unknown> | unknown;
  cycle_id?: string | unknown;
}

export interface CycleCreateIn {
  title: string;
}

export interface CycleFollowUpsResponse {
  agenda_id?: string | unknown;
  cycle_id?: string | unknown;
  followups?: Array<unknown> | unknown;
}

export interface CycleScheduleIn {
  cadence?: "weekly" | "monthly";
  committee_id?: string | unknown;
  cycle_name_template: string;
  deadline_offset_days?: number;
  enabled?: boolean;
  weekday?: "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun";
}

export interface CycleTeamResponse {
  agenda_id?: string | unknown;
  cycle_id?: string | unknown;
  members?: Array<unknown> | unknown;
}

export interface DeclareRoleIn {
  declared_role: "ned" | "executive" | "dual" | "undeclared";
}

export interface DeclineIn {
  reason?: string | unknown;
}

export interface DeleteAccountRequest {
  confirm: string;
}

export interface DemoSensitivityIn {
  text: string;
}

export interface DiffResponse {
  diff?: Array<unknown> | unknown;
  previous_doc?: Record<string, unknown> | unknown;
}

export interface DispatchIn {
  checklist_ids: Array<string>;
}

export interface DocumentEngagementResponse {
  linked_count?: number | unknown;
  linked_documents?: Array<unknown> | unknown;
  readers?: Array<unknown> | unknown;
  share_count?: number | unknown;
  shares?: Array<unknown> | unknown;
  unique_readers?: number | unknown;
  view_count?: number | unknown;
}

export interface DocumentExtractResponse {
  document_id?: string | unknown;
  extract_goals?: unknown | unknown;
  extract_tasks?: unknown | unknown;
  extraction_queued?: boolean | unknown;
  has_extracted_text?: boolean | unknown;
}

export interface DocumentMetaGenerateIn {
  filename?: string | unknown;
  preview_text?: string | unknown;
}

export interface DocumentMetaResponse {
  description?: string | unknown;
  display_name?: string | unknown;
  mode?: string | unknown;
  shielding?: unknown | unknown;
  shielding_masked?: unknown | unknown;
}

export interface DocumentPatchIn {
  structured_content?: Record<string, unknown> | unknown;
  title?: string | unknown;
}

export interface DocumentShareIn {
  message?: string | unknown;
  recipient_emails: Array<string>;
}

export interface DocumentTrustUpdate {
  data_trust?: "trusted" | "mixed" | "weak" | unknown;
  related_doc_id?: string | unknown;
}

export interface DoorIn {
  door: string;
}

export interface DraftLifecycleResponse {
  draft_session_id?: string | unknown;
  export_id?: string | unknown;
  idempotent_update?: boolean | unknown;
  lifecycle_state?: string | unknown;
  updated_at?: string | unknown;
}

export interface EarlyAccessApplication {
  cohort_understood: boolean;
  company: string;
  first_name: string;
  last_name: string;
  linkedin_url?: string | unknown;
  role_title: string;
  role_type: string;
  valuable_text?: string | unknown;
  work_email: string;
}

export interface EarlyAccessIn {
  note?: string | unknown;
}

export interface EnhanceRequest {
  base_revision_id?: string | unknown;
  instruction: string;
  scope?: string;
}

export interface EnterpriseInterestIn {
  company_size?: string | unknown;
  timing?: string | unknown;
  use_case?: string | unknown;
}

export interface EventIn {
  end_at?: string | unknown;
  location?: string | unknown;
  notes?: string | unknown;
  start_at: string;
  title: string;
  type: string;
}

export interface EventOut {
  confidence?: number | unknown;
  context_id: string;
  created_at: string;
  created_by_account_id: string;
  end_at: string | unknown;
  extracted_at?: string | unknown;
  extracted_by?: string | unknown;
  id: string;
  location: string | unknown;
  notes: string | unknown;
  source: string;
  source_ref: string | unknown;
  start_at: string;
  status?: string | unknown;
  title: string;
  type: string;
  updated_at: string;
}

export interface EventPatch {
  end_at?: string | unknown;
  location?: string | unknown;
  notes?: string | unknown;
  start_at?: string | unknown;
  status?: string | unknown;
  title?: string | unknown;
  type?: string | unknown;
}

export interface EventsList {
  items: Array<EventOut>;
  total: number;
}

export interface ExcoAddMemberIn {
  account_id: string;
}

export interface ExcoCreateIn {
  description?: string | unknown;
  member_account_ids?: Array<string>;
  name: string;
}

export interface ExcoMember {
  account_id: string;
  name: string;
  role: string;
  sub_role?: string | unknown;
}

export interface ExcoTeamOut {
  context_id: string;
  created_at: string;
  created_by: string;
  description?: string | unknown;
  id: string;
  member_account_ids: Array<string>;
  members?: Array<ExcoMember> | unknown;
  my_role?: "creator" | "member" | "outside" | unknown;
  name: string;
  status: "active" | "archived";
  updated_at: string;
}

export interface ExcoUpdateIn {
  description?: string | unknown;
  name?: string | unknown;
  status?: "active" | "archived" | unknown;
}

export interface ExportPolicyResponse {
  can_export?: boolean | unknown;
  watermark_label?: string | unknown;
  watermark_required?: boolean | unknown;
}

export interface ExportRequest {
  company_label?: string;
  depth: string;
  document_type?: string;
  fidelity: string;
  format: string;
  programme?: string | unknown;
  revision_id?: string | unknown;
  source_id: string;
  source_type: string;
}

export interface ExportRequestIn {
  description: string;
  objective: string;
  output_format?: "docx" | "pptx" | "pdf" | "auto";
  scope: string;
}

export interface ExportStartResponse {
  created_at?: string | unknown;
  export_id?: string | unknown;
  kind?: string | unknown;
  output_format?: string | unknown;
  status?: string | unknown;
}

export interface ExtractEventsOut {
  discarded: Record<string, unknown>;
  extracted: Array<Record<string, unknown>>;
  persisted_draft_ids: Array<string>;
}

export interface ExtractFromDocIn {
  doc_id: string;
  replace_existing?: boolean;
}

export interface ExtractTriggerIn {
  extract_goals?: boolean;
  extract_tasks?: boolean;
  force?: boolean;
}

export interface FinishIn {
  magic_link_token?: string | unknown;
  session_id: string;
}

export interface FirstSessionResetIn {
  account_email?: string | unknown;
}

export interface FollowUpDraftsResponse {
  count?: number | unknown;
  drafts?: Array<unknown> | unknown;
}

export interface FollowUpsDraftIn {
  item_ids?: Array<string> | unknown;
}

export interface FollowupDraft {
  body_md: string;
  subject: string;
  to_email: string;
  to_name?: string | unknown;
}

export interface ForceResetIn {
  send_email?: boolean;
}

export interface ForgotPasswordIn {
  email: string;
}

export interface FormPayload {
  email?: string;
  emphasis?: Array<string>;
  name: string;
  org_size: string;
  org_type: string;
  org_type_other?: string;
  role: string;
  role_other?: string;
  situation?: string;
}

export interface FromDocumentRequest {
  kind: "board_pack" | "committee_pack" | "minutes" | "deck" | "report";
  source_doc_id: string;
}

export interface FromSourceRequest {
  company_label?: string;
  document_type?: string;
  kind: "briefing" | "deck" | "report";
  programme?: string | unknown;
  source_id: string;
  source_type: "solva_session" | "chat_artefact";
}

export interface GenerateIn {
  confirmed?: boolean;
  edits?: Record<string, unknown> | unknown;
  outline_id: string;
}

export interface GoalIn {
  category?: "revenue" | "customer" | "product" | "people" | "operations" | "compliance";
  current_score?: number | unknown;
  current_value?: string | unknown;
  department?: "ceo" | "cfo" | "coo" | "commercial" | "board";
  description?: string | unknown;
  initiatives_count?: number;
  owner_name?: string | unknown;
  probability?: number | unknown;
  status?: "on_track" | "at_risk" | "off_track" | "achieved" | "abandoned";
  target_date?: string | unknown;
  target_metric?: string | unknown;
  target_value?: string | unknown;
  title: string;
}

export interface GoalPatch {
  category?: "revenue" | "customer" | "product" | "people" | "operations" | "compliance" | unknown;
  current_score?: number | unknown;
  current_value?: string | unknown;
  department?: "ceo" | "cfo" | "coo" | "commercial" | "board" | unknown;
  description?: string | unknown;
  initiatives_count?: number | unknown;
  owner_name?: string | unknown;
  probability?: number | unknown;
  status?: "on_track" | "at_risk" | "off_track" | "achieved" | "abandoned" | unknown;
  target_date?: string | unknown;
  target_metric?: string | unknown;
  target_value?: string | unknown;
  title?: string | unknown;
}

export interface HTTPValidationError {
  detail?: Array<ValidationError>;
}

export interface IdResponse {
  deleted?: boolean | unknown;
  id?: string | unknown;
}

export interface ImageUploadIn {
  alt?: string | unknown;
  data_base64: string;
  filename: string;
  mime_type: string;
}

export interface IntakeIn {
  primary_context_name: string;
  role: string;
  top_of_mind: string;
}

export interface IntelligenceRegenerateResponse {
  doc_id?: string | unknown;
  mode?: string | unknown;
  status?: string | unknown;
}

export interface InvitationIn {
  email: string;
  role?: "ned" | "executive" | "reportee";
  sub_role?: string | unknown;
}

export interface IssueIn {
  application_id: string;
}

export interface IssueInviteIn {
  cohort_tag: string;
  email: string;
  first_name?: string | unknown;
  logo_name?: string | unknown;
  trial_length_days?: number;
}

export interface ItemsListResponse {
  items?: Array<unknown> | unknown;
  next_cursor?: string | unknown;
  total?: number | unknown;
  total_pending?: number | unknown;
}

export interface JournalCommentaryResponse {
  cached?: boolean | unknown;
  commentary?: unknown | unknown;
  commentary_redacted?: unknown | unknown;
  doc_id?: string | unknown;
  generated_at?: string | unknown;
  synisense_version?: string | unknown;
}

export interface LLMProbeIn {
  module: string;
  query: string;
}

export interface LastActionOut {
  action: string | unknown;
  artefact_id: string | unknown;
  artefact_kind?: string | unknown;
  artefact_title: string | unknown;
  at: string | unknown;
  context_id: string | unknown;
  context_name: string | unknown;
  deep_link: string | unknown;
  surface: string | unknown;
}

export interface LearnResearchIn {
  context_id?: string | unknown;
  topic: string;
}

export interface LensRunIn {
  committee_id?: string | unknown;
  lens: string;
  signal_id?: string | unknown;
  subject: string;
}

export interface LineagePatchBody {
  parent_doc_id?: string | unknown;
  version_label?: string | unknown;
}

export interface LinkResponseIn {
  document_id: string;
}

export interface LinkedContextIn {
  ctx_id: string;
  ctx_type: string;
}

export interface LoginIn {
  email: string;
  password: string;
}

export interface MFAConfirmIn {
  code: string;
}

export interface MFADisableIn {
  password: string;
}

export interface MFAVerifyIn {
  code: string;
}

export interface MarkAnsweredIn {
  note?: string | unknown;
}

export interface MarkReadIn {
  via?: string;
}

export interface MeetingCreate {
  committee: string;
  context_id: string;
  paper_doc_ids?: Array<string> | unknown;
  scheduled_at: string;
  title: string;
}

export interface MeetingPatch {
  committee?: string | unknown;
  formulated_question?: string | unknown;
  paper_doc_ids?: Array<string> | unknown;
  prep_state?: "not_started" | "started" | "ready" | unknown;
  scheduled_at?: string | unknown;
  state?: "pre" | "in" | "post" | "closed" | unknown;
  title?: string | unknown;
}

export interface MessageSendIn {
  acknowledge_unshielded?: boolean;
  attached_document_ids?: Array<string>;
  content: string;
  force_class?: "trivial" | "light_substantive" | "substantive_analytical" | "strategic_deliverable" | unknown;
  show_pass_1?: boolean;
}

export interface MfaEnrollStartResponse {
  otpauth_url?: string | unknown;
  qr_data_url?: string | unknown;
  secret?: string | unknown;
}

export interface MfaStatusResponse {
  enrolled_at?: string | unknown;
  locked?: boolean | unknown;
  mfa_enabled?: boolean | unknown;
  recovery_codes_remaining?: number | unknown;
}

export interface NewsFeedOut {
  items: Array<NewsItemOut>;
  region_applied?: string | unknown;
  total: number;
}

export interface NewsItemOut {
  id: string;
  published_at: string;
  regions: Array<string>;
  source: string;
  summary: string;
  title: string;
  url: string;
}

export interface NoteCreate {
  body: string;
  kind: "qna" | "decision" | "open";
  related_question_index?: number | unknown;
}

export interface NotifyOut {
  already_subscribed: boolean;
  coming_soon: boolean;
  message: string;
  notified: boolean;
}

export interface ObjectiveCheckAnswerIn {
  answer: string;
  note?: string | unknown;
}

export interface ObjectiveSourceResponse {
  objective?: unknown | unknown;
  source?: unknown | unknown;
  success_criteria?: Array<unknown> | unknown;
}

export interface OkResponse {
  message?: string | unknown;
  ok?: boolean | unknown;
}

export interface OnboardingBriefsResponse {
  slides?: Array<unknown> | unknown;
}

export interface OutlineIn {
  audience?: string | unknown;
  intent: string;
  parent_outline_id?: string | unknown;
  target_slides?: number | unknown;
}

export interface ParagraphsResponse {
  computed_at?: string | unknown;
  doc_id?: string | unknown;
  page_count?: number | unknown;
  paragraphs?: Array<unknown> | unknown;
  version?: unknown | unknown;
}

export interface PasswordChangeIn {
  current_password: string;
  new_password: string;
}

export interface PasswordResetTokenResponse {
  email_masked?: string | unknown;
  valid?: boolean | unknown;
}

export interface PipelineRunIn {
  focus?: string | unknown;
}

export interface PolishIn {
  instruction?: string | unknown;
}

export interface PortfolioMetricsOut {
  briefings: number;
  companies: number;
  documents: number;
  signals: number;
}

export interface PositionCreate {
  decision_text: string;
  position: "for" | "against" | "abstained";
  private_note?: string | unknown;
}

export interface PreferencesPutRequest {
  custom_instructions?: string;
  lenses_enabled?: Array<string>;
}

export interface ProfileOut {
  country?: string | unknown;
}

export interface ProfilePatchIn {
  country?: string | unknown;
}

export interface QuestionPatch {
  category?: "audit" | "risk" | "operational" | "strategic" | "people" | "financial" | "regulatory" | "general" | unknown;
  committee_id?: string | unknown;
  status?: "open" | "answered" | "retired" | unknown;
  text?: string | unknown;
}

export interface QuestionsDecomposition {
  board: number;
  ceo: number;
  team: number;
}

export interface QuickActionOrderOut {
  canonical: Array<string>;
  order: Array<string>;
}

export interface ReadinessOut {
  open_task_count: number;
  readiness_percent: number | unknown;
}

export interface RecentDocSeedIn {
  account_email?: string | unknown;
  context_name?: string | unknown;
}

export interface RecentViewIn {
  artefact_id?: string | unknown;
  artefact_kind?: string | unknown;
  context_id?: string | unknown;
  deep_link?: string | unknown;
  label: string;
  surface_path: string;
}

export interface RejectIn {
  reason?: string | unknown;
}

export interface ReorderIn {
  block_ids: Array<string>;
}

export interface ReportComposeIn {
  chain: Array<ReviewerIn>;
  cycle_name: string;
  description?: string | unknown;
  title: string;
}

export interface ReportPatchIn {
  body?: string | unknown;
  note?: string | unknown;
  title?: string | unknown;
}

export interface ReporteeIn {
  areas?: Array<"audit" | "risk" | "operational" | "strategic" | "people" | "financial" | "regulatory" | "general">;
  committee_id?: string | unknown;
  email: string;
  name: string;
  title: string;
}

export interface ResetPasswordIn {
  new_password: string;
}

export interface ResolveIn {
  resolution_note?: string | unknown;
}

export interface ReviewActionIn {
  action: "approve" | "send_back";
  note?: string | unknown;
}

export interface ReviewerIn {
  email: string;
  name: string;
  title: string;
}

export interface ReviseIn {
  instruction: string;
  scope?: "entire" | "section" | "pages";
  section_index?: number | unknown;
  tone?: "formal" | "concise" | "detailed";
}

export interface SandboxConvertIn {
  email: string;
  keep_sandbox?: boolean;
  name: string;
  password: string;
}

export interface SandboxEmailCaptureIn {
  email: string;
}

export interface SandboxIntakeIn {
  company_name: string;
  objective?: string | unknown;
  other_sector_description?: string | unknown;
  other_sector_name?: string | unknown;
  prospect_email?: string | unknown;
  region: "east_africa" | "west_africa" | "southern_africa" | "north_africa" | "europe" | "north_america" | "middle_east" | "asia_pacific";
  role: "ned" | "executive" | "both";
  sector: "financial_services" | "saas" | "logistics" | "healthcare" | "manufacturing" | "retail" | "real_estate" | "other";
}

export interface SandboxSampleAccept {
  filename: string;
  preview: string;
  title: string;
}

export interface SandboxV2AddSentenceIn {
  sentence: string;
}

export interface SandboxV2PatchIn {
  payload?: Record<string, unknown> | unknown;
  state?: string | unknown;
}

export interface SandboxV2SaveSendIn {
  email: string;
}

export interface SandboxV2WelcomeIn {
  hope?: string | unknown;
  name: string;
  org_type: "bank" | "healthcare" | "logistics" | "saas" | "government" | "pre_ipo" | "listed_corporate" | "other";
  role: "ceo" | "ned" | "company_secretary" | "exco_member" | "government_executive" | "regulator" | "investor" | "other";
}

export interface SaveIn {
  label?: string | unknown;
}

export interface ScheduleResponse {
  schedule?: Record<string, unknown> | unknown;
}

export interface ScoreIn {
  fullness?: number | unknown;
  rationale?: string | unknown;
  readiness?: number | unknown;
  relevance?: number | unknown;
}

export interface SeededContextIn {
  company_name: string;
  objective?: string | unknown;
  other_sector_description?: string | unknown;
  other_sector_name?: string | unknown;
  region: "east_africa" | "west_africa" | "southern_africa" | "north_africa" | "europe" | "north_america" | "middle_east" | "asia_pacific";
  role: "ned" | "executive" | "both";
  sector: "financial_services" | "saas" | "logistics" | "healthcare" | "manufacturing" | "retail" | "real_estate" | "other";
  seed_data?: boolean;
}

export interface SendIn {
  body_note?: string | unknown;
  subject?: string | unknown;
  to: Array<string>;
}

export interface SetActiveRequest {
  revision_id: string;
}

export interface SetDefaultContextIn {
  context_id: string;
}

export interface SetPasswordIn {
  password: string;
}

export interface ShareCreateIn {
  delivery_method?: "email" | "akki_notification";
  include_as_quote?: boolean;
  item_id: string;
  item_type: "signal" | "briefing" | "brief" | "doc_summary" | "doc_evolution";
  message?: string | unknown;
  subject?: string | unknown;
  to_email: string;
}

export interface ShareEmailIn {
  message?: string | unknown;
  to_email: string;
  to_name?: string | unknown;
}

export interface SimulateIn {
  committee_id?: string | unknown;
  horizon?: string;
  hypothesis: string;
  signal_ids?: Array<string> | unknown;
}

export interface SnapshotResponse {
  saved_at?: string | unknown;
  snapshot_id?: string | unknown;
}

export interface SolvaCycleEditIn {
  note?: string | unknown;
  questions?: Array<Record<string, unknown>> | unknown;
}

export interface SpecialAskIn {
  case_study_consent?: boolean | unknown;
  referral_email?: string | unknown;
  referral_name?: string | unknown;
  testimonial_text?: string | unknown;
}

export interface StateOnlyResponse {
  state?: string | unknown;
}

export interface StatusAssessmentBody {
  note?: string | unknown;
}

export interface StatusKindResponse {
  kind?: string | unknown;
  status?: string | unknown;
}

export interface StatusOut {
  connected: boolean;
  connected_at: string | unknown;
  last_sync_at: string | unknown;
  last_sync_error: string | unknown;
  last_sync_status: string | unknown;
  provider: string | unknown;
  synced_count: number;
}

export interface StrategicGoalUpdateIn {
  note?: string | unknown;
}

export interface SubmissionIn {
  answers: Array<routers__cycle__AnswerIn>;
  notes?: string | unknown;
}

export interface SubmitForBoardOut {
  board_status: string;
  brief_id: string;
  submitted_at: string;
  submitter_account_id: string;
}

export interface SubmitReviewIn {
  note?: string | unknown;
}

export interface SubscribeIn {
  email: string;
  name?: string | unknown;
  role?: string | unknown;
}

export interface SyncOut {
  errors: number;
  imported: number;
  skipped: number;
}

export interface TaskCirculationResponse {
  docs?: Array<unknown> | unknown;
  expires_at?: string | unknown;
  own_comments?: unknown | unknown;
  reviewer_email?: string | unknown;
  task?: unknown | unknown;
}

export interface TaskContributeResponse {
  contribution?: unknown | unknown;
  contributor_email?: string | unknown;
  docs?: Array<unknown> | unknown;
  expires_at?: string | unknown;
  peers?: Array<unknown> | unknown;
  task?: unknown | unknown;
  your_due_date?: string | unknown;
  your_status?: string | unknown;
}

export interface TaskHashResponse {
  contributor_id?: string | unknown;
  readiness_score?: number | unknown;
  status?: string | unknown;
  task_hash?: string | unknown;
  task_id?: string | unknown;
  team?: unknown | unknown;
}

export interface TaskInitiativeIn {
  body?: string | unknown;
  category?: "revenue" | "customer" | "product" | "people" | "operations" | "compliance";
  owner_role?: "CEO" | "CFO" | "COO" | "CRO" | "CTO" | "CHRO" | "CMO" | "CIO" | "OTHER" | unknown;
  parent_objective_id?: string | unknown;
  performance_score?: number;
  probability_score?: number;
  source_document_id?: string | unknown;
  status?: "on_track" | "at_risk" | "off_track" | "achieved" | "not_started";
  title: string;
}

export interface TaskInitiativePatch {
  body?: string | unknown;
  category?: "revenue" | "customer" | "product" | "people" | "operations" | "compliance" | unknown;
  owner_role?: "CEO" | "CFO" | "COO" | "CRO" | "CTO" | "CHRO" | "CMO" | "CIO" | "OTHER" | unknown;
  parent_objective_id?: string | unknown;
  performance_score?: number | unknown;
  probability_score?: number | unknown;
  status?: "on_track" | "at_risk" | "off_track" | "achieved" | "not_started" | unknown;
  title?: string | unknown;
}

export interface TeamMemberIn {
  contribution_description: string;
  email: string;
  id?: string | unknown;
  name: string;
  owns_item_ids?: Array<string>;
  role?: string | unknown;
}

export interface TeamMemberPatch {
  contribution_description?: string | unknown;
  email?: string | unknown;
  name?: string | unknown;
  owns_item_ids?: Array<string> | unknown;
  role?: string | unknown;
}

export interface TelemetryEventIn {
  context_id?: string | unknown;
  event_name: string;
  event_version?: string;
  properties?: Record<string, unknown>;
  session_id?: string | unknown;
  surface?: string | unknown;
}

export interface ThreadAncestryResponse {
  ancestors?: Array<unknown> | unknown;
  descendants?: Array<unknown> | unknown;
}

export interface TokenIssueResponse {
  expires_at?: string | unknown;
  token?: string | unknown;
}

export interface TopSignalItem {
  deep_link: string;
  id: string;
  severity: string | unknown;
  subtitle: string;
  timestamp: string | unknown;
  title: string;
}

export interface TopSignalsOut {
  chip: string;
  items: Array<TopSignalItem>;
  total_available: number;
}

export interface TutorialDismissIn {
  dismissed?: boolean;
}

export interface UserCreateIn {
  cohort_tag?: string | unknown;
  email: string;
  first_name?: string | unknown;
  initial_password?: string | unknown;
  logo_name?: string | unknown;
  role?: string | unknown;
}

export interface ValidationError {
  loc: Array<string | number>;
  msg: string;
  type: string;
}

export interface WaitlistJoinRequest {
  email: string;
  source_application_id?: string | unknown;
}

export interface WalkinIn {
  artefact_id: string;
  context_id: string;
  kind: "brief" | "minutes" | "deck";
}

export interface _ActionIn {
  note?: string | unknown;
}

export interface _AgentPrefillIn {
  name: string;
}

export interface _ApplyCommentIn {
  action: string;
  comment_id: string;
}

export interface _CirculationCommentIn {
  comment: string;
  doc_id?: string | unknown;
  span?: _CirculationSpan | unknown;
}

export interface _CirculationSendIn {
  base_url?: string | unknown;
  message?: string | unknown;
  reviewer_emails: Array<string>;
}

export interface _CirculationSpan {
  end: number;
  start: number;
  text: string;
}

export interface _ContributionPatchIn {
  note?: string | unknown;
  status: string;
}

export interface _ContributorCommentIn {
  comment: string;
}

export interface _ContributorSubmitIn {
  final_note?: string | unknown;
}

export interface _ManualCreateIn {
  body?: string;
  name?: string;
  objective?: Record<string, unknown> | unknown;
  origin?: string;
  state?: string;
}

export interface _OutputSpecIn {
  final_due_date?: string | unknown;
  formats?: Array<string>;
  free_text?: string | unknown;
  kind?: string;
  template_id?: string | unknown;
}

export interface _PromptedEditIn {
  prompt: string;
}

export interface _ReviewCompleteIn {
  skip_circulation?: boolean;
}

export interface _RouteIn {
  route_kind: string;
  target_hint?: Record<string, unknown> | unknown;
}

export interface _SaveDraftIn {
  document_id?: string | unknown;
  draft_session_id: string;
  kind?: "report" | "deck" | "minutes" | "committee_pack" | "briefing" | "board_pack";
  structured_content?: Record<string, unknown>;
  title?: string;
}

export interface _SeedQuestionIn {
  asker_role?: string | unknown;
  assignee_account_id?: string | unknown;
  context_id?: string | unknown;
  cycle_id?: string | unknown;
  status?: string | unknown;
  text: string;
}

export interface _StatusIn {
  status: string;
}

export interface _TaskIn {
  context_id?: string | unknown;
  due_date?: string | unknown;
  name: string;
  objective?: string | unknown;
  output_spec?: _OutputSpecIn | unknown;
  state?: string;
  success_criteria?: string | unknown;
  team?: Array<_TeamMemberIn>;
}

export interface _TaskPatch {
  due_date?: string | unknown;
  name?: string | unknown;
  objective?: string | unknown;
  output_spec?: _OutputSpecIn | unknown;
  state?: string | unknown;
  success_criteria?: string | unknown;
  team?: Array<_TeamMemberIn> | unknown;
}

export interface _TeamMemberIn {
  adherence_score?: number | unknown;
  allow_email_reply?: boolean | unknown;
  contribution?: string | unknown;
  contribution_mode?: string;
  contributor_id?: string | unknown;
  due_date?: string | unknown;
  email: string;
  name: string;
  role?: string | unknown;
  status?: string | unknown;
}

export interface routers__admin_journal__BackfillRequest {
  concurrency?: number;
  limit?: number | unknown;
  refresh?: boolean;
  sleep_ms?: number;
}

export interface routers__auth__RegisterIn {
  context_name?: string | unknown;
  email: string;
  name: string;
  password: string;
}

export interface routers__comments__CommentIn {
  body: string;
  parent_id?: string | unknown;
}

export interface routers__cycle__AnswerIn {
  answer?: string;
  question_id?: string | unknown;
  question_text?: string | unknown;
}

export interface routers__cycle__QuestionIn {
  category?: "audit" | "risk" | "operational" | "strategic" | "people" | "financial" | "regulatory" | "general";
  committee_id?: string | unknown;
  source?: string | unknown;
  text: string;
}

export interface routers__daily_review__ApproveIn {
  note?: string | unknown;
}

export interface routers__decks__FeedbackIn {
  comment?: string | unknown;
  rating: string;
  regen_reason?: string | unknown;
  will_regenerate?: boolean;
}

export interface routers__early_access__RegisterIn {
  board_count?: number | unknown;
  company?: string | unknown;
  email: string;
  full_name?: string | unknown;
  message?: string | unknown;
  role?: "executive" | "ned" | "chair" | "other" | unknown;
}

export interface routers__feedback__FeedbackIn {
  surface_path: string;
  tag: "Broken" | "Wrong" | "Great";
  text: string;
}

export interface routers__pulse__CommentIn {
  note: string;
}

export interface routers__pulse__ShareIn {
  note?: string | unknown;
  recipients?: Array<string>;
}

export interface routers__questions__AnswerIn {
  text: string;
}

export interface routers__questions__QuestionIn {
  agenda_item_id?: string | unknown;
  assignee_account_id?: string | unknown;
  text: string;
}

export interface routers__questions__ShareIn {
  message?: string | unknown;
  recipient_emails: Array<string>;
}

export interface routers__studio__ShareIn {
  external?: boolean;
  message?: string | unknown;
  to_email: string;
  to_name?: string | unknown;
}

export interface routers__studio_blocks__ApproveIn {
  note?: string | unknown;
}

// ── Client ──
export interface AkkiClientOptions {
  baseUrl: string;
  authToken?: string;
  fetchImpl?: typeof fetch;
}

export class AkkiClient {
  private baseUrl: string;
  private authToken?: string;
  private fetchImpl: typeof fetch;

  constructor(opts: AkkiClientOptions) {
    this.baseUrl = opts.baseUrl.replace(/\/$/, '');
    this.authToken = opts.authToken;
    this.fetchImpl = opts.fetchImpl ?? fetch;
  }

  private async _request(method: string, path: string, body?: unknown): Promise<unknown> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.authToken) headers['Authorization'] = `Bearer ${this.authToken}`;
    const resp = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    if (!resp.ok) throw new Error(`${method} ${path} → ${resp.status}`);
    const ct = resp.headers.get('content-type') || '';
    return ct.includes('application/json') ? resp.json() : resp.text();
  }

  async getV1Akki(): Promise<unknown> {
    return this._request('GET', '/v1/akki/');
  }

  async patchV1AkkiAccountsMe(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/accounts/me', body);
  }

  async getV1AkkiAccountsMeConsent_decisions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/accounts/me/consent-decisions');
  }

  async postV1AkkiAccountsMeDefault_context(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/accounts/me/default-context', body);
  }

  async getV1AkkiAccountsByaccount_idTask_activityRecent(): Promise<unknown> {
    return this._request('GET', '/v1/akki/accounts/{account_id}/task-activity/recent');
  }

  async getV1AkkiAdminAudit_invariant_violations(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/audit-invariant-violations');
  }

  async getV1AkkiAdminAudit_invariant_violationsSummary(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/audit-invariant-violations/summary');
  }

  async getV1AkkiAdminAuthEvents(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/auth/events');
  }

  async postV1AkkiAdminAuthRevoke_allByaccount_id(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/auth/revoke-all/{account_id}', body);
  }

  async postV1AkkiAdminChat_retentionSweep(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/chat-retention/sweep', body);
  }

  async getV1AkkiAdminCohortApplications(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/applications');
  }

  async postV1AkkiAdminCohortApplicationsByapplication_idApprove(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/cohort/applications/{application_id}/approve', body);
  }

  async postV1AkkiAdminCohortApplicationsByapplication_idDecline(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/cohort/applications/{application_id}/decline', body);
  }

  async postV1AkkiAdminCohortApplicationsByapplication_idHold(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/cohort/applications/{application_id}/hold', body);
  }

  async getV1AkkiAdminCohortConsole(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/console');
  }

  async getV1AkkiAdminCohortConsoleAccountByaccount_idTimeline(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/console/account/{account_id}/timeline');
  }

  async getV1AkkiAdminCohortConsoleSpecial_asks(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/console/special-asks');
  }

  async getV1AkkiAdminCohortConsoleStages(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/console/stages');
  }

  async getV1AkkiAdminCohortCopy(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/copy');
  }

  async putV1AkkiAdminCohortCopyByslot(body?: unknown): Promise<unknown> {
    return this._request('PUT', '/v1/akki/admin/cohort/copy/{slot}', body);
  }

  async getV1AkkiAdminCohortFunnel(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/funnel');
  }

  async getV1AkkiAdminCohortInvites(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/cohort/invites');
  }

  async postV1AkkiAdminCohortInvites(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/cohort/invites', body);
  }

  async getV1AkkiAdminEmail_providerHealth(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/email-provider/health');
  }

  async getV1AkkiAdminExtractions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/extractions');
  }

  async getV1AkkiAdminHealthFull(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/health/full');
  }

  async getV1AkkiAdminInboxMessages(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/inbox/messages');
  }

  async getV1AkkiAdminInboxMessagesBymessage_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/inbox/messages/{message_id}');
  }

  async postV1AkkiAdminInboxMessagesBymessage_idClassify(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/inbox/messages/{message_id}/classify', body);
  }

  async postV1AkkiAdminInboxMessagesBymessage_idDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/inbox/messages/{message_id}/dismiss', body);
  }

  async postV1AkkiAdminInboxMessagesBymessage_idRoute(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/inbox/messages/{message_id}/route', body);
  }

  async getV1AkkiAdminInboxMessagesBymessage_idRouting_log(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/inbox/messages/{message_id}/routing-log');
  }

  async postV1AkkiAdminInboxMessagesBymessage_idStatus(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/inbox/messages/{message_id}/status', body);
  }

  async getV1AkkiAdminInboxUnread_count(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/inbox/unread-count');
  }

  async postV1AkkiAdminJournalBackfill(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/journal/backfill', body);
  }

  async getV1AkkiAdminLlmDecksQuality(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/llm/decks/quality');
  }

  async getV1AkkiAdminLlmRetries_24h(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/llm/retries_24h');
  }

  async getV1AkkiAdminLlmSpend(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/llm/spend');
  }

  async postV1AkkiAdminQaFirst_sessionReset(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/qa/first-session/reset', body);
  }

  async postV1AkkiAdminQaSeedQuestion(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/qa/seed/question', body);
  }

  async postV1AkkiAdminQaSeedRecent_doc(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/qa/seed/recent-doc', body);
  }

  async getV1AkkiAdminSandboxKpi(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/sandbox/kpi');
  }

  async getV1AkkiAdminSandboxObjectives(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/sandbox/objectives');
  }

  async getV1AkkiAdminTenants(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/tenants');
  }

  async getV1AkkiAdminTenantsBycontext_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/tenants/{context_id}');
  }

  async getV1AkkiAdminTenantsBycontext_idExtractions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/tenants/{context_id}/extractions');
  }

  async getV1AkkiAdminUsers(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/users');
  }

  async postV1AkkiAdminUsers(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/users', body);
  }

  async getV1AkkiAdminUsersExport_csv(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/users/export.csv');
  }

  async postV1AkkiAdminUsersProcess_deletions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/users/process-deletions', body);
  }

  async getV1AkkiAdminUsersByuser_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/users/{user_id}');
  }

  async postV1AkkiAdminUsersByuser_idForce_reset_password(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/users/{user_id}/force-reset-password', body);
  }

  async postV1AkkiAdminUsersByuser_idRestore(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/users/{user_id}/restore', body);
  }

  async postV1AkkiAdminUsersByuser_idSuspend(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/admin/users/{user_id}/suspend', body);
  }

  async getV1AkkiAdminUsersByuser_idTimeline(): Promise<unknown> {
    return this._request('GET', '/v1/akki/admin/users/{user_id}/timeline');
  }

  async postV1AkkiAuthDeclare_role(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/declare-role', body);
  }

  async postV1AkkiAuthForgot_password(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/forgot-password', body);
  }

  async postV1AkkiAuthLogin(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/login', body);
  }

  async postV1AkkiAuthLogout(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/logout', body);
  }

  async postV1AkkiAuthMagic_linkConsume(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/magic-link/consume', body);
  }

  async postV1AkkiAuthMagic_linkIssue(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/magic-link/issue', body);
  }

  async getV1AkkiAuthMagic_linkPreviewBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/magic-link/preview/{token}');
  }

  async getV1AkkiAuthMagicBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/magic/{token}');
  }

  async getV1AkkiAuthMe(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/me');
  }

  async postV1AkkiAuthMfaDisable(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/mfa/disable', body);
  }

  async postV1AkkiAuthMfaEnrollConfirm(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/mfa/enroll/confirm', body);
  }

  async postV1AkkiAuthMfaEnrollStart(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/mfa/enroll/start', body);
  }

  async postV1AkkiAuthMfaRecoveryRegenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/mfa/recovery/regenerate', body);
  }

  async getV1AkkiAuthMfaStatus(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/mfa/status');
  }

  async postV1AkkiAuthMfaVerify(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/mfa/verify', body);
  }

  async postV1AkkiAuthOauthGoogleFinish(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/oauth/google/finish', body);
  }

  async getV1AkkiAuthOauthGoogleStart(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/oauth/google/start');
  }

  async getV1AkkiAuthOauthMicrosoftCallback(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/oauth/microsoft/callback');
  }

  async postV1AkkiAuthOauthMicrosoftFinish(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/oauth/microsoft/finish', body);
  }

  async getV1AkkiAuthOauthMicrosoftStart(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/oauth/microsoft/start');
  }

  async postV1AkkiAuthPasswordChange(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/password/change', body);
  }

  async postV1AkkiAuthRefresh(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/refresh', body);
  }

  async postV1AkkiAuthRegister(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/register', body);
  }

  async getV1AkkiAuthReset_passwordBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/auth/reset-password/{token}');
  }

  async postV1AkkiAuthReset_passwordBytoken(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/reset-password/{token}', body);
  }

  async postV1AkkiAuthSet_password(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/auth/set-password', body);
  }

  async postV1AkkiBillingCheckout(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/billing/checkout', body);
  }

  async getV1AkkiBillingMe(): Promise<unknown> {
    return this._request('GET', '/v1/akki/billing/me');
  }

  async getV1AkkiBillingPlans(): Promise<unknown> {
    return this._request('GET', '/v1/akki/billing/plans');
  }

  async getV1AkkiBillingStatusBysession_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/billing/status/{session_id}');
  }

  async getV1AkkiBlogAdminPostsByslug(): Promise<unknown> {
    return this._request('GET', '/v1/akki/blog/admin/posts/{slug}');
  }

  async postV1AkkiBlogCompose(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/blog/compose', body);
  }

  async postV1AkkiBlogCronWeekly(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/blog/cron/weekly', body);
  }

  async getV1AkkiBlogPosts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/blog/posts');
  }

  async deleteV1AkkiBlogPostsByslug(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/blog/posts/{slug}');
  }

  async getV1AkkiBlogPostsByslug(): Promise<unknown> {
    return this._request('GET', '/v1/akki/blog/posts/{slug}');
  }

  async postV1AkkiBlogPostsByslugPublish(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/blog/posts/{slug}/publish', body);
  }

  async getV1AkkiBlogRss(): Promise<unknown> {
    return this._request('GET', '/v1/akki/blog/rss');
  }

  async postV1AkkiBlogSeedLaunch_10(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/blog/seed/launch-10', body);
  }

  async postV1AkkiBlogSubscribe(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/blog/subscribe', body);
  }

  async getV1AkkiBlogSubscribers(): Promise<unknown> {
    return this._request('GET', '/v1/akki/blog/subscribers');
  }

  async getV1AkkiChatModels(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chat/models');
  }

  async getV1AkkiChats(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats');
  }

  async postV1AkkiChats(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/chats', body);
  }

  async getV1AkkiChatsArchived(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/archived');
  }

  async getV1AkkiChatsSearch(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/search');
  }

  async deleteV1AkkiChatsBychat_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/chats/{chat_id}');
  }

  async getV1AkkiChatsBychat_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/{chat_id}');
  }

  async patchV1AkkiChatsBychat_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/chats/{chat_id}', body);
  }

  async postV1AkkiChatsBychat_idAttach(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/chats/{chat_id}/attach', body);
  }

  async getV1AkkiChatsBychat_idAudit(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/{chat_id}/audit');
  }

  async getV1AkkiChatsBychat_idAudit_panel(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/{chat_id}/audit-panel');
  }

  async getV1AkkiChatsBychat_idAudit_panelAggregate(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/{chat_id}/audit-panel/aggregate');
  }

  async getV1AkkiChatsBychat_idAuditExport_zip(): Promise<unknown> {
    return this._request('GET', '/v1/akki/chats/{chat_id}/audit/export.zip');
  }

  async postV1AkkiChatsBychat_idGovernanceSolva_escalation_clicked(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/chats/{chat_id}/governance/solva-escalation-clicked', body);
  }

  async postV1AkkiChatsBychat_idMessages(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/chats/{chat_id}/messages', body);
  }

  async postV1AkkiChatsBychat_idMessagesStream(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/chats/{chat_id}/messages/stream', body);
  }

  async deleteV1AkkiChatsBychat_idPermanent(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/chats/{chat_id}/permanent');
  }

  async postV1AkkiChatsBychat_idRestore(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/chats/{chat_id}/restore', body);
  }

  async postV1AkkiCohortApplications(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/cohort/applications', body);
  }

  async postV1AkkiCohortEmail_eventsSendgrid(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/cohort/email-events/sendgrid', body);
  }

  async postV1AkkiCohortWaitlist(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/cohort/waitlist', body);
  }

  async postV1AkkiContexts(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts', body);
  }

  async postV1AkkiContextsBycidDocumentsBydoc_idExtract_events(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{cid}/documents/{doc_id}/extract-events', body);
  }

  async getV1AkkiContextsBycidEvents(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{cid}/events');
  }

  async postV1AkkiContextsBycidEvents(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{cid}/events', body);
  }

  async postV1AkkiContextsBycidEventsSync_calendar(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{cid}/events/sync-calendar', body);
  }

  async deleteV1AkkiContextsBycidEventsByevent_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{cid}/events/{event_id}');
  }

  async getV1AkkiContextsBycidEventsByevent_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{cid}/events/{event_id}');
  }

  async patchV1AkkiContextsBycidEventsByevent_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{cid}/events/{event_id}', body);
  }

  async getV1AkkiContextsBycidOauthCalendarStatus(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{cid}/oauth/calendar/status');
  }

  async postV1AkkiContextsBycidOauthGoogleDisconnect(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{cid}/oauth/google/disconnect', body);
  }

  async deleteV1AkkiContextsBycontext_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}');
  }

  async getV1AkkiContextsBycontext_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}');
  }

  async patchV1AkkiContextsBycontext_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}', body);
  }

  async getV1AkkiContextsBycontext_idActivityRecent(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/activity/recent');
  }

  async getV1AkkiContextsBycontext_idAgenda_evolution(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/agenda-evolution');
  }

  async getV1AkkiContextsBycontext_idAudit_log(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/audit-log');
  }

  async getV1AkkiContextsBycontext_idBoardpacks(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/boardpacks');
  }

  async getV1AkkiContextsBycontext_idBoardpacksBybpid(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/boardpacks/{bpid}');
  }

  async postV1AkkiContextsBycontext_idBoardpacksBybpidRegenerate_commentary(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/boardpacks/{bpid}/regenerate-commentary', body);
  }

  async getV1AkkiContextsBycontext_idBriefings(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefings');
  }

  async postV1AkkiContextsBycontext_idBriefings(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/briefings', body);
  }

  async getV1AkkiContextsBycontext_idBriefingsAggregates(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefings/aggregates');
  }

  async getV1AkkiContextsBycontext_idBriefingsAggregatesByaggregate_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefings/aggregates/{aggregate_id}');
  }

  async deleteV1AkkiContextsBycontext_idBriefingsBybriefing_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/briefings/{briefing_id}');
  }

  async getV1AkkiContextsBycontext_idBriefingsBybriefing_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefings/{briefing_id}');
  }

  async getV1AkkiContextsBycontext_idBriefingsBybriefing_idExport(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefings/{briefing_id}/export');
  }

  async postV1AkkiContextsBycontext_idBriefingsBybriefing_idMark_read(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/briefings/{briefing_id}/mark-read', body);
  }

  async postV1AkkiContextsBycontext_idBriefingsBybriefing_idSpeaking_notes(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/briefings/{briefing_id}/speaking-notes', body);
  }

  async getV1AkkiContextsBycontext_idBriefs(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefs');
  }

  async postV1AkkiContextsBycontext_idBriefs(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/briefs', body);
  }

  async deleteV1AkkiContextsBycontext_idBriefsBybrief_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/briefs/{brief_id}');
  }

  async getV1AkkiContextsBycontext_idBriefsBybrief_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/briefs/{brief_id}');
  }

  async getV1AkkiContextsBycontext_idChecklists(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/checklists');
  }

  async postV1AkkiContextsBycontext_idChecklistsDispatch(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/checklists/dispatch', body);
  }

  async postV1AkkiContextsBycontext_idChecklistsGenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/checklists/generate', body);
  }

  async patchV1AkkiContextsBycontext_idChecklistsBycid(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/checklists/{cid}', body);
  }

  async deleteV1AkkiContextsBycontext_idCommentsBycomment_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/comments/{comment_id}');
  }

  async getV1AkkiContextsBycontext_idCommittees(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/committees');
  }

  async postV1AkkiContextsBycontext_idCommittees(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/committees', body);
  }

  async deleteV1AkkiContextsBycontext_idCommitteesBycommittee_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/committees/{committee_id}');
  }

  async patchV1AkkiContextsBycontext_idCommitteesBycommittee_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/committees/{committee_id}', body);
  }

  async getV1AkkiContextsBycontext_idContext_object(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/context-object');
  }

  async postV1AkkiContextsBycontext_idContext_object(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/context-object', body);
  }

  async deleteV1AkkiContextsBycontext_idCycle_assignmentsByassignment_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/cycle-assignments/{assignment_id}');
  }

  async getV1AkkiContextsBycontext_idCycleActions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/actions');
  }

  async getV1AkkiContextsBycontext_idCycleAgenda(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/agenda');
  }

  async postV1AkkiContextsBycontext_idCycleAgenda(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/agenda', body);
  }

  async getV1AkkiContextsBycontext_idCycleCommittees(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/committees');
  }

  async getV1AkkiContextsBycontext_idCycleContributions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/contributions');
  }

  async postV1AkkiContextsBycontext_idCycleContributions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/contributions', body);
  }

  async postV1AkkiContextsBycontext_idCycleContributionsBycontribution_idScore(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/contributions/{contribution_id}/score', body);
  }

  async postV1AkkiContextsBycontext_idCycleDraft_compilation(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/draft-compilation', body);
  }

  async postV1AkkiContextsBycontext_idCycleDraft_compilationStream(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/draft-compilation/stream', body);
  }

  async getV1AkkiContextsBycontext_idCycleFollow_ups(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/follow-ups');
  }

  async postV1AkkiContextsBycontext_idCycleFollow_upsDraft(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/follow-ups/draft', body);
  }

  async postV1AkkiContextsBycontext_idCycleFollow_upsByfollowup_idApprove(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/follow-ups/{followup_id}/approve', body);
  }

  async postV1AkkiContextsBycontext_idCycleFollow_upsByfollowup_idSend(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/follow-ups/{followup_id}/send', body);
  }

  async getV1AkkiContextsBycontext_idCycleReadiness(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/readiness');
  }

  async deleteV1AkkiContextsBycontext_idCycleSchedule(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/cycle/schedule');
  }

  async getV1AkkiContextsBycontext_idCycleSchedule(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/schedule');
  }

  async putV1AkkiContextsBycontext_idCycleSchedule(body?: unknown): Promise<unknown> {
    return this._request('PUT', '/v1/akki/contexts/{context_id}/cycle/schedule', body);
  }

  async getV1AkkiContextsBycontext_idCycleTeam(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycle/team');
  }

  async postV1AkkiContextsBycontext_idCycleTeam(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycle/team', body);
  }

  async deleteV1AkkiContextsBycontext_idCycleTeamBymember_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/cycle/team/{member_id}');
  }

  async patchV1AkkiContextsBycontext_idCycleTeamBymember_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/cycle/team/{member_id}', body);
  }

  async getV1AkkiContextsBycontext_idCycles(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycles');
  }

  async postV1AkkiContextsBycontext_idCycles(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles', body);
  }

  async getV1AkkiContextsBycontext_idCyclesBycycle_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}');
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idActivate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/activate', body);
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idAgenda_itemsByagenda_item_idCheck_team_duplicate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/agenda-items/{agenda_item_id}/check-team-duplicate', body);
  }

  async getV1AkkiContextsBycontext_idCyclesBycycle_idAgenda_itemsByagenda_item_idEligible_contributors(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/agenda-items/{agenda_item_id}/eligible-contributors');
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idApply_template(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/apply-template', body);
  }

  async getV1AkkiContextsBycontext_idCyclesBycycle_idBriefsBybrief_idAssignments(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/briefs/{brief_id}/assignments');
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idBriefsBybrief_idAssignments(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/briefs/{brief_id}/assignments', body);
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idBriefsBybrief_idSubmit_for_board(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/briefs/{brief_id}/submit-for-board', body);
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idClose(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/close', body);
  }

  async getV1AkkiContextsBycontext_idCyclesBycycle_idQuestions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/questions');
  }

  async postV1AkkiContextsBycontext_idCyclesBycycle_idQuestions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/cycles/{cycle_id}/questions', body);
  }

  async getV1AkkiContextsBycontext_idDecks(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/decks');
  }

  async postV1AkkiContextsBycontext_idDecksOutline(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/decks/outline', body);
  }

  async getV1AkkiContextsBycontext_idDecksBydeck_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/decks/{deck_id}');
  }

  async postV1AkkiContextsBycontext_idDecksBydeck_idFeedback(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/decks/{deck_id}/feedback', body);
  }

  async postV1AkkiContextsBycontext_idDecksBydeck_idQuality_check(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/decks/{deck_id}/quality_check', body);
  }

  async postV1AkkiContextsBycontext_idDecksByoutline_idGenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/decks/{outline_id}/generate', body);
  }

  async postV1AkkiContextsBycontext_idDecksByoutline_idGenerateStream(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/decks/{outline_id}/generate/stream', body);
  }

  async getV1AkkiContextsBycontext_idDocument_journal(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/document-journal');
  }

  async getV1AkkiContextsBycontext_idDocument_journalRecent(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/document-journal/recent');
  }

  async getV1AkkiContextsBycontext_idDocument_journalSearch(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/document-journal/search');
  }

  async getV1AkkiContextsBycontext_idDocuments(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents');
  }

  async postV1AkkiContextsBycontext_idDocuments(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents', body);
  }

  async getV1AkkiContextsBycontext_idDocumentsDrafts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/drafts');
  }

  async postV1AkkiContextsBycontext_idDocumentsGenerate_meta(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/generate-meta', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsGenerate_metaAsync(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/generate-meta/async', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsManual_create(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/manual-create', body);
  }

  async deleteV1AkkiContextsBycontext_idDocumentsBydoc_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/documents/{doc_id}');
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}');
  }

  async patchV1AkkiContextsBycontext_idDocumentsBydoc_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/documents/{doc_id}', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idBriefingsGenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/briefings/generate', body);
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idDownload(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/download');
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idEngagement(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/engagement');
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idEvolution_diff(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/evolution-diff', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idEvolution_diffAsync(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/evolution-diff/async', body);
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idExport_guard(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/export-guard');
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idExtract(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/extract', body);
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idIntelligence(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/intelligence');
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idIntelligenceRegenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/intelligence/regenerate', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idJournal_commentary(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/journal-commentary', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idJournal_commentaryAsync(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/journal-commentary/async', body);
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idParagraphs(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/paragraphs');
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idParagraphsBypidOriginal(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/paragraphs/{pid}/original');
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idRelated(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/related');
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idShare(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/share', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idSummary(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/summary', body);
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idSummaryAsync(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/summary/async', body);
  }

  async getV1AkkiContextsBycontext_idDocumentsBydoc_idThread(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/documents/{doc_id}/thread');
  }

  async postV1AkkiContextsBycontext_idDocumentsBydoc_idView(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/documents/{doc_id}/view', body);
  }

  async postV1AkkiContextsBycontext_idEventsSync_calendarStream(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/events/sync-calendar/stream', body);
  }

  async getV1AkkiContextsBycontext_idExco_teams(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/exco-teams');
  }

  async postV1AkkiContextsBycontext_idExco_teams(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/exco-teams', body);
  }

  async deleteV1AkkiContextsBycontext_idExco_teamsByteam_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/exco-teams/{team_id}');
  }

  async getV1AkkiContextsBycontext_idExco_teamsByteam_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/exco-teams/{team_id}');
  }

  async patchV1AkkiContextsBycontext_idExco_teamsByteam_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/exco-teams/{team_id}', body);
  }

  async postV1AkkiContextsBycontext_idExco_teamsByteam_idMembers(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/exco-teams/{team_id}/members', body);
  }

  async deleteV1AkkiContextsBycontext_idExco_teamsByteam_idMembersBymember_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/exco-teams/{team_id}/members/{member_id}');
  }

  async postV1AkkiContextsBycontext_idExport(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/export', body);
  }

  async getV1AkkiContextsBycontext_idHomeComing_up(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/home/coming-up');
  }

  async getV1AkkiContextsBycontext_idHomeInsights(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/home/insights');
  }

  async getV1AkkiContextsBycontext_idHomeWhats_new(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/home/whats-new');
  }

  async getV1AkkiContextsBycontext_idInbound_queue(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/inbound-queue');
  }

  async getV1AkkiContextsBycontext_idInbound_queueByqueue_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/inbound-queue/{queue_id}');
  }

  async postV1AkkiContextsBycontext_idInbound_queueByqueue_idAccept(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/inbound-queue/{queue_id}/accept', body);
  }

  async postV1AkkiContextsBycontext_idInbound_queueByqueue_idReject(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/inbound-queue/{queue_id}/reject', body);
  }

  async getV1AkkiContextsBycontext_idInfluence_map(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/influence-map');
  }

  async postV1AkkiContextsBycontext_idInfluence_mapDigest(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/influence-map/digest', body);
  }

  async getV1AkkiContextsBycontext_idInvitations(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/invitations');
  }

  async postV1AkkiContextsBycontext_idInvitations(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/invitations', body);
  }

  async deleteV1AkkiContextsBycontext_idInvitationsByinvitation_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/invitations/{invitation_id}');
  }

  async postV1AkkiContextsBycontext_idLeave(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/leave', body);
  }

  async getV1AkkiContextsBycontext_idLensCoachSessions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/lens/coach/sessions');
  }

  async postV1AkkiContextsBycontext_idLensCoachSessions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/lens/coach/sessions', body);
  }

  async deleteV1AkkiContextsBycontext_idLensCoachSessionsBysid(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/lens/coach/sessions/{sid}');
  }

  async getV1AkkiContextsBycontext_idLensCoachSessionsBysid(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/lens/coach/sessions/{sid}');
  }

  async postV1AkkiContextsBycontext_idLensCoachSessionsBysidMessages(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/lens/coach/sessions/{sid}/messages', body);
  }

  async postV1AkkiContextsBycontext_idLensRun(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/lens/run', body);
  }

  async getV1AkkiContextsBycontext_idLensRuns(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/lens/runs');
  }

  async deleteV1AkkiContextsBycontext_idLensRunsByrun_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/lens/runs/{run_id}');
  }

  async getV1AkkiContextsBycontext_idLensRunsByrun_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/lens/runs/{run_id}');
  }

  async postV1AkkiContextsBycontext_idLlmProbe(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/llm/probe', body);
  }

  async getV1AkkiContextsBycontext_idMembers(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/members');
  }

  async deleteV1AkkiContextsBycontext_idMembersByaccount_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/members/{account_id}');
  }

  async getV1AkkiContextsBycontext_idMentions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/mentions');
  }

  async postV1AkkiContextsBycontext_idMentionsBymention_idRead(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/mentions/{mention_id}/read', body);
  }

  async getV1AkkiContextsBycontext_idMinutes(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/minutes');
  }

  async postV1AkkiContextsBycontext_idMinutesBydoc_idExtract(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/minutes/{doc_id}/extract', body);
  }

  async postV1AkkiContextsBycontext_idMinutesBydoc_idNarrative(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/minutes/{doc_id}/narrative', body);
  }

  async postV1AkkiContextsBycontext_idMinutesBydoc_idTo_cycle(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/minutes/{doc_id}/to_cycle', body);
  }

  async getV1AkkiContextsBycontext_idMonitor(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/monitor');
  }

  async getV1AkkiContextsBycontext_idMonitorAuto_suggest_objectives(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/monitor/auto-suggest-objectives');
  }

  async getV1AkkiContextsBycontext_idMonitorAuto_suggest_projects(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/monitor/auto-suggest-projects');
  }

  async getV1AkkiContextsBycontext_idMonitorOwner_roles(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/monitor/owner-roles');
  }

  async getV1AkkiContextsBycontext_idMonitorBykind(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/monitor/{kind}');
  }

  async postV1AkkiContextsBycontext_idMonitorBykind(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/monitor/{kind}', body);
  }

  async deleteV1AkkiContextsBycontext_idMonitorBykindByrid(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/monitor/{kind}/{rid}');
  }

  async getV1AkkiContextsBycontext_idMonitorBykindByrid(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/monitor/{kind}/{rid}');
  }

  async patchV1AkkiContextsBycontext_idMonitorBykindByrid(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/monitor/{kind}/{rid}', body);
  }

  async postV1AkkiContextsBycontext_idMonitorBykindByridUpdate_status(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/monitor/{kind}/{rid}/update-status', body);
  }

  async getV1AkkiContextsBycontext_idPipelineEvents(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/pipeline/events');
  }

  async postV1AkkiContextsBycontext_idPipelineRun(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pipeline/run', body);
  }

  async getV1AkkiContextsBycontext_idPulseAcross_boards(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/pulse/across-boards');
  }

  async getV1AkkiContextsBycontext_idPulseFeed(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/pulse/feed');
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idBookmark(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/bookmark', body);
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idComment(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/comment', body);
  }

  async deleteV1AkkiContextsBycontext_idPulseSignalsBysignal_idCommentsBycomment_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/comments/{comment_id}');
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idResolve(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/resolve', body);
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idSave(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/save', body);
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idShare(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/share', body);
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idTake_to_solva(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/take-to-solva', body);
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idUnbookmark(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/unbookmark', body);
  }

  async postV1AkkiContextsBycontext_idPulseSignalsBysignal_idUnresolve(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/pulse/signals/{signal_id}/unresolve', body);
  }

  async getV1AkkiContextsBycontext_idQuestions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/questions');
  }

  async postV1AkkiContextsBycontext_idQuestions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions', body);
  }

  async postV1AkkiContextsBycontext_idQuestionsSeed_from_briefings(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions/seed-from-briefings', body);
  }

  async patchV1AkkiContextsBycontext_idQuestionsByqid(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/questions/{qid}', body);
  }

  async getV1AkkiContextsBycontext_idQuestionsByquestion_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/questions/{question_id}');
  }

  async postV1AkkiContextsBycontext_idQuestionsByquestion_idAnswer(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions/{question_id}/answer', body);
  }

  async postV1AkkiContextsBycontext_idQuestionsByquestion_idLink_response(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions/{question_id}/link-response', body);
  }

  async postV1AkkiContextsBycontext_idQuestionsByquestion_idMark_answered(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions/{question_id}/mark-answered', body);
  }

  async postV1AkkiContextsBycontext_idQuestionsByquestion_idReopen(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions/{question_id}/reopen', body);
  }

  async postV1AkkiContextsBycontext_idQuestionsByquestion_idShare(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/questions/{question_id}/share', body);
  }

  async getV1AkkiContextsBycontext_idQuick_actionsOrder(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/quick-actions/order');
  }

  async postV1AkkiContextsBycontext_idQuick_actionsByaction_keyClicked(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/quick-actions/{action_key}/clicked', body);
  }

  async getV1AkkiContextsBycontext_idReportees(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/reportees');
  }

  async postV1AkkiContextsBycontext_idReportees(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/reportees', body);
  }

  async deleteV1AkkiContextsBycontext_idReporteesByrid(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/reportees/{rid}');
  }

  async getV1AkkiContextsBycontext_idReports(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/reports');
  }

  async postV1AkkiContextsBycontext_idReportsCompose(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/reports/compose', body);
  }

  async getV1AkkiContextsBycontext_idReportsByrid(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/reports/{rid}');
  }

  async patchV1AkkiContextsBycontext_idReportsByrid(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/reports/{rid}', body);
  }

  async getV1AkkiContextsBycontext_idReportsByridExport_deck_pdf(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/reports/{rid}/export.deck.pdf');
  }

  async getV1AkkiContextsBycontext_idReportsByridExport_pdf(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/reports/{rid}/export.pdf');
  }

  async postV1AkkiContextsBycontext_idReportsByridPolish(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/reports/{rid}/polish', body);
  }

  async postV1AkkiContextsBycontext_idReportsByridReview(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/reports/{rid}/review', body);
  }

  async postV1AkkiContextsBycontext_idReportsByridSend_up(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/reports/{rid}/send_up', body);
  }

  async postV1AkkiContextsBycontext_idShares(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/shares', body);
  }

  async postV1AkkiContextsBycontext_idSimulate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/simulate', body);
  }

  async getV1AkkiContextsBycontext_idSimulations(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/simulations');
  }

  async deleteV1AkkiContextsBycontext_idSimulationsBysimulation_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/simulations/{simulation_id}');
  }

  async getV1AkkiContextsBycontext_idSimulationsBysimulation_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/simulations/{simulation_id}');
  }

  async getV1AkkiContextsBycontext_idStrategic_goals(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/strategic-goals');
  }

  async postV1AkkiContextsBycontext_idStrategic_goals(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/strategic-goals', body);
  }

  async postV1AkkiContextsBycontext_idStrategic_goalsExtract(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/strategic-goals/extract', body);
  }

  async deleteV1AkkiContextsBycontext_idStrategic_goalsBygoal_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/strategic-goals/{goal_id}');
  }

  async patchV1AkkiContextsBycontext_idStrategic_goalsBygoal_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/strategic-goals/{goal_id}', body);
  }

  async getV1AkkiContextsBycontext_idStrategic_goalsBygoal_idEvolution(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/strategic-goals/{goal_id}/evolution');
  }

  async postV1AkkiContextsBycontext_idStrategic_goalsBygoal_idUpdate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/strategic-goals/{goal_id}/update', body);
  }

  async postV1AkkiContextsBycontext_idStudioBackfill_sensitivity(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/studio/backfill_sensitivity', body);
  }

  async getV1AkkiContextsBycontext_idStudioHistory(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/studio/history');
  }

  async getV1AkkiContextsBycontext_idStudioBykindByartefact_idEngagement(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/studio/{kind}/{artefact_id}/engagement');
  }

  async postV1AkkiContextsBycontext_idStudioBykindByartefact_idRescore(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/studio/{kind}/{artefact_id}/rescore', body);
  }

  async postV1AkkiContextsBycontext_idStudioBykindByartefact_idShare(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/studio/{kind}/{artefact_id}/share', body);
  }

  async postV1AkkiContextsBycontext_idStudioBykindByartefact_idShare_email(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/studio/{kind}/{artefact_id}/share-email', body);
  }

  async postV1AkkiContextsBycontext_idStudioBykindByartefact_idView(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/studio/{kind}/{artefact_id}/view', body);
  }

  async getV1AkkiContextsBycontext_idSubmissions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/submissions');
  }

  async getV1AkkiContextsBycontext_idTasks_initiatives(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/tasks-initiatives');
  }

  async postV1AkkiContextsBycontext_idTasks_initiatives(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/tasks-initiatives', body);
  }

  async deleteV1AkkiContextsBycontext_idTasks_initiativesByti_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/tasks-initiatives/{ti_id}');
  }

  async getV1AkkiContextsBycontext_idTasks_initiativesByti_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/tasks-initiatives/{ti_id}');
  }

  async patchV1AkkiContextsBycontext_idTasks_initiativesByti_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/tasks-initiatives/{ti_id}', body);
  }

  async getV1AkkiContextsBycontext_idTeam_catalogue(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/team-catalogue');
  }

  async postV1AkkiContextsBycontext_idTeam_catalogue(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/team-catalogue', body);
  }

  async deleteV1AkkiContextsBycontext_idTeam_catalogueBymember_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/team-catalogue/{member_id}');
  }

  async patchV1AkkiContextsBycontext_idTeam_catalogueBymember_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/team-catalogue/{member_id}', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioArtefacts(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/artefacts', body);
  }

  async getV1AkkiContextsBycontext_idWork_studioCompilations(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/compilations');
  }

  async postV1AkkiContextsBycontext_idWork_studioCompilations(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/compilations', body);
  }

  async getV1AkkiContextsBycontext_idWork_studioCompilationsBycompilation_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/compilations/{compilation_id}');
  }

  async postV1AkkiContextsBycontext_idWork_studioCompilationsBycompilation_idStart(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/compilations/{compilation_id}/start', body);
  }

  async getV1AkkiContextsBycontext_idWork_studioDocuments(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/documents');
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsSave_draft(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/save-draft', body);
  }

  async deleteV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}');
  }

  async getV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}');
  }

  async patchV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idCommit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/commit', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idCreate_new_version(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/create-new-version', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idMove_to_review(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/move-to-review', body);
  }

  async getV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idRender(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/render');
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idRevise(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/revise', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idSave(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/save', body);
  }

  async getV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idVersions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/versions');
  }

  async getV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idVersionsByversion_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/versions/{version_id}');
  }

  async postV1AkkiContextsBycontext_idWork_studioDocumentsByartefact_idVersionsByversion_idRestore(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/documents/{artefact_id}/versions/{version_id}/restore', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioEnhanceBykind(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/enhance/{kind}', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioEnhanceBykindStream(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/enhance/{kind}/stream', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioExportBykind(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/export/{kind}', body);
  }

  async getV1AkkiContextsBycontext_idWork_studioExportsByexport_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/exports/{export_id}');
  }

  async getV1AkkiContextsBycontext_idWork_studioExportsByexport_idDownload(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/exports/{export_id}/download');
  }

  async getV1AkkiContextsBycontext_idWork_studioExportsByexport_idStream(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/work-studio/exports/{export_id}/stream');
  }

  async postV1AkkiContextsBycontext_idWork_studioFrom_document(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/from-document', body);
  }

  async postV1AkkiContextsBycontext_idWork_studioFrom_source(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/work-studio/from-source', body);
  }

  async getV1AkkiContextsBycontext_idByartefact_typeByartefact_idComments(): Promise<unknown> {
    return this._request('GET', '/v1/akki/contexts/{context_id}/{artefact_type}/{artefact_id}/comments');
  }

  async postV1AkkiContextsBycontext_idByartefact_typeByartefact_idComments(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/contexts/{context_id}/{artefact_type}/{artefact_id}/comments', body);
  }

  async postV1AkkiCronParagraph_anchors_sweep(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/cron/paragraph-anchors-sweep', body);
  }

  async postV1AkkiCronWeekly_digest(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/cron/weekly-digest', body);
  }

  async getV1AkkiCsrf(): Promise<unknown> {
    return this._request('GET', '/v1/akki/csrf');
  }

  async postV1AkkiCycleCronRun_schedules(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/cycle/cron/run-schedules', body);
  }

  async getV1AkkiDecksBydeck_idContext(): Promise<unknown> {
    return this._request('GET', '/v1/akki/decks/{deck_id}/context');
  }

  async getV1AkkiDocsBundle_zip(): Promise<unknown> {
    return this._request('GET', '/v1/akki/docs/bundle.zip');
  }

  async getV1AkkiDocsDevelopment(): Promise<unknown> {
    return this._request('GET', '/v1/akki/docs/development');
  }

  async getV1AkkiDocsProduct(): Promise<unknown> {
    return this._request('GET', '/v1/akki/docs/product');
  }

  async postV1AkkiDocumentsBydoc_idAttachments(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/documents/{doc_id}/attachments', body);
  }

  async deleteV1AkkiDocumentsBydoc_idAttachmentsByattachment_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/documents/{doc_id}/attachments/{attachment_id}');
  }

  async patchV1AkkiDocumentsBydoc_idLineage(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/documents/{doc_id}/lineage', body);
  }

  async postV1AkkiDocumentsBydoc_idPrompted_edit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/documents/{doc_id}/prompted-edit', body);
  }

  async postV1AkkiEarly_accessRegister(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/early-access/register', body);
  }

  async getV1AkkiEarly_accessRegistrations(): Promise<unknown> {
    return this._request('GET', '/v1/akki/early-access/registrations');
  }

  async postV1AkkiEnterpriseInterest(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/enterprise/interest', body);
  }

  async getV1AkkiEnterpriseInterestMe(): Promise<unknown> {
    return this._request('GET', '/v1/akki/enterprise/interest/me');
  }

  async postV1AkkiEvents(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/events', body);
  }

  async postV1AkkiFeedback(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/feedback', body);
  }

  async getV1AkkiHealth(): Promise<unknown> {
    return this._request('GET', '/v1/akki/health');
  }

  async getV1AkkiHealthComposite(): Promise<unknown> {
    return this._request('GET', '/v1/akki/health/composite');
  }

  async getV1AkkiHelpFeatures(): Promise<unknown> {
    return this._request('GET', '/v1/akki/help/features');
  }

  async getV1AkkiHelpFeatures_md(): Promise<unknown> {
    return this._request('GET', '/v1/akki/help/features.md');
  }

  async getV1AkkiIdeasDigestCurrent(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ideas/digest/current');
  }

  async getV1AkkiIdeasDigestHistory(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ideas/digest/history');
  }

  async postV1AkkiIdeasDigestRegenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ideas/digest/regenerate', body);
  }

  async getV1AkkiIdeasDigestByweek_iso(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ideas/digest/{week_iso}');
  }

  async getV1AkkiIdeasPreferences(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ideas/preferences');
  }

  async putV1AkkiIdeasPreferences(body?: unknown): Promise<unknown> {
    return this._request('PUT', '/v1/akki/ideas/preferences', body);
  }

  async getV1AkkiInboundAddress(): Promise<unknown> {
    return this._request('GET', '/v1/akki/inbound/address');
  }

  async postV1AkkiInboundPostmark(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/inbound/postmark', body);
  }

  async postV1AkkiInboundSendgrid(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/inbound/sendgrid', body);
  }

  async getV1AkkiInboxMessagesBymessage_idPreview(): Promise<unknown> {
    return this._request('GET', '/v1/akki/inbox/messages/{message_id}/preview');
  }

  async getV1AkkiInvitationsBy_tokenBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/invitations/by-token/{token}');
  }

  async postV1AkkiInvitationsBytokenAccept(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/invitations/{token}/accept', body);
  }

  async getV1AkkiJobsByjob_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/jobs/{job_id}');
  }

  async postV1AkkiLearnResearch(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/learn/research', body);
  }

  async getV1AkkiLensCatalog(): Promise<unknown> {
    return this._request('GET', '/v1/akki/lens/catalog');
  }

  async getV1AkkiLlmQuota(): Promise<unknown> {
    return this._request('GET', '/v1/akki/llm/quota');
  }

  async postV1AkkiMeActive_context(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/active-context', body);
  }

  async getV1AkkiMeBoards_to_watch(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/boards-to-watch');
  }

  async getV1AkkiMeCompany_homeAttention(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/company-home/attention');
  }

  async getV1AkkiMeCompany_homeReadiness(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/company-home/readiness');
  }

  async getV1AkkiMeCompany_homeTop_signals(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/company-home/top-signals');
  }

  async getV1AkkiMeContexts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/contexts');
  }

  async getV1AkkiMeCopyByslot(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/copy/{slot}');
  }

  async postV1AkkiMeDelete_account(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/delete-account', body);
  }

  async postV1AkkiMeDelete_accountCancel(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/delete-account/cancel', body);
  }

  async getV1AkkiMeDepth_status(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/depth-status');
  }

  async postV1AkkiMeDepth_statusDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/depth-status/dismiss', body);
  }

  async postV1AkkiMeEarly_access_opt_in(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/early-access-opt-in', body);
  }

  async getV1AkkiMeFirst_session(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/first-session');
  }

  async postV1AkkiMeFirst_sessionChoose_door(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/first-session/choose-door', body);
  }

  async postV1AkkiMeFirst_sessionComplete(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/first-session/complete', body);
  }

  async postV1AkkiMeFirst_sessionIntake(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/first-session/intake', body);
  }

  async postV1AkkiMeFirst_sessionSkip(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/first-session/skip', body);
  }

  async postV1AkkiMeFirst_sessionStart(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/first-session/start', body);
  }

  async getV1AkkiMeHomeStream(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/home/stream');
  }

  async getV1AkkiMeInbound_queueCounts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/inbound-queue/counts');
  }

  async getV1AkkiMeLast_action(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/last-action');
  }

  async getV1AkkiMeOnboarding_briefs(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/onboarding-briefs');
  }

  async postV1AkkiMeOnboarding_briefsComplete(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/onboarding-briefs/complete', body);
  }

  async getV1AkkiMePortfolio(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/portfolio');
  }

  async getV1AkkiMePortfolio_metrics(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/portfolio-metrics');
  }

  async getV1AkkiMeProfile(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/profile');
  }

  async patchV1AkkiMeProfile(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/me/profile', body);
  }

  async getV1AkkiMeQuestions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/questions');
  }

  async getV1AkkiMeRecent_views(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/recent-views');
  }

  async postV1AkkiMeRecent_views(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/recent-views', body);
  }

  async getV1AkkiMeReview_queue(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/review-queue');
  }

  async getV1AkkiMeReview_queueCounts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/review-queue/counts');
  }

  async postV1AkkiMeReview_queueItemsBykindByitem_idApprove(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/review-queue/items/{kind}/{item_id}/approve', body);
  }

  async postV1AkkiMeReview_queueItemsBykindByitem_idEdit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/review-queue/items/{kind}/{item_id}/edit', body);
  }

  async postV1AkkiMeReview_queueItemsBykindByitem_idReject(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/review-queue/items/{kind}/{item_id}/reject', body);
  }

  async getV1AkkiMeRole_probe(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/role-probe');
  }

  async getV1AkkiMeRole_probeExecutive(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/role-probe/executive');
  }

  async getV1AkkiMeRole_probeNed(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/role-probe/ned');
  }

  async getV1AkkiMeSharesInbox(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/shares/inbox');
  }

  async getV1AkkiMeSharesOutbox(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/shares/outbox');
  }

  async getV1AkkiMeSpecial_ask(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/special-ask');
  }

  async postV1AkkiMeSpecial_ask(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/special-ask', body);
  }

  async postV1AkkiMeSpecial_askDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/special-ask/dismiss', body);
  }

  async postV1AkkiMeSpecial_askSurface_ack(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/me/special-ask/surface-ack', body);
  }

  async getV1AkkiMeSubmitted_briefs(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/submitted-briefs');
  }

  async getV1AkkiMeTrial_status(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/trial-status');
  }

  async getV1AkkiMeTrial_statusBy_accountByaccount_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/me/trial-status/by-account/{account_id}');
  }

  async postV1AkkiNedAssignmentsByassignment_idAccept(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/assignments/{assignment_id}/accept', body);
  }

  async postV1AkkiNedAssignmentsByassignment_idDecline(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/assignments/{assignment_id}/decline', body);
  }

  async getV1AkkiNedCommitteeBycontext_idBycommittee(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ned/committee/{context_id}/{committee}');
  }

  async getV1AkkiNedInboxAssignments(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ned/inbox/assignments');
  }

  async getV1AkkiNedLanding(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ned/landing');
  }

  async postV1AkkiNedMeetings(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/meetings', body);
  }

  async deleteV1AkkiNedMeetingsBymeeting_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/ned/meetings/{meeting_id}');
  }

  async getV1AkkiNedMeetingsBymeeting_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ned/meetings/{meeting_id}');
  }

  async patchV1AkkiNedMeetingsBymeeting_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/ned/meetings/{meeting_id}', body);
  }

  async postV1AkkiNedMeetingsBymeeting_idFollowups(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/meetings/{meeting_id}/followups', body);
  }

  async postV1AkkiNedMeetingsBymeeting_idFollowupsByfidSend(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/meetings/{meeting_id}/followups/{fid}/send', body);
  }

  async postV1AkkiNedMeetingsBymeeting_idNotes(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/meetings/{meeting_id}/notes', body);
  }

  async deleteV1AkkiNedMeetingsBymeeting_idNotesBynote_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/ned/meetings/{meeting_id}/notes/{note_id}');
  }

  async postV1AkkiNedMeetingsBymeeting_idPositions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/ned/meetings/{meeting_id}/positions', body);
  }

  async getV1AkkiNedSearch(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ned/search');
  }

  async getV1AkkiNews(): Promise<unknown> {
    return this._request('GET', '/v1/akki/news');
  }

  async postV1AkkiNotify_billing_launch(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/notify-billing-launch', body);
  }

  async getV1AkkiOauthGoogleCallback(): Promise<unknown> {
    return this._request('GET', '/v1/akki/oauth/google/callback');
  }

  async getV1AkkiOauthGoogleConnect(): Promise<unknown> {
    return this._request('GET', '/v1/akki/oauth/google/connect');
  }

  async getV1AkkiObservabilityReasoning_velocity(): Promise<unknown> {
    return this._request('GET', '/v1/akki/observability/reasoning_velocity');
  }

  async getV1AkkiPrepareBrief_kinds(): Promise<unknown> {
    return this._request('GET', '/v1/akki/prepare/brief-kinds');
  }

  async getV1AkkiPresetsIndustries(): Promise<unknown> {
    return this._request('GET', '/v1/akki/presets/industries');
  }

  async getV1AkkiPresetsJurisdictions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/presets/jurisdictions');
  }

  async getV1AkkiProduct_features(): Promise<unknown> {
    return this._request('GET', '/v1/akki/product-features');
  }

  async getV1AkkiProduct_features_md(): Promise<unknown> {
    return this._request('GET', '/v1/akki/product-features.md');
  }

  async getV1AkkiPublicObservabilityReasoning_velocity(): Promise<unknown> {
    return this._request('GET', '/v1/akki/public/observability/reasoning_velocity');
  }

  async getV1AkkiPublicStudioReadBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/public/studio/read/{token}');
  }

  async postV1AkkiPublicStudioSensitivity_demo(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/public/studio/sensitivity-demo', body);
  }

  async getV1AkkiPublicStudioTrackBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/public/studio/track/{token}');
  }

  async getV1AkkiReportsInbox(): Promise<unknown> {
    return this._request('GET', '/v1/akki/reports/inbox');
  }

  async getV1AkkiRespondBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/respond/{token}');
  }

  async postV1AkkiRespondBytoken(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/respond/{token}', body);
  }

  async postV1AkkiSandbox_genSessions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox-gen/sessions', body);
  }

  async deleteV1AkkiSandbox_genSessionsBysid(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/sandbox-gen/sessions/{sid}');
  }

  async getV1AkkiSandbox_genSessionsBysid(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox-gen/sessions/{sid}');
  }

  async postV1AkkiSandboxCleanupExpired(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/cleanup/expired', body);
  }

  async postV1AkkiSandboxContextsSeeded(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/contexts/seeded', body);
  }

  async postV1AkkiSandboxContextsBycontext_idCapture_email(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/contexts/{context_id}/capture-email', body);
  }

  async getV1AkkiSandboxContextsBycontext_idObjective_check(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/contexts/{context_id}/objective-check');
  }

  async postV1AkkiSandboxContextsBycontext_idObjective_check(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/contexts/{context_id}/objective-check', body);
  }

  async getV1AkkiSandboxContextsBycontext_idSample_doc(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/contexts/{context_id}/sample-doc');
  }

  async postV1AkkiSandboxContextsBycontext_idSample_docAccept(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/contexts/{context_id}/sample-doc/accept', body);
  }

  async getV1AkkiSandboxContextsBycontext_idTutorial(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/contexts/{context_id}/tutorial');
  }

  async postV1AkkiSandboxContextsBycontext_idTutorialDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/contexts/{context_id}/tutorial/dismiss', body);
  }

  async postV1AkkiSandboxConvert(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/convert', body);
  }

  async postV1AkkiSandboxGenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/generate', body);
  }

  async getV1AkkiSandboxGenerateBysession_idStatus(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/generate/{session_id}/status');
  }

  async getV1AkkiSandboxTemplates(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/templates');
  }

  async postV1AkkiSandboxV2Sessions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/v2/sessions', body);
  }

  async getV1AkkiSandboxV2SessionsBysid(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}');
  }

  async patchV1AkkiSandboxV2SessionsBysid(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/sandbox/v2/sessions/{sid}', body);
  }

  async getV1AkkiSandboxV2SessionsBysidComposed_draft(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}/composed-draft');
  }

  async getV1AkkiSandboxV2SessionsBysidCycle_snapshot(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}/cycle-snapshot');
  }

  async postV1AkkiSandboxV2SessionsBysidExit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/v2/sessions/{sid}/exit', body);
  }

  async getV1AkkiSandboxV2SessionsBysidFallback_situation(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}/fallback-situation');
  }

  async getV1AkkiSandboxV2SessionsBysidOpening_question(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}/opening-question');
  }

  async getV1AkkiSandboxV2SessionsBysidPulse_signals(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}/pulse-signals');
  }

  async postV1AkkiSandboxV2SessionsBysidSave_and_send(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/v2/sessions/{sid}/save-and-send', body);
  }

  async getV1AkkiSandboxV2SessionsBysidStudio_sources(): Promise<unknown> {
    return this._request('GET', '/v1/akki/sandbox/v2/sessions/{sid}/studio-sources');
  }

  async postV1AkkiSandboxV2SessionsBysidStudioAdd_sentence(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/sandbox/v2/sessions/{sid}/studio/add-sentence', body);
  }

  async getV1AkkiSearch(): Promise<unknown> {
    return this._request('GET', '/v1/akki/search');
  }

  async postV1AkkiSearchCross_context_open(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/search/cross-context-open', body);
  }

  async deleteV1AkkiSharesByshare_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/shares/{share_id}');
  }

  async getV1AkkiSharesByshare_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/shares/{share_id}');
  }

  async postV1AkkiSolvaV2SessionsBysidTurnStream(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/solva/v2/sessions/{sid}/turn/stream', body);
  }

  async postV1AkkiStudioBykindByartefact_idApprove(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/approve', body);
  }

  async getV1AkkiStudioBykindByartefact_idBlocks(): Promise<unknown> {
    return this._request('GET', '/v1/akki/studio/{kind}/{artefact_id}/blocks');
  }

  async postV1AkkiStudioBykindByartefact_idBlocks(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/blocks', body);
  }

  async postV1AkkiStudioBykindByartefact_idBlocksReorder(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/blocks/reorder', body);
  }

  async deleteV1AkkiStudioBykindByartefact_idBlocksByblock_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/akki/studio/{kind}/{artefact_id}/blocks/{block_id}');
  }

  async patchV1AkkiStudioBykindByartefact_idBlocksByblock_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/studio/{kind}/{artefact_id}/blocks/{block_id}', body);
  }

  async postV1AkkiStudioBykindByartefact_idBlocksByblock_idMove(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/blocks/{block_id}/move', body);
  }

  async getV1AkkiStudioBykindByartefact_idLifecycle(): Promise<unknown> {
    return this._request('GET', '/v1/akki/studio/{kind}/{artefact_id}/lifecycle');
  }

  async postV1AkkiStudioBykindByartefact_idSend(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/send', body);
  }

  async postV1AkkiStudioBykindByartefact_idSubmit_review(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/submit-review', body);
  }

  async postV1AkkiStudioBykindByartefact_idSynisense_accept(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/synisense-accept', body);
  }

  async postV1AkkiStudioBykindByartefact_idUpload_image(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/studio/{kind}/{artefact_id}/upload-image', body);
  }

  async getV1AkkiTasks(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks');
  }

  async postV1AkkiTasks(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks', body);
  }

  async postV1AkkiTasksAgent_prefill(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/agent-prefill', body);
  }

  async getV1AkkiTasksCirculationBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/circulation/{token}');
  }

  async postV1AkkiTasksCirculationBytokenComment(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/circulation/{token}/comment', body);
  }

  async getV1AkkiTasksContributeBytoken(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/contribute/{token}');
  }

  async postV1AkkiTasksContributeBytokenComment(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/contribute/{token}/comment', body);
  }

  async postV1AkkiTasksContributeBytokenSubmit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/contribute/{token}/submit', body);
  }

  async postV1AkkiTasksContributeBytokenUpload(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/contribute/{token}/upload', body);
  }

  async getV1AkkiTasksCounts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/counts');
  }

  async getV1AkkiTasksBytask_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/{task_id}');
  }

  async patchV1AkkiTasksBytask_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/tasks/{task_id}', body);
  }

  async getV1AkkiTasksBytask_idCompile(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/{task_id}/compile');
  }

  async postV1AkkiTasksBytask_idCompileCirculationClose(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/circulation/close', body);
  }

  async postV1AkkiTasksBytask_idCompileCirculationSend(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/circulation/send', body);
  }

  async postV1AkkiTasksBytask_idCompileCommit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/commit', body);
  }

  async postV1AkkiTasksBytask_idCompileDraft(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/draft', body);
  }

  async postV1AkkiTasksBytask_idCompileFinal_productionApply_comment(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/final-production/apply-comment', body);
  }

  async postV1AkkiTasksBytask_idCompileFinal_productionComplete(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/final-production/complete', body);
  }

  async postV1AkkiTasksBytask_idCompileReviewComplete(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/compile/review/complete', body);
  }

  async patchV1AkkiTasksBytask_idContributionsBycontributor_id(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/akki/tasks/{task_id}/contributions/{contributor_id}', body);
  }

  async postV1AkkiTasksBytask_idContributorsBycontributor_idReinvite(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/contributors/{contributor_id}/reinvite', body);
  }

  async getV1AkkiTasksBytask_idDrafts(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/{task_id}/drafts');
  }

  async getV1AkkiTasksBytask_idIntelligence(): Promise<unknown> {
    return this._request('GET', '/v1/akki/tasks/{task_id}/intelligence');
  }

  async postV1AkkiTasksBytask_idIntelligenceRegenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{task_id}/intelligence/regenerate', body);
  }

  async postV1AkkiTasksBytidClose(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{tid}/close', body);
  }

  async postV1AkkiTasksBytidCommission(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/tasks/{tid}/commission', body);
  }

  async getV1AkkiUsersMeOnboarding_status(): Promise<unknown> {
    return this._request('GET', '/v1/akki/users/me/onboarding-status');
  }

  async postV1AkkiUsersMeOnboarding_statusAcknowledge(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/users/me/onboarding-status/acknowledge', body);
  }

  async postV1AkkiUsersMeOnboarding_statusDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/users/me/onboarding-status/dismiss', body);
  }

  async postV1AkkiUsersMeOnboarding_statusFirst_chat_seen(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/users/me/onboarding-status/first-chat-seen', body);
  }

  async postV1AkkiUsersMeOnboarding_statusTooltipsHelpDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/users/me/onboarding-status/tooltips/help/dismiss', body);
  }

  async postV1AkkiUsersMeOnboarding_statusTooltipsTrust_centerDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/users/me/onboarding-status/tooltips/trust-center/dismiss', body);
  }

  async postV1AkkiUsersMeOnboarding_statusTrust_center_tourDismiss(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/users/me/onboarding-status/trust-center-tour/dismiss', body);
  }

  async getV1AkkiUx_advisories(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ux-advisories');
  }

  async getV1AkkiUx_advisories_md(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ux-advisories.md');
  }

  async getV1AkkiUx_audit(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ux-audit');
  }

  async getV1AkkiUx_audit_md(): Promise<unknown> {
    return this._request('GET', '/v1/akki/ux-audit.md');
  }

  async postV1AkkiWalkin(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/walkin', body);
  }

  async postV1AkkiWalkinRegenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/walkin/regenerate', body);
  }

  async postV1AkkiWebhookStripe(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/webhook/stripe', body);
  }

  async postV1AkkiWebsiteContact(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/website/contact', body);
  }

  async postV1AkkiWebsiteEarly_access(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/website/early-access', body);
  }

  async getV1AkkiWork_studioArtefactsBykindByartefact_idSynisense_breakdown(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/artefacts/{kind}/{artefact_id}/synisense-breakdown');
  }

  async getV1AkkiWork_studioBriefsBybrief_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/briefs/{brief_id}');
  }

  async postV1AkkiWork_studioBriefsBybrief_idEnhance(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/work_studio/briefs/{brief_id}/enhance', body);
  }

  async getV1AkkiWork_studioBriefsBybrief_idRevisions(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/briefs/{brief_id}/revisions');
  }

  async getV1AkkiWork_studioBriefsBybrief_idRevisionsByrevision_idDiff(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/briefs/{brief_id}/revisions/{revision_id}/diff');
  }

  async postV1AkkiWork_studioBriefsBybrief_idSet_active(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/work_studio/briefs/{brief_id}/set_active', body);
  }

  async postV1AkkiWork_studioExports(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/akki/work_studio/exports', body);
  }

  async getV1AkkiWork_studioExportsByexport_id(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/exports/{export_id}');
  }

  async getV1AkkiWork_studioExportsByexport_idDownload(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/exports/{export_id}/download');
  }

  async getV1AkkiWork_studioPicker(): Promise<unknown> {
    return this._request('GET', '/v1/akki/work_studio/picker');
  }

}
