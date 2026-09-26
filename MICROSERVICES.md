# GameApp Microservices

The original Spring MVC application remains unchanged under `src/`. The new services are independent, containerized replacements:

| Folder | Responsibility | Runtime |
| --- | --- | --- |
| `frontend/` | React user interface for login, registration, dashboard, Snake, and Calculator | Nginx |
| `backend/` | JSON API, session authentication, and user business logic | Java 17 / Spring Boot |
| `db/` | Idempotent PostgreSQL schema migration against Amazon RDS | Python 3 / psycopg |

## Start with RDS

1. Copy `.env.example` to `.env` and replace every placeholder with the RDS PostgreSQL endpoint and application credentials.
2. Ensure the RDS security group permits inbound TCP port `5432` from the Docker host or the runtime environment where this is deployed.
3. Run `docker compose up --build`.
4. Open `http://localhost:8088`.

`db-migrate` is a one-shot service. It uses `CREATE TABLE IF NOT EXISTS`, so rerunning it does not erase existing users. The backend uses `spring.jpa.hibernate.ddl-auto=validate`; schema ownership stays in the Python database service.

## API

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Authenticate and create a session |
| `POST` | `/api/auth/logout` | End the current session |
| `GET` | `/api/auth/me` | Get the signed-in user |
| `GET` | `/api/dashboard` | Get dashboard user and total-user count |

The browser sends requests to Nginx on the same origin. Nginx proxies `/api` to `backend`, which preserves the `JSESSIONID` cookie without CORS configuration.

## Deployment Notes

Use separate RDS credentials for the migration job and the Java service in production when possible: the migration role needs DDL privileges, while the application role should only access the `users` table. Store these values in a secret manager or your deployment platform's encrypted environment variables rather than committing `.env`.