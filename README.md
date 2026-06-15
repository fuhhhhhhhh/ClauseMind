# ClauseMind

ClauseMind 是一个基于 React + FastAPI + MinerU + OpenAI-compatible LLM 的合同智能审查系统骨架。当前版本是首轮可运行架构：前后端可以联通，后端读取 `.env`，保留 MinerU、文档标准化、多 Agent 审查、报告生成和管理员后台的扩展边界。

## Tech Stack

- Frontend: React 18, Vite, TypeScript, Ant Design, Axios, Zustand
- Backend: FastAPI, SQLAlchemy 2.x, Pydantic Settings, httpx, uv
- Storage: local `storage/` directories
- Database: SQLite by default, MySQL-compatible URL supported later

## Backend

```bash
cd backend
uv sync
uv run alembic upgrade head   # 首次运行或数据库结构变更后执行
uv run uvicorn main:app --reload
```

Useful endpoints:

- `GET /health`
- `GET /api/v1/system/config`
- `GET /docs`

The real LLM settings live in `backend/.env`. Keep that file local. Use `backend/.env.example` as the template for other machines.

MinerU is expected to be configured through environment variables. The local recommended setup is:

```env
MINERU_COMMAND=/home/fuxiangyu/miniconda3/envs/wepipeline/bin/mineru
MINERU_BACKEND=hybrid-auto-engine
```

Do not install or upgrade packages inside the existing `wepipeline` conda environment from this project. A vendored MinerU source copy is available at `third_party/MinerU` for inspection/integration work.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/health` and `/api` to `http://localhost:8000`.

## Current Scope

This repository currently contains the initial runnable skeleton only. Business implementation should continue from `TODO.md` in small phases:

1. auth and JWT
2. contract upload and file persistence
3. MinerU parse integration
4. document normalization
5. first LLM agent
6. full multi-agent workflow
7. result pages
8. admin and course documents
