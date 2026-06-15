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
  markdown_path: string | null;
  content_json_path: string | null;
  middle_json_path: string | null;
  layout_pdf_path: string | null;
  image_dir: string | null;
  normalized_json: string | null;
};
