-- schema.sql
CREATE TABLE ai_reports (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    report TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
