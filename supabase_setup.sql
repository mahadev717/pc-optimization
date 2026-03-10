-- ============================================================
-- SUPABASE TABLE SETUP for Hacker Control Center
-- Run this in: Supabase Dashboard -> SQL Editor -> New Query
-- ============================================================

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username   TEXT    UNIQUE NOT NULL,
    password   TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);

-- 2. LOGINS TABLE
CREATE TABLE IF NOT EXISTS logins (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username   TEXT    NOT NULL,
    ip         TEXT,
    device     TEXT,
    hostname   TEXT,
    logged_at  TEXT    NOT NULL
);

-- 3. SEED DEFAULT USER (username=1, password=1)
INSERT INTO users (username, password, created_at)
VALUES ('1', '1', NOW()::TEXT)
ON CONFLICT (username) DO NOTHING;

-- 4. DISABLE ROW LEVEL SECURITY (for simplicity — your server handles auth)
ALTER TABLE users  ENABLE ROW LEVEL SECURITY;
ALTER TABLE logins ENABLE ROW LEVEL SECURITY;

-- Allow all operations via anon key (public access through your server)
CREATE POLICY "Allow all on users"  ON users  FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on logins" ON logins FOR ALL USING (true) WITH CHECK (true);

-- 5. ACTIVE SESSIONS TABLE
CREATE TABLE IF NOT EXISTS active_sessions (
    username   TEXT PRIMARY KEY,
    last_active TEXT NOT NULL
);
ALTER TABLE active_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on active_sessions" ON active_sessions FOR ALL USING (true) WITH CHECK (true);

-- Done! Your tables are ready.
