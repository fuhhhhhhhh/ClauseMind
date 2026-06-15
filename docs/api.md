# ClauseMind API 文档

统一响应格式: `{"code": 200, "message": "success", "data": {...}}`

## Auth
| 方法 | 路径 | 鉴权 | 描述 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 否 | 注册 |
| POST | `/api/v1/auth/login` | 否 | 登录 |
| GET | `/api/v1/auth/me` | 是 | 当前用户 |

## Contracts
| 方法 | 路径 | 鉴权 | 描述 |
|------|------|------|------|
| POST | `/api/v1/contracts/upload` | 是 | 上传 |
| GET | `/api/v1/contracts` | 是 | 列表 |
| GET | `/api/v1/contracts/{id}` | 是 | 详情 |
| DELETE | `/api/v1/contracts/{id}` | 是 | 删除 |
| GET | `/api/v1/contracts/{id}/review/latest` | 是 | 最新审查任务 |

## Parse
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/contracts/{id}/parse` | 启动解析 |
| GET | `/api/v1/contracts/{id}/parse-status` | 解析状态 |
| GET | `/api/v1/contracts/{id}/parse-result` | 解析结果 |
| POST | `/api/v1/contracts/{id}/normalize` | 标准化 |

## Review
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/contracts/{id}/review` | 完整 6-Agent |
| POST | `/api/v1/contracts/{id}/review/profile` | 仅 Profile |
| GET | `/api/v1/review-tasks/{id}` | 任务 |
| GET | `/api/v1/review-tasks/{id}/progress` | 进度 |
| GET | `/api/v1/review-tasks/{id}/agent-logs` | 日志 |
| GET | `/api/v1/review-tasks/{id}/profile` | 画像 |
| GET | `/api/v1/review-tasks/{id}/clauses` | 条款 |
| GET | `/api/v1/review-tasks/{id}/risks` | 风险 |
| GET | `/api/v1/review-tasks/{id}/suggestions` | 建议 |

## Reports
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/reports/{task_id}` | 报告 |
| GET | `/api/v1/reports/{task_id}/export` | 导出 MD |

## Admin (需 admin role)
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/admin/users` | 用户列表 |
| GET | `/api/v1/admin/contracts` | 合同列表 |
| GET | `/api/v1/admin/review-tasks` | 任务列表 |
| GET | `/api/v1/admin/agent-logs` | 日志列表 |
| GET | `/api/v1/admin/agent-logs/{id}` | 日志详情 |
| GET | `/api/v1/admin/statistics` | 统计 |
