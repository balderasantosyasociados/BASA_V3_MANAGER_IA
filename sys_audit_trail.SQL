CREATE TABLE sys_audit_trail (
    audit_id BIGSERIAL PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    transaction_id UUID NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    action_type VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE, FRAUD_ALERT
    timestamp_utc TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC'),
    client_ip VARCHAR(45) NOT NULL,
    record_hash CHAR(64) NOT NULL, -- SHA-256 de toda la fila para evitar manipulaciones de DBAs
    payload_before JSONB,
    payload_after JSONB
);
CREATE INDEX idx_audit_module_time ON sys_audit_trail (module_name, timestamp_utc DESC);
