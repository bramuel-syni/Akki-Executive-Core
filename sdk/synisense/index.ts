// AUTO-GENERATED — do not edit by hand.
// Source: backend/openapi-sdk/synisense.openapi.json
// Regenerate via: python scripts/build_sdk.py

// ── Schemas ──
export interface AskIn {
  question: string;
}

export interface DryrunIn {
  context_id?: string | unknown;
  context_people?: Array<string> | unknown;
  mode?: string;
  surface?: string;
  text: string;
  tier_limit?: number | unknown;
}

export interface ErrorEnvelope {
  audit_id?: string | unknown;
  error_class: string;
  message: string;
}

export interface ExportIn {
  action?: string | unknown;
  since?: string | unknown;
  until?: string | unknown;
}

export interface GovernancePanelResponse {
  audit_log?: unknown | unknown;
  connected_models?: unknown | unknown;
  inbound?: unknown | unknown;
  sensitivity?: unknown | unknown;
  shielding?: unknown | unknown;
  synisense?: unknown | unknown;
}

export interface HTTPValidationError {
  detail?: Array<ValidationError>;
}

export interface ItemsListResponse {
  items?: Array<unknown> | unknown;
  next_cursor?: string | unknown;
  total?: number | unknown;
  total_pending?: number | unknown;
}

export interface ShieldInvokeRequest {
  consumer_id: string;
  content: string;
  model_preference?: "analytical" | "generative" | "balanced";
  purpose: string;
  schema?: Record<string, unknown> | unknown;
  tenant_id: string;
  user_id: string;
}

export interface ShieldInvokeResponse {
  audit_id: string;
  response: string;
  trust_receipt: TrustReceiptV1;
}

export interface Signal {
  confidence: number;
  context_id?: string | unknown;
  created_at: string;
  derivation_source: string;
  entity_ref?: string | unknown;
  expires_at?: string | unknown;
  payload?: Record<string, unknown>;
  signal_category: "profile" | "anomaly" | "life_stage" | "risk" | "operational" | "compliance";
  signal_id: string;
  signal_type: string;
  tenant_id: string;
}

export interface SignalActionIn {
  action_type: string;
  note?: string | unknown;
  recipients?: Array<string> | unknown;
  recommendation_idx?: number | unknown;
  recommendation_label?: string | unknown;
}

export interface SignalGenerateIn {
  focus?: string | unknown;
}

export interface SignalQueryFilter {
  confidence_min?: number | unknown;
  derivation_source?: string | unknown;
  entity_ref?: string | unknown;
  signal_category?: "profile" | "anomaly" | "life_stage" | "risk" | "operational" | "compliance" | unknown;
  signal_type?: string | unknown;
}

export interface SignalQueryPagination {
  cursor?: string | unknown;
  limit?: number;
}

export interface SignalQueryRequest {
  consumer_id: string;
  filter?: SignalQueryFilter;
  pagination?: SignalQueryPagination;
  tenant_id: string;
}

export interface SignalQueryResponse {
  next_cursor?: string | unknown;
  signals: Array<Signal>;
  total_estimate: number;
}

export interface SignalTypeCatalogue {
  signal_types: Array<SignalTypeDefinition>;
}

export interface SignalTypeDefinition {
  description: string;
  payload_schema: Record<string, unknown>;
  signal_category: "profile" | "anomaly" | "life_stage" | "risk" | "operational" | "compliance";
  signal_type: string;
  version?: string;
}

export interface SubscriptionRequest {
  consumer_id: string;
  delivery?: "webhook" | "stream" | "poll";
  signal_types?: Array<"anomaly_flag" | "life_stage" | "churn_risk" | "behavioral_vector" | "compliance_trigger" | "operational_health">;
  tenant_id: string;
  webhook_url?: string | unknown;
}

export interface SubscriptionResponse {
  created_at: string;
  delivery: string;
  status?: "pending" | "active" | "rejected";
  subscription_id: string;
}

export interface TrustReceiptV1 {
  audit_id: string;
  consumer_id: string;
  de_id_summary: Record<string, unknown>;
  dilution_score: number;
  exposure_reduction_score: number;
  llm_model: string;
  llm_provider: string;
  purpose: string;
  receipt_id: string;
  request_hash: string;
  response_hash: string;
  signature: string;
  tenant_id: string;
  timestamp: string;
  version?: string;
}

export interface ValidationError {
  loc: Array<string | number>;
  msg: string;
  type: string;
}

export interface _BatchMsgIds {
  msg_ids?: Array<string>;
}

export interface routers__admin_shield_backfill__BackfillRequest {
  batch_size?: number;
  dry_run?: boolean;
  limit?: number | unknown;
  sleep_ms?: number;
}

// ── Client ──
export interface SynisenseClientOptions {
  baseUrl: string;
  authToken?: string;
  fetchImpl?: typeof fetch;
}

