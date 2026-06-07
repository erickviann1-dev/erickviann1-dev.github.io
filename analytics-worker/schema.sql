CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  site TEXT NOT NULL,
  event TEXT NOT NULL,
  path TEXT NOT NULL,
  section TEXT NOT NULL DEFAULT '',
  referrer_host TEXT NOT NULL DEFAULT 'direct',
  lang TEXT NOT NULL DEFAULT '',
  viewport TEXT NOT NULL DEFAULT '',
  session_id TEXT NOT NULL,
  ip TEXT NOT NULL,
  location TEXT NOT NULL DEFAULT '',
  country TEXT NOT NULL DEFAULT '',
  region TEXT NOT NULL DEFAULT '',
  city TEXT NOT NULL DEFAULT '',
  colo TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_path_ts ON events(path, ts);
CREATE INDEX IF NOT EXISTS idx_events_event_ts ON events(event, ts);
CREATE INDEX IF NOT EXISTS idx_events_session_ts ON events(session_id, ts);
CREATE INDEX IF NOT EXISTS idx_events_ip_ts ON events(ip, ts);
CREATE INDEX IF NOT EXISTS idx_events_location_ts ON events(location, ts);
