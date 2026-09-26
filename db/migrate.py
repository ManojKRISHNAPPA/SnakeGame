import os
import time
from pathlib import Path

import psycopg


def database_url() -> str:
    return (
        f"postgresql://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.getenv('DB_PORT', '5432')}/{os.environ['DB_NAME']}"
        f"?sslmode={os.getenv('DB_SSLMODE', 'require')}"
    )


def connect_with_retry() -> psycopg.Connection:
    attempts = int(os.getenv('DB_CONNECT_ATTEMPTS', '12'))
    for attempt in range(1, attempts + 1):
        try:
            return psycopg.connect(database_url())
        except psycopg.OperationalError as error:
            if attempt == attempts:
                raise
            print(f"Database connection attempt {attempt}/{attempts} failed: {error}", flush=True)
            time.sleep(5)
    raise RuntimeError("Unable to connect to PostgreSQL.")


def main() -> None:
    schema = Path(__file__).with_name('schema.sql').read_text(encoding='utf-8')
    with connect_with_retry() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema)
        connection.commit()
    print('Database migration completed successfully.', flush=True)


if __name__ == '__main__':
    main()