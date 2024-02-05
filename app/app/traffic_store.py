import json
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
from sqlite3 import Connection, Cursor
from uuid import uuid4


class Query(ABC):
    @abstractmethod
    @abstractproperty
    def _execute(self, cursor: Cursor):
        pass


class TrafficStore:
    def __init__(self):
        self.__db = Connection(
            # database="./data/traffic_store.db", check_same_thread=False,
            database=":memory:", check_same_thread=False,
            isolation_level=None
        )
        self.run(CreateStore())

    def run(self, query: Query):
        with self.__db:
            result = query._execute(self.__db.cursor())

        return result


class CreateStore(Query):
    def _execute(self, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS traffic(
                id TEXT PRIMARY KEY,
                data TEXT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE VIEW IF NOT EXISTS statistics AS
	            SELECT count(id) as packets_count, created FROM traffic group by created ORDER BY created DESC;
            """
        )


class InsertMany(Query):
    def __init__(self, *rows):
        self.data = tuple({"id": str(uuid4()), "data": json.dumps(row)} for row in rows)

    def _execute(self, cursor: Cursor) -> None:
        cursor.executemany(
            "INSERT INTO traffic(id, data) VALUES(:id, :data)", self.data
        )


class GetRecordsSince(Query):
    def __init__(
        self, seconds_offset: int, threshold: int = 1_000, additional_count: int = 1_000
    ):
        self.__threshold = threshold
        self.__additional_records_count = additional_count
        self.offset = int(datetime.now().timestamp()) - seconds_offset

    def _execute(self, cursor: Cursor):
        return cursor.execute(
            f"""
            SELECT id, created FROM traffic
                WHERE created > DATETIME({self.offset}, 'unixepoch')

            UNION

            SELECT id, created FROM ( 
                SELECT id, created FROM traffic
                    WHERE (
                        SELECT COUNT(*)
                        FROM traffic
                        WHERE created > DATETIME({self.offset}, 'unixepoch')
                    ) <= {self.__threshold}
                LIMIT {self.__additional_records_count}
            )
            """
        ).fetchall()


class GetStatsSince(Query):
    def __init__(self, time_offset: int):
        self.__threshold = int(datetime.now().timestamp()) - time_offset

    def _execute(self, cursor: Cursor):
        resp = cursor.execute(
            f"SELECT packets_count FROM statistics WHERE created > DATETIME({self.__threshold}, 'unixepoch')"
        ).fetchall()
        return tuple(row[0] for row in resp)


class GetStatsRows(Query):
    def __init__(
        self, rows_count: int = 120
    ):
        self.__rows = rows_count

    def _execute(self, cursor: Cursor):
        resp = cursor.execute(
            f"SELECT packets_count FROM statistics LIMIT {self.__rows}"
        ).fetchall()
        return tuple(row[0] for row in resp)


class DeleteAfter(Query):
    def __init__(self, time_sec: int):
        self.__threshold = int(datetime.now().timestamp()) - time_sec

    def _execute(self, cursor: Cursor) -> None:
        cursor.execute(
            f"DELETE FROM traffic WHERE created < DATETIME({self.__threshold}, 'unixepoch')"
        )


# SELECT count(id), created FROM traffic group by created
if __name__ == "__main__":
    TrafficStore()
