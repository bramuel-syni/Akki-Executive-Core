// AUTO-GENERATED — do not edit by hand.
// Source: backend/openapi-sdk/solva.openapi.json
// Regenerate via: python scripts/build_sdk.py

// ── Schemas ──
export interface AnomaliesRequest {
  column?: string | unknown;
  iqr_multiplier?: number;
  sheet: string;
  z_threshold?: number;
}

export interface AnomaliesResponse {
  anomalies?: Array<unknown> | unknown;
}

export interface ArtefactFromSolvaIn {
  session_id: string;
}

export interface AttachDocumentIn {
  document_id: string;
}

export interface Body_restore_one_v1_solva_8c5580bc {
  session_id: string;
}

export interface Body_upload_workbook_multi_v1_solva_3618fa53 {
  context_id?: string | unknown;
  files: Array<string>;
  objective?: string | unknown;
  title?: string | unknown;
}

export interface Body_upload_workbook_v1_solva_21384245 {
  file: string;
}

export interface CreateSessionIn {
  seed_payload?: SeedPayload | unknown;
  sub_module: string;
}

export interface ForecastRequest {
  date_column: string;
  horizon_periods?: number;
  sheet: string;
  value_column: string;
}

export interface ForkV2In {
  persona?: string | unknown;
  to_submodule: string;
}

export interface FrameAuditDecisionIn {
  decision: string;
}

export interface HTTPValidationError {
  detail?: Array<ValidationError>;
}

export interface HandoffCycleIn {
  note?: string | unknown;
}

export interface IdResponse {
  deleted?: boolean | unknown;
  id?: string | unknown;
}

export interface IntentClassifyIn {
  intent: string;
}

export interface ItemsListResponse {
  items?: Array<unknown> | unknown;
  next_cursor?: string | unknown;
  total?: number | unknown;
  total_pending?: number | unknown;
}

export interface RefuseIn {
  operator_reason?: string | unknown;
}

export interface SeedPayload {
  attached_references?: Array<string>;
  preview_text?: string;
  source: string;
  source_id: string;
  sub_module_hint?: string | unknown;
}

export interface SignalsResponse {
  signals?: Array<unknown> | unknown;
}

export interface SimulateRequest {
  column: string;
  distribution: string;
  formula?: string;
  iterations?: number;
  params: Record<string, unknown>;
  seed?: number;
  sheet: string;
}

export interface StartV2In {
  auto_cluster?: boolean;
  cluster_id?: string | unknown;
  context_id?: string | unknown;
  intake_seed?: Record<string, unknown> | unknown;
  intent: string;
  persona?: string | unknown;
  pro_tier?: boolean;
  sandbox?: boolean;
  submodule?: string;
}

export interface SubmitAnswerIn {
  answer_text: string;
}

export interface SubmitFramingIn {
  framing_text: string;
}

export interface TurnV2In {
  user_text: string;
}

export interface ValidationError {
  loc: Array<string | number>;
  msg: string;
  type: string;
}

export interface WorkbookAnalysisResponse {
  account_id?: string | unknown;
  context_id?: string | unknown;
  id?: string | unknown;
  status?: string | unknown;
}

export interface _AnalysisNoteIn {
  body: string;
}

export interface _AnalysisObjectivePatch {
  objective: string;
}

export interface _PostBody {
  action: "increment" | "suppress" | "unsuppress";
  area: string;
}

export interface _UpdateSessionTitleIn {
  title: string;
}

// ── Client ──
export interface SolvaClientOptions {
  baseUrl: string;
  authToken?: string;
  fetchImpl?: typeof fetch;
}

export class SolvaClient {
  private baseUrl: string;
  private authToken?: string;
  private fetchImpl: typeof fetch;

  constructor(opts: SolvaClientOptions) {
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

  async getV1SolvaAdminSolvaKey_usage(): Promise<unknown> {
    return this._request('GET', '/v1/solva/admin/solva/key-usage');
  }

  async getV1SolvaAdminSolvaLegacyOrphan_count(): Promise<unknown> {
    return this._request('GET', '/v1/solva/admin/solva/legacy/orphan-count');
  }

  async postV1SolvaAdminSolvaLegacyRestore(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/admin/solva/legacy/restore', body);
  }

  async postV1SolvaAdminSolvaLegacySoft_archive(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/admin/solva/legacy/soft-archive', body);
  }

  async getV1SolvaAdminSolvaVariant_coverage(): Promise<unknown> {
    return this._request('GET', '/v1/solva/admin/solva/variant-coverage');
  }

  async getV1SolvaBriefingState(): Promise<unknown> {
    return this._request('GET', '/v1/solva/briefing/state');
  }

  async postV1SolvaBriefingState(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/briefing/state', body);
  }

  async getV1SolvaChatsBychat_idPrivacy_report_pdf(): Promise<unknown> {
    return this._request('GET', '/v1/solva/chats/{chat_id}/privacy-report.pdf');
  }

  async getV1SolvaContextsBycontext_idSolvaV2Sessions(): Promise<unknown> {
    return this._request('GET', '/v1/solva/contexts/{context_id}/solva/v2/sessions');
  }

  async postV1SolvaContextsBycontext_idSolvaV2Sessions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/contexts/{context_id}/solva/v2/sessions', body);
  }

  async getV1SolvaContextsBycontext_idSolvaV2SessionsBysession_id(): Promise<unknown> {
    return this._request('GET', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}');
  }

  async postV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idAnswer(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/answer', body);
  }

  async postV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idAttach_document(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/attach-document', body);
  }

