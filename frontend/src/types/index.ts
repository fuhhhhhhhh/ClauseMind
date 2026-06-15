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
