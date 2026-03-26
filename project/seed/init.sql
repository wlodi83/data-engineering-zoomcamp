-- Seed schema for local development (mirrors PushMetrics operational tables)
-- No PII, no secrets — safe to commit

CREATE TABLE IF NOT EXISTS workflow (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL,
    cron_rule VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_on TIMESTAMP DEFAULT NOW(),
    changed_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_log (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflow(id),
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    progress FLOAT DEFAULT 0,
    created_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS noteflow_run (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    flow_run_id VARCHAR(100),
    created_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS noteflow_run_task (
    id SERIAL PRIMARY KEY,
    noteflow_run_id INTEGER REFERENCES noteflow_run(id),
    task_name VARCHAR(200),
    status VARCHAR(50) NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL,
    created_on TIMESTAMP DEFAULT NOW(),
    changed_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS block (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    workspace_id INTEGER NOT NULL,
    created_on TIMESTAMP DEFAULT NOW(),
    changed_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS report_block (
    report_id INTEGER REFERENCES report(id),
    block_id INTEGER REFERENCES block(id),
    block_type VARCHAR(50),
    PRIMARY KEY (report_id, block_id)
);

CREATE TABLE IF NOT EXISTS block_execution (
    id SERIAL PRIMARY KEY,
    block_id INTEGER REFERENCES block(id),
    block_type VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_on TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(200),
    user_id INTEGER,
    dttm TIMESTAMP DEFAULT NOW(),
    duration_ms INTEGER,
    json TEXT
);

-- Sample data for local development
INSERT INTO workflow (workspace_id, cron_rule, is_active) VALUES
    (1, '0 9 * * *', true),
    (1, '0 */6 * * *', true),
    (2, '30 8 * * 1-5', true),
    (2, '0 0 * * *', false);

INSERT INTO report (workspace_id) VALUES (1), (1), (2), (2), (2);

INSERT INTO block (type, workspace_id) VALUES
    ('sql', 1), ('chart', 1), ('slack', 1), ('text', 1),
    ('sql', 2), ('chart', 2), ('s3', 2), ('email', 2);

INSERT INTO report_block (report_id, block_id, block_type) VALUES
    (1, 1, 'sql'), (1, 2, 'chart'), (2, 3, 'slack'), (2, 4, 'text'),
    (3, 5, 'sql'), (3, 6, 'chart'), (4, 7, 's3'), (5, 8, 'email');

-- Generate workflow execution history
INSERT INTO workflow_log (workflow_id, status, start_time, end_time, progress)
SELECT
    (random() * 3 + 1)::int,
    CASE WHEN random() > 0.15 THEN 'completed' ELSE 'failed' END,
    NOW() - (random() * 30)::int * INTERVAL '1 day' - (random() * 24)::int * INTERVAL '1 hour',
    NOW() - (random() * 30)::int * INTERVAL '1 day' - (random() * 24)::int * INTERVAL '1 hour' + (random() * 300)::int * INTERVAL '1 second',
    CASE WHEN random() > 0.15 THEN 100 ELSE (random() * 80)::int END
FROM generate_series(1, 200);

-- Generate noteflow runs
INSERT INTO noteflow_run (workspace_id, status, start_time, end_time)
SELECT
    CASE WHEN random() > 0.5 THEN 1 ELSE 2 END,
    CASE WHEN random() > 0.1 THEN 'completed' WHEN random() > 0.5 THEN 'failed' ELSE 'running' END,
    NOW() - (random() * 30)::int * INTERVAL '1 day',
    NOW() - (random() * 30)::int * INTERVAL '1 day' + (random() * 600)::int * INTERVAL '1 second'
FROM generate_series(1, 150);

-- Generate block executions
INSERT INTO block_execution (block_id, block_type, status, start_date, end_date)
SELECT
    (random() * 7 + 1)::int,
    (ARRAY['sql', 'chart', 'slack', 'text', 's3', 'email'])[floor(random() * 6 + 1)::int],
    CASE WHEN random() > 0.12 THEN 'completed' ELSE 'failed' END,
    NOW() - (random() * 30)::int * INTERVAL '1 day',
    NOW() - (random() * 30)::int * INTERVAL '1 day' + (random() * 120)::int * INTERVAL '1 second'
FROM generate_series(1, 500);

-- Generate platform logs
INSERT INTO logs (action, user_id, dttm, duration_ms)
SELECT
    (ARRAY['explore', 'dashboard', 'report_view', 'query_execute', 'block_run', 'login'])[floor(random() * 6 + 1)::int],
    (random() * 20 + 1)::int,
    NOW() - (random() * 30)::int * INTERVAL '1 day',
    (random() * 5000)::int
FROM generate_series(1, 1000);