  async getV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idAttachments(): Promise<unknown> {
    return this._request('GET', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/attachments');
  }

  async getV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idAudit_panelTimeline(): Promise<unknown> {
    return this._request('GET', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/audit-panel/timeline');
  }

  async postV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idFraming(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/framing', body);
  }

  async postV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idRefuse(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/refuse', body);
  }

  async patchV1SolvaContextsBycontext_idSolvaV2SessionsBysession_idTitle(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/solva/contexts/{context_id}/solva/v2/sessions/{session_id}/title', body);
  }

  async postV1SolvaContextsBycontext_idWork_studioArtefactsFrom_solva(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/contexts/{context_id}/work-studio/artefacts/from-solva', body);
  }

  async getV1SolvaSessionsBysidV2Chair_notes(): Promise<unknown> {
    return this._request('GET', '/v1/solva/sessions/{sid}/v2/chair_notes');
  }

  async getV1SolvaSessionsBysidV2Export_pptx(): Promise<unknown> {
    return this._request('GET', '/v1/solva/sessions/{sid}/v2/export.pptx');
  }

  async getV1SolvaSessionsBysidV2Payload(): Promise<unknown> {
    return this._request('GET', '/v1/solva/sessions/{sid}/v2/payload');
  }

  async getV1SolvaSessionsBysidV2Stream(): Promise<unknown> {
    return this._request('GET', '/v1/solva/sessions/{sid}/v2/stream');
  }

  async postV1SolvaV2CronStale_session_sweep(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/cron/stale-session-sweep', body);
  }

  async postV1SolvaV2IntentClassify(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/intent/classify', body);
  }

  async getV1SolvaV2Seed(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/seed');
  }

  async getV1SolvaV2Sessions(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions');
  }

  async postV1SolvaV2Sessions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions', body);
  }

  async getV1SolvaV2SessionsBysid(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}');
  }

  async postV1SolvaV2SessionsBysidAbandon(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/abandon', body);
  }

  async getV1SolvaV2SessionsBysidArtefact_reasoning(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}/artefact-reasoning');
  }

  async postV1SolvaV2SessionsBysidAttach_document(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/attach-document', body);
  }

  async deleteV1SolvaV2SessionsBysidAttached_documentsBydocument_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/solva/v2/sessions/{sid}/attached-documents/{document_id}');
  }

  async postV1SolvaV2SessionsBysidContinue_chat(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/continue-chat', body);
  }

  async getV1SolvaV2SessionsBysidExport_docx(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}/export.docx');
  }

  async getV1SolvaV2SessionsBysidExport_pdf(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}/export.pdf');
  }

  async postV1SolvaV2SessionsBysidFork(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/fork', body);
  }

  async postV1SolvaV2SessionsBysidFrame_audit(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/frame-audit', body);
  }

  async postV1SolvaV2SessionsBysidFrame_audit_decision(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/frame-audit-decision', body);
  }

  async postV1SolvaV2SessionsBysidHandoffCycle(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/handoff/cycle', body);
  }

  async getV1SolvaV2SessionsBysidReasoning_log(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}/reasoning-log');
  }

  async getV1SolvaV2SessionsBysidReasoning_logSummary(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}/reasoning-log/summary');
  }

  async getV1SolvaV2SessionsBysidSynisense_breakdown(): Promise<unknown> {
    return this._request('GET', '/v1/solva/v2/sessions/{sid}/synisense-breakdown');
  }

  async postV1SolvaV2SessionsBysidTake_to_cycle(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/take-to-cycle', body);
  }

  async postV1SolvaV2SessionsBysidTurn(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/v2/sessions/{sid}/turn', body);
  }

  async getV1SolvaWorkbookAnalyses(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/analyses');
  }

  async getV1SolvaWorkbookAnalysesByaid(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/analyses/{aid}');
  }

  async postV1SolvaWorkbookAnalysesByaidAnomalies(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/analyses/{aid}/anomalies', body);
  }

  async postV1SolvaWorkbookAnalysesByaidForecast(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/analyses/{aid}/forecast', body);
  }

  async getV1SolvaWorkbookAnalysesByaidReport_docx(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/analyses/{aid}/report.docx');
  }

  async getV1SolvaWorkbookAnalysesByaidReport_pptx(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/analyses/{aid}/report.pptx');
  }

  async getV1SolvaWorkbookAnalysesByaidReport_xlsx(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/analyses/{aid}/report.xlsx');
  }

  async postV1SolvaWorkbookAnalysesByaidSignalsExtract(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/analyses/{aid}/signals/extract', body);
  }

  async postV1SolvaWorkbookAnalysesByaidSimulate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/analyses/{aid}/simulate', body);
  }

  async postV1SolvaWorkbookUpload(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/upload', body);
  }

  async postV1SolvaWorkbookUpload_multi(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/upload-multi', body);
  }

  async getV1SolvaWorkbookV2Analyses(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/v2/analyses');
  }

  async getV1SolvaWorkbookV2AnalysesByaid(): Promise<unknown> {
    return this._request('GET', '/v1/solva/workbook/v2/analyses/{aid}');
  }

  async postV1SolvaWorkbookV2AnalysesByaidNotes(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/v2/analyses/{aid}/notes', body);
  }

  async patchV1SolvaWorkbookV2AnalysesByaidObjective(body?: unknown): Promise<unknown> {
    return this._request('PATCH', '/v1/solva/workbook/v2/analyses/{aid}/objective', body);
  }

  async postV1SolvaWorkbookV2AnalysesByaidSession_close(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/v2/analyses/{aid}/session-close', body);
  }

  async postV1SolvaWorkbookV2AnalysesByaidSynthesize(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/solva/workbook/v2/analyses/{aid}/synthesize', body);
  }

}
