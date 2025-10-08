-- Basic schema placeholder
CREATE TABLE IF NOT EXISTS retouch_jobs (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  prompt TEXT,
  status TEXT NOT NULL DEFAULT 'created'
);
