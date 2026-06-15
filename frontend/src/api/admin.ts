import type { ApiResponse } from './request';
import { request } from './request';

// ── Types ────────────────────────────────────────────────────────────────────

export type AdminUser = {
  id: number;
  username: string;
  email: string | null;
  role: string;
  status: string;
  created_at: string;
};

export type AdminContract = {
  id: number;
  user_id: number;
  file_name: string;
  contract_type: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

export type AdminReviewTask = {
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

export type AdminAgentLog = {
  id: number;
  task_id: number;
  contract_id: number;
  agent_name: string;
  status: string;
  error_message: string | null;
  duration_ms: number | null;
  started_at: string | null;
  finished_at: string | null;
};

export type AdminAgentLogDetail = AdminAgentLog & {
  input_json: string | null;
  output_json: string | null;
};

export type AdminStatistics = {
  user_count: number;
  contract_count: number;
  review_task_count: number;
  completed_review_count: number;
  failed_review_count: number;
  high_risk_count: number;
  risk_level_counts: { high: number; medium: number; low: number };
  recent_review_tasks: { id: number; contract_id: number; status: string; created_at: string }[];
};

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

export type AdminQueryParams = {
  page?: number;
  page_size?: number;
  keyword?: string;
  status?: string;
  role?: string;
  agent_name?: string;
};

// ── API ──────────────────────────────────────────────────────────────────────

export function getAdminUsers(params?: AdminQueryParams) {
  return request.get<ApiResponse<PaginatedResponse<AdminUser>>>('/api/v1/admin/users', { params });
}

export function getAdminContracts(params?: AdminQueryParams) {
  return request.get<ApiResponse<PaginatedResponse<AdminContract>>>('/api/v1/admin/contracts', { params });
}

export function getAdminReviewTasks(params?: AdminQueryParams) {
  return request.get<ApiResponse<PaginatedResponse<AdminReviewTask>>>('/api/v1/admin/review-tasks', { params });
}

export function getAdminAgentLogs(params?: AdminQueryParams) {
  return request.get<ApiResponse<PaginatedResponse<AdminAgentLog>>>('/api/v1/admin/agent-logs', { params });
}

export function getAdminAgentLogDetail(logId: number) {
  return request.get<ApiResponse<AdminAgentLogDetail>>(`/api/v1/admin/agent-logs/${logId}`);
}

export function getAdminStatistics() {
  return request.get<ApiResponse<AdminStatistics>>('/api/v1/admin/statistics');
}
