CREATE TABLE tickets (
    id BIGSERIAL PRIMARY KEY,
    ticket_id VARCHAR(100) NOT NULL UNIQUE,
    creation_time TIMESTAMPTZ,
    creator VARCHAR(255),
    creator_detail TEXT,
    summary TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ticket_analyses (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    analysis_result JSONB NOT NULL,
    explanation JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE human_reviews (
    id BIGSERIAL PRIMARY KEY,
    ticket_analysis_id BIGINT NOT NULL
        REFERENCES ticket_analyses(id) ON DELETE CASCADE,
    decision VARCHAR(100) NOT NULL,
    review_notes TEXT,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
