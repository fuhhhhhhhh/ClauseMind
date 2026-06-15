export type ContractStatus = 'UPLOADED' | 'PARSING' | 'PARSED' | 'REVIEWING' | 'COMPLETED' | 'FAILED';

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW';

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
