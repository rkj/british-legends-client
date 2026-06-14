# Developer Notes & Safety Guidelines

## Critical Rules

**1. NEVER spam connections to the MUD Server**
When coding network features (especially reconnect logic or background tasks), ensure that you do NOT accidentally rapidly spawn multiple active connections or leave "ghost threads" running. MUD servers employ strict anti-bot and anti-spam measures. Spawning multiple connections simultaneously or polling connections too fast without closing old ones will trip their automated defenses and result in a temporary IP ban.

**2. Always manage threads safely**
When creating a background loop (e.g. `mud_reader_loop`), ensure the thread has a condition to cleanly exit if it is no longer the primary thread. Never leave an infinite `while True` loop running without checking the global state, as this steals socket data and leaks threads.

**3. Inform the UI on Disconnect**
If a connection is dropped or closed by the server, do not silently swallow the error. The background thread must report the failure to the frontend (e.g., via `mud_buffer`) so the user knows they have been disconnected and can trigger a manual reconnect when ready.
