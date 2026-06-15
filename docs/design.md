# ClauseMind 设计文档

## 技术架构
```
React 前端 → FastAPI 后端 → SQLite + 文件存储
              ├── MinerU CLI (subprocess)
              └── LLM API (OpenAI-compatible)
```

## 前端
- React 18 + Vite + TypeScript 5 + Ant Design 5
- React Router 6 + Zustand + Axios + react-markdown

## 后端模块
- `app/core/` — config, database, security, response, exceptions
- `app/api/v1/` — auth, contracts, parse, reviews, reports, admin
- `app/models/` — user, contract, parse_job, review_task, review_results
- `app/services/` — mineru, document_normalizer, review, file_storage
- `app/agents/` — base, llm_client, 6 agents + orchestrator
- `app/schemas/` — Pydantic models for all modules

## Agent 架构
6 个 Agent 继承 BaseAgent，顺序执行：
ContractProfile → Clause → Risk → Suggestion → Consistency → Report
每个 Agent 记录 execution log (input/output/status/duration/error)

## 安全
- JWT + bcrypt
- 用户数据隔离 (user_id)
- 管理员 role 校验
- 不暴露服务器路径
