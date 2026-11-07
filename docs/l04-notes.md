# L04 notes: system design for the hotel booking app

1. **Peak load**: 1,440 visitors/day × 20 searches/visitor = 28,800 searches/day (0.33 searches/s on average). With a 10× peak factor, peak search traffic is **3.33 searches/second** (**200 searches/minute**, matching scenario S1), generating 133 database queries/second across 40 rooms.
2. **HTTP API and shared database**: Moving reservations from an in-memory list into PostgreSQL behind an HTTP API (`GET /rooms/availability`, `POST /reservations`, `DELETE /reservations/{id}`) allows multiple clients and multiple app instances to share one durable source of truth that survives restarts.
3. **When a cache helps**: `GET /rooms/availability` runs far more often than bookings change (28,800 searches/day vs 20 bookings/day), so cache-aside in Redis with a short TTL and invalidation on writes cuts database queries dramatically while `POST /reservations` continues reading PostgreSQL directly as the source of truth.