export class SynisenseClient {
  private baseUrl: string;
  private authToken?: string;
  private fetchImpl: typeof fetch;

  constructor(opts: SynisenseClientOptions) {
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

  async postV1SynisenseAdminShieldBackfill(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/admin/shield/backfill', body);
  }

  async getV1SynisenseAdminShieldBackfillStatus(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/shield/backfill/status');
  }

  async getV1SynisenseAdminShieldBackfillByjob_idLog(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/shield/backfill/{job_id}/log');
  }

  async getV1SynisenseAdminShieldBackfillByjob_idStatus(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/shield/backfill/{job_id}/status');
  }

  async getV1SynisenseAdminSignalsAction_heatmap(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/signals/action-heatmap');
  }

  async getV1SynisenseAdminSynisenseBilling(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/synisense/billing');
  }

  async getV1SynisenseAdminSynisenseCron_health(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/synisense/cron-health');
  }

  async getV1SynisenseAdminSynisenseObservability(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/synisense/observability');
  }

  async getV1SynisenseAdminSynisensePerf(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/admin/synisense/perf');
  }

  async postV1SynisenseChatsBychat_idMessagesSynisense_runsBatch(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/chats/{chat_id}/messages/synisense-runs/batch', body);
  }

  async getV1SynisenseChatsBychat_idMessagesBymsg_idSynisense_runs(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/chats/{chat_id}/messages/{msg_id}/synisense-runs');
  }

  async getV1SynisenseChatsBychat_idSynisense_metrics(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/chats/{chat_id}/synisense-metrics');
  }

  async getV1SynisenseContextsBycidSynisense_metrics(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/contexts/{cid}/synisense-metrics');
  }

  async getV1SynisenseContextsBycontext_idAsk(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/contexts/{context_id}/ask');
  }

  async postV1SynisenseContextsBycontext_idAsk(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/contexts/{context_id}/ask', body);
  }

  async getV1SynisenseContextsBycontext_idSignals(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/contexts/{context_id}/signals');
  }

  async postV1SynisenseContextsBycontext_idSignalsGenerate(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/contexts/{context_id}/signals/generate', body);
  }

  async deleteV1SynisenseContextsBycontext_idSignalsBysignal_id(): Promise<unknown> {
    return this._request('DELETE', '/v1/synisense/contexts/{context_id}/signals/{signal_id}');
  }

  async getV1SynisenseContextsBycontext_idSignalsBysignal_idActions(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/contexts/{context_id}/signals/{signal_id}/actions');
  }

  async postV1SynisenseContextsBycontext_idSignalsBysignal_idActions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/contexts/{context_id}/signals/{signal_id}/actions', body);
  }

  async getV1SynisenseContextsBycontext_idSignalsBysignal_idRecommendations(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/contexts/{context_id}/signals/{signal_id}/recommendations');
  }

  async postV1SynisenseDryrun(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/dryrun', body);
  }

  async getV1SynisenseMeGovernance(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/me/governance');
  }

  async getV1SynisenseMeGovernanceAudit(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/me/governance/audit');
  }

  async postV1SynisenseMeGovernanceAuditExport(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/me/governance/audit/export', body);
  }

  async getV1SynisenseStatus(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/status');
  }

  async getV1SynisenseTrust_centerActivity(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/trust-center/activity');
  }

  async getV1SynisenseTrust_centerActivityExport(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/trust-center/activity/export');
  }

  async getV1SynisenseTrust_centerReasoning(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/trust-center/reasoning');
  }

  async getV1SynisenseTrust_centerSessionBychat_id(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/trust-center/session/{chat_id}');
  }

  async getV1SynisenseTrust_centerSessionBychat_idTurnBymessage_id(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/trust-center/session/{chat_id}/turn/{message_id}');
  }

  async getV1SynisenseTrust_centerSessionBychat_idTurnBymessage_idPlaintext(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/trust-center/session/{chat_id}/turn/{message_id}/plaintext');
  }

  async postV1SynisenseV1EngineAdminDerive(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/v1/engine/admin/derive', body);
  }

  async postV1SynisenseV1EngineAdminReseed(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/v1/engine/admin/reseed', body);
  }

  async getV1SynisenseV1EngineSignal_types(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/v1/engine/signal_types');
  }

  async postV1SynisenseV1EngineSignalsQuery(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/v1/engine/signals/query', body);
  }

  async postV1SynisenseV1EngineSubscriptions(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/v1/engine/subscriptions', body);
  }

  async getV1SynisenseV1ShieldAuditByaudit_id(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/v1/shield/audit/{audit_id}');
  }

  async postV1SynisenseV1ShieldLlmInvoke(body?: unknown): Promise<unknown> {
    return this._request('POST', '/v1/synisense/v1/shield/llm/invoke', body);
  }

  async getV1SynisenseV1ShieldReceiptByaudit_id(): Promise<unknown> {
    return this._request('GET', '/v1/synisense/v1/shield/receipt/{audit_id}');
  }

}
