# Notification System Design

# Stage 1: API Design & Contract

### Core Actions
1. **Fetch Notifications**: Retrieve unread/read notifications for a logged-in user with pagination options.
2. **Mark Notification as Read**: Change status of individual notification items to read.
3. **Mark All as Read**: Mark all notifications as read at once.
4. **Delete Notification**: Clear specific notifications from the user interface.
5. **Manage Notification Preferences**: Allow setting custom weights/channel limits.

### API Endpoints and Schema Contracts

#### 1. Fetch User Notifications
* **Endpoint**: 
* **Headers**:
  ```http
  Authorization: Bearer <JWT_TOKEN>
  Accept: application/json
  ```
* **Query Parameters**:
  * `page` (optional, default: 1)
  * `limit` (optional, default: 20)
  * `status` (optional: `unread`, `read`, `all`)
* **Response (Status Code: 200 OK)**:
  ```json
  {
    "notifications": [
      {
        "id": "e4b312a1-12ef-4d33-9025-a67bcf19129d",
        "type": "Placement",
        "message": "Directi is hiring for Software Engineering roles.",
        "isRead": false,
        "createdAt": "2026-06-30T10:30:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "pageSize": 20,
      "totalPages": 5,
      "totalCount": 98
    }
  }
  ```

#### 2. Mark Notification as Read
* **Endpoint**: `PATCH /api/v1/notifications/{id}/read`
* **Headers**:
  ```http
  Authorization: Bearer <JWT_TOKEN>
  Content-Type: application/json
  ```
* **Response (Status Code: 200 OK)**:
  ```json
  {
    "success": true,
    "id": "e4b312a1-12ef-4d33-9025-a67bcf19129d",
    "isRead": true
  }
  ```

#### 3. Mark All Notifications as Read
* **Endpoint**: `POST /api/v1/notifications/read-all`
* **Headers**:
  ```http
  Authorization: Bearer <JWT_TOKEN>
  ```
* **Response (Status Code: 200 OK)**:
  ```json
  {
    "success": true,
    "markedCount": 15
  }
  ```

### Real-Time Notification Delivery Mechanism
* **Chosen Approach**: **WebSockets**.
* **Reasoning**: Unlike HTTP Polling, WebSockets establish a full-duplex persistent TCP connection. This minimizes the metadata overhead of recurring HTTP requests and keeps communication real-time.
* **Handshake Details**:
  * Client requests to upgrade connection to ws: `GET /api/v1/notifications/ws` with `Sec-WebSocket-Key` headers.
  * Server authenticates using the JWT payload via query parameter or cookie and upgrades the socket connection (returning status `101 Switching Protocols`).
* **Frame Event Design**:
  ```json
  {
    "event": "new_notification",
    "data": {
      "id": "78fa9c21-bca2-4809-90bc-2c1b489d812d",
      "type": "Result",
      "message": "Semester 6 Grades are published.",
      "createdAt": "2026-06-30T10:32:00Z"
    }
  }
  ```

---

# Stage 2: Persistent Storage Choice & Schema

### Database Recommendation
We recommend **PostgreSQL**.
* **Why**: PostgreSQL handles ACID compliance natively. Schema configuration is robust and allows foreign keys which ensures system integrity (e.g., a notification cannot reference a student record that does not exist). Furthermore, PostgreSQL handles JSON properties efficiently and has excellent indexing architectures (like B-Tree, GIN) which are critical as data volume grows.

### Schema Definition
```sql
CREATE TYPE notification_type AS ENUM ('Placement', 'Result', 'Event');

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    roll_no VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crucial composite index for common query optimizations
CREATE INDEX idx_student_unread ON notifications(student_id, is_read, created_at DESC);
```

### Potential Problems with High Scale
1. **Table Bloat**: High volumes (e.g. millions of alerts per month) lead to large tables, causing index traversal to slow down.
2. **Read/Write Bottlenecks**: Bulk operations (like "Notify All") will lock resources and delay simple read operations for students.

### Scale Mitigation Strategies
* **Database Partitioning**: Partition the `notifications` table by year/month (Range partitioning) or hash of `student_id`.
* **Hot/Cold Storage Splitting**: Keep notifications active for only 30 days in the main PostgreSQL DB. Archive old read notifications into cheaper cold storage (e.g., Amazon S3, parquet storage).
* **Caching**: Cache total unread counts in Redis.

### Sample DB Queries
* **Fetch Unread Notifications (Paginated)**:
  ```sql
  SELECT id, notification_type, message, is_read, created_at 
  FROM notifications 
  WHERE student_id = 1042 AND is_read = FALSE 
  ORDER BY created_at DESC 
  LIMIT 20 OFFSET 0;
  ```
* **Mark single notification as read**:
  ```sql
  UPDATE notifications 
  SET is_read = TRUE 
  WHERE id = 'e4b312a1-12ef-4d33-9025-a67bcf19129d' AND student_id = 1042;
  ```

---

# Stage 3: Query Optimization Analysis

### Problem Query
```sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```

### Is the query accurate?
Yes, it functions correctly by filtering notification rows for student `1042` that are unread, returning results ordered by publication date descending.

