export type ContractStatus = 'UPLOADED' | 'PARSING' | 'PARSED' | 'REVIEWING' | 'COMPLETED' | 'FAILED';

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export type ParseJobStatus = 'WAITING' | 'RUNNING' | 'SUCCESS' | 'FAILED';

export type UserInfo = {
  id: number;
  username: string;
  email: string | null;
  role: string;
  status: string;
  created_at: string;
};

export type ContractListItem = {
  id: number;
  file_name: string;
  file_type: string;
  file_size: number | null;
  contract_type: string | null;
  title: string | null;
  status: ContractStatus;
  created_at: string;
};

export type ContractDetail = ContractListItem & {
  user_id: number;
  stored_file_name: string;
  updated_at: string;
};

export type ParseJob = {
  id: number;
  contract_id: number;
  backend: string;
  status: string;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
};

export type ParseStatusInfo = {
  contract_id: number;
  contract_status: ContractStatus;
  parse_job: ParseJob | null;
};

export type ParseResultInfo = {
  parse_job: ParseJob;
  raw_markdown: string | null;
  normalized_json: string | null;
  // Safety: boolean flags instead of exposing server paths
  has_markdown: boolean;
  has_content_json: boolean;
  has_middle_json: boolean;
  has_layout_pdf: boolean;
  has_images: boolean;
};

// ── Normalized Document Types ────────────────────────────────────────────────

export type NormalizedSection = {
  id: string;
  title: string;
  order_index: number;
  clause_ids: string[];
};

export type NormalizedClause = {
  id: string;
  section_id: string;
  title: string;
  text: string;
  order_index: number;
  clause_type?: string;
  page_number?: number;
  source?: string;
};

export type NormalizedParty = {
  name: string;
  role: string;
  source?: string;
};

export type NormalizedTable = {
  table_id: string;
  html?: string;
  page?: number;
  caption?: string;
};

export type NormalizedDocument = {
  title: string | null;
  contract_type: string | null;
  parties: NormalizedParty[];
  sections: NormalizedSection[];
  clauses: NormalizedClause[];
  tables: NormalizedTable[];
  metadata: { parse_engine: string; content_json_available: boolean };
};

// ── Review / Agent Types ────────────────────────────────────────────────────

export type ReviewTask = {
  id: number;
  contract_id: number;
  user_id: number;
  status: string;
  current_step: string | null;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
};

export type AgentExecutionLog = {
  id: number;
  task_id: number;
  contract_id: number;
  agent_name: string;
  input_json: string | null;
  output_json: string | null;
  status: string;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
};
