import { request } from './request';

export function getReviewProgress(taskId: string) {
  return request.get(`/api/v1/review-tasks/${taskId}/progress`);
}
