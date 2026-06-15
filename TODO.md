# ClauseMind TODO

This checklist is the handoff file for future model or agent sessions. Work one phase at a time and keep API contracts aligned with `CLAUDE_contract_review_react_fastapi.md`.

## Phase 1: Architecture Skeleton

- [x] Create monorepo layout: `frontend/`, `backend/`, `docs/`, `database/`, `storage/`.
- [x] Configure FastAPI with CORS, unified response helpers, health check, and `/api/v1` routes.
- [x] Configure backend `uv` project with core dependencies.
- [x] Add local `.env` and sanitized `.env.example`.
- [x] Add React + Vite + TypeScript + Ant Design shell.
- [x] Add placeholder frontend routes for the planned user journey.
- [x] Add MinerU, LLM, normalizer, agent, review, and report service boundaries.

## Phase 2: User and Auth

- [ ] Add SQLAlchemy `User` model matching the project spec.
- [ ] Add Alembic migration setup.
- [ ] Implement password hashing with `passlib[bcrypt]`.
- [ ] Implement `POST /api/v1/auth/register`.
- [ ] Implement `POST /api/v1/auth/login`.
- [ ] Implement JWT validation dependency.
- [ ] Implement `GET /api/v1/auth/me`.
- [ ] Connect frontend login/register pages to real APIs.
- [ ] Add route guard for protected pages.

## Phase 3: Contract Upload and Management

- [ ] Add `Contract` model and schema.
- [ ] Implement file extension and size validation.
- [ ] Persist uploaded files into `storage/uploads` with UUID filenames.
- [ ] Implement contract upload/list/detail/delete APIs.
- [ ] Enforce `user_id` isolation for normal users.
- [ ] Connect upload, list, and detail frontend pages.

## Phase 4: MinerU Parse

- [ ] Add `ParseJob` and `DocumentParseResult` models.
- [ ] Wire `MinerUService` into `POST /api/v1/contracts/{contract_id}/parse`.
- [ ] Store MinerU output paths and raw Markdown.
- [ ] Add parse status transitions: `WAITING`, `RUNNING`, `SUCCESS`, `FAILED`.
- [ ] Add graceful error messages for missing MinerU command, timeout, and missing output files.
- [ ] Show parse status and Markdown preview on the frontend.

## Phase 5: Document Normalization

- [ ] Expand `DocumentNormalizer` rules for headings, paragraphs, page source, and tables.
- [ ] Save `normalized_json` on `document_parse_result`.
- [ ] Display sections and tables in the parse result page.
- [ ] Add tests for heading recognition patterns listed in the spec.

## Phase 6: First Agent

- [ ] Add `AgentExecutionLog` model.
- [ ] Implement robust JSON retry logic in `BaseAgent`.
- [ ] Implement `ContractProfileAgent` output validation.
- [ ] Save profile agent input/output/error logs.
- [ ] Display contract profile result in the frontend.

## Phase 7: Full Multi-Agent Workflow

- [ ] Implement `ClauseExtractionAgent`.
- [ ] Implement `RiskDetectionAgent`.
- [ ] Implement `SuggestionAgent`.
- [ ] Implement `ConsistencyCheckAgent`.
- [ ] Implement `ReportGenerationAgent`.
- [ ] Implement `AgentOrchestrator` persistence through `ReviewService`.
- [ ] Add models and APIs for clauses, risks, suggestions, and reports.
- [ ] Ensure generated reports always include the required disclaimer.

## Phase 8: Result Pages

- [ ] Connect review progress page to real task and agent log APIs.
- [ ] Implement Agent log Drawer with input/output/error tabs.
- [ ] Connect risk analysis page to `risk_item` data.
- [ ] Connect suggestion page to `modify_suggestion` data.
- [ ] Connect report page to `review_report` data.

## Phase 9: Admin and Course Deliverables

- [ ] Implement admin user/contract/review-task/agent-log/statistics APIs.
- [ ] Add frontend admin tabs with real tables.
- [ ] Prepare `docs/requirement.md`.
- [ ] Prepare `docs/design.md`.
- [ ] Prepare `docs/api.md`.
- [ ] Prepare `docs/database.md`.
- [ ] Add UML diagrams and screenshots for course submission.

## Guardrails

- Do not modify or clone the `wepipeline` conda environment.
- Use `uv` for backend dependency management.
- Keep real secrets only in local `.env` files.
- Do not commit `backend/.env`, SQLite DBs, uploaded files, MinerU output, or reports.
- Keep LLM calls inside `backend/app/agents/llm_client.py`.
- Keep MinerU calls inside `backend/app/services/mineru_service.py`.
- Do not put business logic directly in FastAPI route functions.
- Do not remove the AI legal disclaimer from reports.
