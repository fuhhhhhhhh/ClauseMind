import type { ApiResponse } from './request';
import { request } from './request';

import type { ParseJob, ParseResultInfo, ParseStatusInfo, NormalizedDocument } from '../types';

export function startParse(contractId: number | string) {
  return request.post<ApiResponse<ParseJob>>(`/api/v1/contracts/${contractId}/parse`);
}

export function getParseStatus(contractId: number | string) {
  return request.get<ApiResponse<ParseStatusInfo>>(`/api/v1/contracts/${contractId}/parse-status`);
}

export function getParseResult(contractId: number | string) {
  return request.get<ApiResponse<ParseResultInfo>>(`/api/v1/contracts/${contractId}/parse-result`);
}

export function normalizeDocument(contractId: number | string) {
  return request.post<ApiResponse<NormalizedDocument>>(`/api/v1/contracts/${contractId}/normalize`);
}