### Why is it slow?
At 5,000,000 notifications:
1. **Lack of Index**: Without a composite index, the database engine must execute a full table scan or use a weak index and then perform a filesort in memory or disk to output the `ORDER BY` statement.
2. **Select Wildcard (`*`)**: Retrieving unnecessary columns adds excessive input/output load.

### Solution & Computational Cost
Create a Composite Index:
```sql
CREATE INDEX idx_student_unread_sort ON notifications (studentID, isRead, createdAt DESC);
```
* **Cost Impact**:
  * **Read query cost**: Dropped from $O(N)$ table scans to $O(\log N)$ near-instant index lookups.
  * **Write cost**: Slight overhead on inserts/updates ($O(\log N)$) to keep the index balanced.

### Advice: "Add index on every column"
* **Effectiveness**: **Extremely counterproductive**.
* **Reasoning**:
  1. High storage footprint overhead.
  2. Severely reduces `INSERT` / `UPDATE` performance as the database must rewrite all B-Trees for every write operation.
  3. Query planners can only evaluate and use limited indexes per query; unused indexes sit idle as storage bloat.

### Placement Query (Last 7 Days)
```sql
SELECT DISTINCT studentID 
FROM notifications
WHERE notificationType = 'Placement'
  AND createdAt >= NOW() - INTERVAL '7 days';
```

---

# Stage 4: Performance Optimization

### Caching Strategy
We suggest placing an in-memory **Redis Cache** in front of PostgreSQL.

* **Cache Aside Pattern**: Read request queries Redis first. If a cache miss occurs, the backend database is queried, and the result is stored in Redis with a Time-To-Live (TTL) configuration (e.g. 5 minutes).
* **Write-Through**: New notifications write directly to both PostgreSQL and Redis cache simultaneously.

### Performance Tradeoffs

| Optimization Strategy | Tradeoffs & Challenges |
| :--- | :--- |
| **Cache Aside Pattern** (Redis) | High read speed; risk of stale cache if notification is created or marked read without cache eviction logic. |
| **Write-Through Caching** | High consistency; increased write latency because records write to cache and database concurrently. |
| **API Pagination** | Lowers bandwidth; client side needs to track cursor position. |

---

# Stage 5: Notify All Scale & Resiliency

### Shortcomings of Original Sync Implementation
1. **Synchronous Execution Block**: Doing `send_email` sequentially over 50,000 iterations takes hours and will trigger client timeouts.
2. **Lack of Transaction Fault-Tolerance**: If it crashes midway at index 32,500, we don't know who has been notified.
3. **No Retries**: Fails indefinitely for the 200 students if their network is briefly offline.

### Redesigned Architecture (Reliable & Fast)
We introduce an **Asynchronous Message Queue** (e.g. RabbitMQ, SQS, or Celery).

* **Producer**: API Endpoint receives "Notify All" requests, pushes the broadcast job to the Message Queue, and immediately returns a success status code `202 Accepted` to the client.
* **Consumer Workers**: Multi-threaded/concurrect workers pull jobs from the queue in batches and complete sending tasks independently.

### DB Operations & Email Separated?
**Yes, they should be asynchronous and decoupled.**
* **Reason**: Writing to the database is an internal network operation. Sending an email requires communicating with external services (e.g., SMTP servers, AWS SES), which can fail or take seconds. If grouped together in a single transaction, email failures will rollback database writes, leaving the system inconsistent.

### Redesigned Resilient Pseudocode
```python

def notify_all_endpoint(student_ids, message):
    # Enqueue a single bulk event job and return immediately to UI
    message_broker.publish("broadcast_notification_job", {
        "student_ids": student_ids,
        "message": message
    })
    return {"status": "Processing broadcast request."}


def process_broadcast_notification_job(payload):
    student_ids = payload["student_ids"]
    message = payload["message"]
    

    for batch in chunk_list(student_ids, 1000):
        # Enqueue individual worker sub-tasks to process concurrently
        for student_id in batch:
            message_broker.publish("send_email_task", {"student_id": student_id, "message": message})
            message_broker.publish("save_db_task", {"student_id": student_id, "message": message})
            message_broker.publish("push_app_task", {"student_id": student_id, "message": message})

# Individual Worker Task with Retries
@task(max_retries=3, backoff_seconds=10)
def send_email_task(student_id, message):
    email = db.fetch_student_email(student_id)
    try:
        email_client.send(email, message)
    except TemporaryNetworkError as exc:
        # Puts message back into retry queue
        raise retry(exc)
```

---

# Stage 6: Priority Inbox Implementation

### Algorithmic Approach
To construct the Priority Inbox, we need to rank notifications based on:
1. **Weight**: `Placement` (weight 3) > `Result` (weight 2) > `Event` (weight 1).
2. **Recency**: Newer notifications rank higher.

Instead of retrieving all notifications, sorting them in memory ($O(M \log M)$), and keeping only the top 10, we utilize a **Min-Heap** of capacity 10.
* For each incoming notification, we evaluate its score tuple: `(weight, timestamp)`.
* We push it to our heap. If the heap exceeds 10 elements, we pop the smallest one.
* **Complexity**: For $M$ notifications, maintaining the top 10 requires only $O(M \log 10) = O(M)$ time. This is optimal and highly efficient for high-scale, real-time incoming data streams.
