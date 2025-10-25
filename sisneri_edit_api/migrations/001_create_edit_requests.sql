CREATE TABLE IF NOT EXISTS edit_requests (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  father        TEXT NOT NULL,
  grandfather   TEXT NOT NULL,
  email         TEXT NOT NULL,
  phone_e164    TEXT,
  phone_iso     TEXT,
  phone_dial    TEXT,
  message       TEXT NOT NULL,
  user_agent    TEXT,
  ip            TEXT,
  created_at    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_edit_requests_created ON edit_requests(created_at);