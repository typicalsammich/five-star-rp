CREATE TABLE contact_rate_limits (
    bucket TEXT PRIMARY KEY NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    expires_at INTEGER NOT NULL
);
CREATE INDEX contact_rate_limits_expiry ON contact_rate_limits(expires_at);
