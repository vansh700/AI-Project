## Architecture Invariants

Frontend communicates ONLY with MS1.

MS2 is never exposed publicly.

Every analysis request passes through BullMQ.

MS1 owns business data.

MS2 owns execution state.

Databases are never shared.

Workers are stateless.

MS2 communicates completion only through webhooks.

Frontend receives updates only from MS1 WebSockets.