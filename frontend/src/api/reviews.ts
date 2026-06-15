import type { ApiResponse } from './request';
import { request } from './request';

import type { AgentExecutionLog, ReviewTask } from '../types';

export function startProfileReview(contractId: number | string) {
  return request.post<ApiResponse<{ task: ReviewTask; profile: Record<string, unknown> }>>(
    `/api/v1/contracts/${contractId}/review/profile`,
  );
}

export function getReviewTask(taskId: number | string) {
  return request.get<ApiResponse<ReviewTask>>(`/api/v1/review-tasks/${taskId}`);
}

export function getAgentLogs(taskId: number | string) {
  return request.get<ApiResponse<AgentExecutionLog[]>>(`/api/v1/review-tasks/${taskId}/agent-logs`);
}

export function getProfileResult(taskId: number | string) {
  return request.get<ApiResponse<Record<string, unknown>>>(`/api/v1/review-tasks/${taskId}/profile`);
}
