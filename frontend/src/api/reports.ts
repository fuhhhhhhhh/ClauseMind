import { request } from './request';

export function getReport(taskId: string) {
  return request.get(`/api/v1/reports/${taskId}`);
}
