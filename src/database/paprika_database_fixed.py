from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sqlite3


DATABASE_PATH = Path(r"C:\paprika\data\paprika.db")


class PaprikaDatabase:

    def __init__(
        self,
        database_path=DATABASE_PATH
    ):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(
            self.database_path
        )
        connection.row_factory = sqlite3.Row
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def connect(self):
        connection = sqlite3.connect(
            self.database_path
        )
        connection.row_factory = sqlite3.Row
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )
        return connection

    def _table_columns(
        self,
        connection,
        table_name
    ):
        rows = connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        return {
            row[1]
            for row in rows
        }

    def _add_column_if_missing(
        self,
        connection,
        table_name,
        column_name,
        column_definition
    ):
        columns = self._table_columns(
            connection,
            table_name
        )

        if column_name not in columns:
            connection.execute(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {column_definition}"
            )

    def _migrate_existing_schema(
        self,
        connection
    ):
        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        if "media_objects" not in tables:
            return

        if "segmentation_runs" in tables:
            segmentation_columns = (
                self._table_columns(
                    connection,
                    "segmentation_runs"
                )
            )

            if "media_id" not in segmentation_columns:
                connection.execute(
                    """
                    ALTER TABLE segmentation_runs
                    ADD COLUMN media_id INTEGER
                    """
                )

                rows = connection.execute(
                    """
                    SELECT id, source_file, source_path
                    FROM segmentation_runs
                    WHERE media_id IS NULL
                    """
                ).fetchall()

                for row in rows:
                    source_file = row[1]
                    source_path = row[2]

                    existing_media = connection.execute(
                        """
                        SELECT id
                        FROM media_objects
                        WHERE file_name = ?
                          AND (
                              file_path = ?
                              OR (? IS NULL AND file_path IS NULL)
                          )
                        LIMIT 1
                        """,
                        (
                            source_file,
                            source_path,
                            source_path
                        )
                    ).fetchone()

                    if existing_media is None:
                        now = datetime.now().isoformat(
                            timespec="seconds"
                        )

                        cursor = connection.execute(
                            """
                            INSERT INTO media_objects (
                                file_name,
                                file_path,
                                file_type,
                                extension,
                                created_at
                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                source_file or "unknown",
                                source_path or "",
                                "image",
                                (
                                    Path(source_file).suffix.lower()
                                    if source_file
                                    else None
                                ),
                                now
                            )
                        )

                        media_id = cursor.lastrowid

                    else:
                        media_id = existing_media[0]

                    connection.execute(
                        """
                        UPDATE segmentation_runs
                        SET media_id = ?
                        WHERE id = ?
                        """,
                        (
                            media_id,
                            row[0]
                        )
                    )

        tables = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        if "segmentation_runs" in tables:
            columns = self._table_columns(
                connection,
                "segmentation_runs"
            )

            missing_columns = {
                "source_file": "TEXT",
                "source_path": "TEXT",
                "capture_date": "TEXT",
                "capture_time": "TEXT",
                "segmentation_date": "TEXT",
                "segmentation_time": "TEXT",
                "image_width": "INTEGER",
                "image_height": "INTEGER",
                "roi_enabled": "INTEGER DEFAULT 0",
                "roi_x1": "INTEGER",
                "roi_y1": "INTEGER",
                "roi_x2": "INTEGER",
                "roi_y2": "INTEGER",
                "model_name": "TEXT",
                "model_path": "TEXT",
                "status": "TEXT",
                "duration_seconds": "REAL",
                "created_at": "TEXT"
            }

            for name, definition in missing_columns.items():
                if name not in columns:
                    self._add_column_if_missing(
                        connection,
                        "segmentation_runs",
                        name,
                        definition
                    )

        if "leaf_objects" in tables:
            columns = self._table_columns(
                connection,
                "leaf_objects"
            )

            missing_columns = {
                "confidence": "REAL",
                "selected": "INTEGER DEFAULT 0",
                "saved": "INTEGER DEFAULT 0",
                "original_path": "TEXT",
                "highlighted_path": "TEXT",
                "segmented_path": "TEXT",
                "crop_path": "TEXT",
                "overlay_path": "TEXT",
                "mask_path": "TEXT",
                "created_at": "TEXT"
            }

            for name, definition in missing_columns.items():
                if name not in columns:
                    self._add_column_if_missing(
                        connection,
                        "leaf_objects",
                        name,
                        definition
                    )

    def create_database(self):
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS media_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    extension TEXT,
                    width INTEGER,
                    height INTEGER,
                    duration_seconds REAL,
                    capture_date TEXT,
                    capture_time TEXT,
                    file_created_at TEXT,
                    file_modified_at TEXT,
                    checksum_sha256 TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS segmentation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_name TEXT NOT NULL UNIQUE,
                    media_id INTEGER,
                    source_file TEXT NOT NULL,
                    source_path TEXT,
                    capture_date TEXT,
                    capture_time TEXT,
                    segmentation_date TEXT NOT NULL,
                    segmentation_time TEXT NOT NULL,
                    image_width INTEGER,
                    image_height INTEGER,
                    roi_enabled INTEGER NOT NULL DEFAULT 0,
                    roi_x1 INTEGER,
                    roi_y1 INTEGER,
                    roi_x2 INTEGER,
                    roi_y2 INTEGER,
                    model_name TEXT,
                    model_path TEXT,
                    status TEXT NOT NULL DEFAULT 'completed',
                    duration_seconds REAL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (media_id)
                        REFERENCES media_objects(id)
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS segmentation_artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    artifact_type TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (run_id)
                        REFERENCES segmentation_runs(id)
                        ON DELETE CASCADE,
                    UNIQUE (run_id, artifact_type, file_path)
                );

                CREATE TABLE IF NOT EXISTS leaf_objects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    leaf_number INTEGER NOT NULL,
                    x1 INTEGER NOT NULL,
                    y1 INTEGER NOT NULL,
                    x2 INTEGER NOT NULL,
                    y2 INTEGER NOT NULL,
                    center_x REAL NOT NULL,
                    center_y REAL NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    area INTEGER NOT NULL,
                    confidence REAL,
                    selected INTEGER NOT NULL DEFAULT 0,
                    saved INTEGER NOT NULL DEFAULT 0,
                    original_path TEXT,
                    highlighted_path TEXT,
                    segmented_path TEXT,
                    crop_path TEXT,
                    overlay_path TEXT,
                    mask_path TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (run_id)
                        REFERENCES segmentation_runs(id)
                        ON DELETE CASCADE,
                    UNIQUE (run_id, leaf_number)
                );

                CREATE TABLE IF NOT EXISTS leaf_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    leaf_id INTEGER NOT NULL,
                    measured_at TEXT NOT NULL,
                    green_percent REAL,
                    yellow_percent REAL,
                    brown_percent REAL,
                    damage_percent REAL,
                    texture_score REAL,
                    disease_score REAL,
                    water_stress_score REAL,
                    health_score REAL,
                    area_pixels REAL,
                    width_pixels REAL,
                    height_pixels REAL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (leaf_id)
                        REFERENCES leaf_objects(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS object_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_code TEXT NOT NULL,
                    object_type TEXT NOT NULL DEFAULT 'leaf',
                    created_at TEXT NOT NULL,
                    UNIQUE (track_code, object_type)
                );

                CREATE TABLE IF NOT EXISTS leaf_track_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_id INTEGER NOT NULL,
                    leaf_id INTEGER NOT NULL,
                    match_score REAL,
                    match_method TEXT,
                    matched_at TEXT NOT NULL,
                    FOREIGN KEY (track_id)
                        REFERENCES object_tracks(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (leaf_id)
                        REFERENCES leaf_objects(id)
                        ON DELETE CASCADE,
                    UNIQUE (track_id, leaf_id)
                );

                CREATE TABLE IF NOT EXISTS change_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_id INTEGER NOT NULL,
                    from_leaf_id INTEGER,
                    to_leaf_id INTEGER,
                    detected_at TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    metric_name TEXT,
                    old_value REAL,
                    new_value REAL,
                    change_value REAL,
                    change_percent REAL,
                    severity TEXT,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (track_id)
                        REFERENCES object_tracks(id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (from_leaf_id)
                        REFERENCES leaf_objects(id)
                        ON DELETE SET NULL,
                    FOREIGN KEY (to_leaf_id)
                        REFERENCES leaf_objects(id)
                        ON DELETE SET NULL
                );

                CREATE INDEX IF NOT EXISTS idx_media_capture
                    ON media_objects(capture_date, capture_time);

                CREATE INDEX IF NOT EXISTS idx_runs_media
                    ON segmentation_runs(media_id);

                CREATE INDEX IF NOT EXISTS idx_runs_capture
                    ON segmentation_runs(segmentation_date, segmentation_time);

                CREATE INDEX IF NOT EXISTS idx_artifacts_run
                    ON segmentation_artifacts(run_id);

                CREATE INDEX IF NOT EXISTS idx_leaves_run
                    ON leaf_objects(run_id);

                CREATE INDEX IF NOT EXISTS idx_leaves_number
                    ON leaf_objects(leaf_number);

                CREATE INDEX IF NOT EXISTS idx_measurements_leaf
                    ON leaf_measurements(leaf_id, measured_at);

                CREATE INDEX IF NOT EXISTS idx_track_members_track
                    ON leaf_track_members(track_id);

                CREATE INDEX IF NOT EXISTS idx_track_members_leaf
                    ON leaf_track_members(leaf_id);

                CREATE INDEX IF NOT EXISTS idx_change_track
                    ON change_events(track_id, detected_at);
                """
            )

            self._migrate_existing_schema(
                connection
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_runs_media
                    ON segmentation_runs(media_id)
                """
            )

            connection.commit()

    def create_media(
        self,
        file_name,
        file_path,
        file_type,
        extension=None,
        width=None,
        height=None,
        duration_seconds=None,
        capture_date=None,
        capture_time=None,
        file_created_at=None,
        file_modified_at=None,
        checksum_sha256=None
    ):
        created_at = datetime.now().isoformat(
            timespec="seconds"
        )

        with self.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO media_objects (
                    file_name,
                    file_path,
                    file_type,
                    extension,
                    width,
                    height,
                    duration_seconds,
                    capture_date,
                    capture_time,
                    file_created_at,
                    file_modified_at,
                    checksum_sha256,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    file_name,
                    file_path,
                    file_type,
                    extension,
                    width,
                    height,
                    duration_seconds,
                    capture_date,
                    capture_time,
                    file_created_at,
                    file_modified_at,
                    checksum_sha256,
                    created_at
                )
            )

            return cursor.lastrowid

    def get_media(self, media_id):
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM media_objects WHERE id = ?",
                (media_id,)
            ).fetchone()

            return dict(row) if row else None

    def create_segmentation_run(
        self,
        run_name,
        media_id,
        source_file,
        source_path=None,
        capture_date=None,
        capture_time=None,
        segmentation_date=None,
        segmentation_time=None,
        image_width=None,
        image_height=None,
        roi_enabled=False,
        roi_x1=None,
        roi_y1=None,
        roi_x2=None,
        roi_y2=None,
        model_name=None,
        model_path=None,
        status="completed",
        duration_seconds=None
    ):
        now = datetime.now()

        if segmentation_date is None:
            segmentation_date = now.strftime(
                "%Y-%m-%d"
            )

        if segmentation_time is None:
            segmentation_time = now.strftime(
                "%H:%M:%S"
            )

        created_at = now.isoformat(
            timespec="seconds"
        )

        with self.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO segmentation_runs (
                    run_name,
                    media_id,
                    source_file,
                    source_path,
                    capture_date,
                    capture_time,
                    segmentation_date,
                    segmentation_time,
                    image_width,
                    image_height,
                    roi_enabled,
                    roi_x1,
                    roi_y1,
                    roi_x2,
                    roi_y2,
                    model_name,
                    model_path,
                    status,
                    duration_seconds,
                    created_at
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    run_name,
                    media_id,
                    source_file,
                    source_path,
                    capture_date,
                    capture_time,
                    segmentation_date,
                    segmentation_time,
                    image_width,
                    image_height,
                    int(roi_enabled),
                    roi_x1,
                    roi_y1,
                    roi_x2,
                    roi_y2,
                    model_name,
                    model_path,
                    status,
                    duration_seconds,
                    created_at
                )
            )

            return cursor.lastrowid

    def get_segmentation_run(self, run_id):
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM segmentation_runs WHERE id = ?",
                (run_id,)
            ).fetchone()

            return dict(row) if row else None

    def create_leaf(self, **fields):
        now = datetime.now().isoformat(
            timespec="seconds"
        )

        fields.setdefault(
            "created_at",
            now
        )
        fields.setdefault(
            "selected",
            0
        )
        fields.setdefault(
            "saved",
            0
        )

        columns = [
            "run_id",
            "leaf_number",
            "x1",
            "y1",
            "x2",
            "y2",
            "center_x",
            "center_y",
            "width",
            "height",
            "area",
            "confidence",
            "selected",
            "saved",
            "original_path",
            "highlighted_path",
            "segmented_path",
            "crop_path",
            "overlay_path",
            "mask_path",
            "created_at"
        ]

        values = [
            fields.get(column)
            for column in columns
        ]

        placeholders = ", ".join(
            "?"
            for _ in columns
        )

        column_sql = ", ".join(
            columns
        )

        with self.connection() as connection:
            cursor = connection.execute(
                f"""
                INSERT INTO leaf_objects ({column_sql})
                VALUES ({placeholders})
                """,
                values
            )

            return cursor.lastrowid

    def get_leaf(self, leaf_id):
        with self.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    l.*,
                    r.run_name,
                    r.source_file,
                    r.source_path,
                    r.capture_date,
                    r.capture_time,
                    r.segmentation_date,
                    r.segmentation_time,
                    r.image_width,
                    r.image_height,
                    r.roi_enabled,
                    r.roi_x1,
                    r.roi_y1,
                    r.roi_x2,
                    r.roi_y2,
                    m.file_path AS media_file_path
                FROM leaf_objects l
                JOIN segmentation_runs r
                    ON r.id = l.run_id
                LEFT JOIN media_objects m
                    ON m.id = r.media_id
                WHERE l.id = ?
                """,
                (leaf_id,)
            ).fetchone()

            return dict(row) if row else None

    def add_measurement(
        self,
        leaf_id,
        **fields
    ):
        now = datetime.now().isoformat(
            timespec="seconds"
        )

        fields.setdefault(
            "measured_at",
            now
        )

        fields.setdefault(
            "created_at",
            now
        )

        columns = [
            "leaf_id",
            "measured_at",
            "green_percent",
            "yellow_percent",
            "brown_percent",
            "damage_percent",
            "texture_score",
            "disease_score",
            "water_stress_score",
            "health_score",
            "area_pixels",
            "width_pixels",
            "height_pixels",
            "notes",
            "created_at"
        ]

        values = [
            leaf_id
        ] + [
            fields.get(column)
            for column in columns[1:]
        ]

        placeholders = ", ".join(
            "?"
            for _ in columns
        )

        column_sql = ", ".join(
            columns
        )

        with self.connection() as connection:
            cursor = connection.execute(
                f"""
                INSERT INTO leaf_measurements (
                    {column_sql}
                )
                VALUES ({placeholders})
                """,
                values
            )

            return cursor.lastrowid


if __name__ == "__main__":
    database = PaprikaDatabase()
    database.create_database()
    print(
        "PAPRIKA DATABASE READY:"
    )
    print(
        database.database_path
    )
