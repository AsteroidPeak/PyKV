1. Problem Statement
We need a simple in-memory key-value store that lets users quickly set, retrieve, and delete data without having to build their own hash table. For v1, the focus is on correctness and fast average-case lookups while keeping the implementation simple enough to understand and extend later.
2. Goals

* Correctness: Every `set` should be retrievable with `get`, and every `delete` should actually remove the key.
* Speed: Lookups should be O(1) on average.
* Future durability: Data should eventually survive a restart, but this will be handled in Sprint 4 with a write-ahead log. It is not part of the current implementation.

3. Non-Goals

* No clustering or replication. The store will run on a single node only.
* No built-in eviction policy. For now, memory usage is effectively unlimited.
* No TTL or key expiry. This will be added later.

4. Design Decision: Why Dict Over SQLite/LMDB?
For v1, I’m using a Python `dict` because it gives O(1) average-case lookups and keeps the implementation very simple. There is also no serialization or database overhead on every `get`, `set`, or `delete` call. A dict is basically the data structure we need for the core in-memory part, so there is less abstraction to deal with while building the system.
The main downside is that a dict does not provide persistence. With SQLite, durability comes built in, while with a dict we will have to build our own persistence layer using a write-ahead log in Sprint 4. For this project, I think that trade-off is worth it. We are building infrastructure rather than just using an existing database, so using a dict gives us a simpler starting point and lets us understand and implement durability ourselves later.