# Real-time Features, Common Problems, and Recommended Solutions

This file explains real-time use-cases relevant to the project, typical problems encountered when implementing them, and pragmatic solutions and trade-offs.

Common real-time features for this kind of platform
- Live notifications (assignment updates, grades, announcements)
- Chat between students and teachers or support chat
- Live attendance or presence indicators for classes
- Real-time dashboard updates (active users, submission counts)
- Collaborative features (editing comments, live Q&A)

Recommended stack for real-time
- **Django Channels (ASGI)** for WebSocket support and background channel layers.
- **Redis** as the channel layer and lightweight pub/sub broker.
- **Daphne** or **Uvicorn** as the ASGI server.
- **Celery** for background jobs and tasks triggered by real-time events.

Common problems and solutions

1) Authentication over WebSockets
- Problem: HTTP cookies/session auth differ from WebSocket handshake.
- Solution: Use token-based auth (DRF token, JWT) for WS connections OR reuse the session cookie by performing the proper cookie-based handshake server-side. Ensure secure transmission (wss + secure cookies).

2) Scaling and horizontal instances
- Problem: WebSocket connections are stateful; scaling requires shared channel layers.
- Solution: Use Redis as a central channel layer. For large scale, use a managed pub/sub (e.g., AWS ElastiCache, Google Memorystore) and consider a message broker like Kafka for heavy event throughput. Use sticky sessions only if required by architecture; prefer stateless message passing via Redis.

3) Delivery guarantees and message persistence
- Problem: Messages lost when server restarts or Redis is volatile.
- Solution: Persist important messages to the database (message store) and replay on reconnect. Use Redis only for live delivery and DB for durable storage.

4) Connection churn and reconnection handling
- Problem: Mobile clients or flaky networks cause frequent connect/disconnect.
- Solution: Implement exponential backoff reconnect logic on client; server should allow idempotent reconnection flows and re-synchronization endpoints (e.g., fetch missed notifications since timestamp).

5) Authorization & permissions for channels
- Problem: Unrestricted channels leak information.
- Solution: Validate authentication and permissions during the WebSocket connect event; ensure channel subscribe topics include user id or course id with permission checks.

6) Race conditions and ordering
- Problem: Concurrent updates (e.g., multiple graders) can cause inconsistent state.
- Solution: Use database-level transactions and optimistic locking where appropriate. For real-time UI, reflect optimistic UI updates but reconcile with authoritative server state.

7) Testing real-time code
- Problem: Hard to write deterministic tests for WebSockets.
- Solution: Use `channels.testing` utilities (Channels' `Communicator`) and pytest to create deterministic tests. Simulate connect/disconnect and message flows; add unit tests for message handlers.

8) Security (XSS, injection, DoS)
- Problem: Realtime endpoints are new attack surface.
- Solution: Sanitize all input, limit message size, rate-limit per connection, use authentication, and configure WAF/edge protections. Monitor unusual connection rates.

9) Monitoring and observability
- Problem: Silent failures or slow message delivery.
- Solution: Add metrics for connections, messages/sec, message latency, and error rates. Use Sentry for errors and Prometheus/Grafana for metrics.

Pattern: Hybrid approach (WebSocket + polling fallback)
- Use WebSockets for live UX where timeliness matters; provide a RESTful fallback (poll every N seconds) for clients that cannot open WS connections.

Example architecture for notifications
- Client connects via WebSocket with JWT.
- Server authenticates on connect and subscribes the client to channels: `user.{user_id}` and optional `course.{course_id}`.
- When an event occurs (new assignment, grade posted), the server:
  1. Persists notification record to DB.
  2. Publishes a small event to Redis channel layer.
  3. Connected clients receive the message and optionally fetch full details via REST if needed.

Deployment considerations
- Use separate workers for Channels and HTTP if needed: ASGI server processes for Channels and Gunicorn for WSGI worker tasks.
- Ensure Redis and Celery are on highly available infrastructure (managed services recommended).
- Test with thousands of simulated connections to find bottlenecks.

Next steps
- I can add a simple example implementation: a notifications WebSocket consumer, Redis configuration, and a small JavaScript snippet to connect and display notifications. Would you like that example created in the repo now?
