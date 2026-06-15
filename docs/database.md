# ClauseMind 数据库设计

## 核心表 (13 tables, 5 Alembic migrations)

### user — 用户
id, username(UNIQUE), password_hash, email, role(USER/admin), status(ACTIVE), created_at, updated_at

### contract — 合同
id, user_id(FK), file_name, stored_file_name(UUID), file_path, file_type, file_size, contract_type, title, status(UPLOADED/PARSING/PARSED/REVIEWING/COMPLETED/FAILED), created_at, updated_at

### parse_job — 解析任务
id, contract_id(FK), input_path, output_dir, backend, status(WAITING/RUNNING/SUCCESS/FAILED), error_message, started_at, finished_at, created_at

### document_parse_result — 解析结果
id, contract_id(FK), parse_job_id(FK), markdown_path, content_json_path, middle_json_path, layout_pdf_path, image_dir, raw_markdown, normalized_json, created_at

### review_task — 审查任务
id, contract_id(FK), user_id(FK), status(RUNNING/SUCCESS/FAILED), current_step, error_message, started_at, finished_at, created_at

### agent_execution_log — Agent 日志
id, task_id(FK), contract_id(FK), agent_name, input_json, output_json, status, error_message, started_at, finished_at, duration_ms

### contract_clause — 条款
id, task_id(FK), contract_id(FK), clause_id, section_id, title, text, clause_type, page_number, source_text, created_at

### risk_item — 风险
id, task_id(FK), contract_id(FK), risk_id, clause_id, risk_level, risk_type, description, reason, suggestion, need_human_review, created_at

### modify_suggestion — 修改建议
id, task_id(FK), contract_id(FK), suggestion_id, risk_id, clause_id, original_text, suggested_text, reason, created_at

### review_report — 审查报告
id, task_id(FK), contract_id(FK), report_title, overall_risk, markdown_report, disclaimer, created_at

## 关系
user 1:N contract → contract 1:N parse_job → parse_job 1:1 document_parse_result
contract 1:N review_task → review_task 1:N agent_execution_log / contract_clause / risk_item / modify_suggestion
review_task 1:1 review_report
