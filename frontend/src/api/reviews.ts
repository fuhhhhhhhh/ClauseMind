import type { ApiResponse } from './request';
import { request } from './request';

import type { AgentExecutionLog, ReviewTask } from '../types';

export function startFullReview(contractId: number | string) {
  return request.post<ApiResponse<{ task: ReviewTask; profile: Record<string, unknown> }>>(
    `/api/v1/contracts/${contractId}/review`,
  );
}

export function startProfileReview(contractId: number | string) {
  return request.post<ApiResponse<{ task: ReviewTask; profile: Record<string, unknown> }>>(
    `/api/v1/contracts/${contractId}/review/profile`,
  );
}

export function getReviewTask(taskId: number | string) {
  return request.get<ApiResponse<ReviewTask>>(`/api/v1/review-tasks/${taskId}`);
}

export function getReviewProgress(taskId: number | string) {
  return request.get<ApiResponse<{ task: ReviewTask; agent_logs: AgentExecutionLog[] }>>(
    `/api/v1/review-tasks/${taskId}/progress`,
  );
}

export function getAgentLogs(taskId: number | string) {
  return request.get<ApiResponse<AgentExecutionLog[]>>(`/api/v1/review-tasks/${taskId}/agent-logs`);
}

export function getProfileResult(taskId: number | string) {
  return request.get<ApiResponse<Record<string, unknown>>>(`/api/v1/review-tasks/${taskId}/profile`);
}

export function getReviewClauses(taskId: number | string) {
  return request.get<ApiResponse<Record<string, unknown>[]>>(`/api/v1/review-tasks/${taskId}/clauses`);
}

export function getReviewRisks(taskId: number | string) {
  return request.get<ApiResponse<Record<string, unknown>[]>>(`/api/v1/review-tasks/${taskId}/risks`);
}

export function getReviewSuggestions(taskId: number | string) {
  return request.get<ApiResponse<Record<string, unknown>[]>>(`/api/v1/review-tasks/${taskId}/suggestions`);
}

export function getReviewReport(taskId: number | string) {
  return request.get<ApiResponse<Record<string, unknown>>>(`/api/v1/reports/${taskId}`);
}

export function getLatestReview(contractId: number | string) {
  return request.get<ApiResponse<ReviewTask | null>>(`/api/v1/contracts/${contractId}/review/latest`);
}
