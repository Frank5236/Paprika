from datetime import datetime
from pathlib import Path
import sqlite3


DATABASE_PATH = Path(r"C:\paprika\data\paprika.db")


class PaprikaDatabase:

    TABLES = (
        "change_events",
        "leaf_track_members",
        "object_tracks",
        "leaf_measurements",
        "segmentation_artifacts",
        "leaf_objects",
        "segmentation_runs",
        "media_objects",
    )

    EXPECTED_TABLES = {
        "media_objects",
        "segmentation_runs",
        "leaf_objects",
        "leaf_measurements",
        "segmentation_artifacts",
        "object_tracks",
        "leaf_track_members",
        "change_events",
    }

    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self):
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_database(self, reset=True):
        if reset and self.database_path.exists():
            self.database_path.unlink()

        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE media_objects (
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

                CREATE TABLE segmentation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_name TEXT NOT NULL UNIQUE,
                    media_id INTEGER NOT NULL,
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

                CREATE TABLE leaf_objects (
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

                CREATE TABLE leaf_measurements (
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

                CREATE TABLE segmentation_artifacts (
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

                CREATE TABLE object_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    track_code TEXT NOT NULL,
                    object_type TEXT NOT NULL DEFAULT 'leaf',
                    created_at TEXT NOT NULL,
                    UNIQUE (track_code, object_type)
                );

                CREATE TABLE leaf_track_members (
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

                CREATE TABLE change_events (
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

                CREATE INDEX idx_media_capture
                    ON media_objects(capture_date, capture_time);

                CREATE INDEX idx_media_checksum
                    ON media_objects(checksum_sha256);

                CREATE INDEX idx_runs_media
                    ON segmentation_runs(media_id);

                CREATE INDEX idx_runs_datetime
                    ON segmentation_runs(segmentation_date, segmentation_time);

                CREATE INDEX idx_runs_status
                    ON segmentation_runs(status);

                CREATE INDEX idx_artifacts_run
                    ON segmentation_artifacts(run_id);

                CREATE INDEX idx_artifacts_type
                    ON segmentation_artifacts(artifact_type);

                CREATE INDEX idx_leaves_run
                    ON leaf_objects(run_id);

                CREATE INDEX idx_leaves_saved
                    ON leaf_objects(saved);

                CREATE INDEX idx_measurements_leaf
                    ON leaf_measurements(leaf_id, measured_at);

                CREATE INDEX idx_tracks_code
                    ON object_tracks(track_code);

                CREATE INDEX idx_track_members_track
                    ON leaf_track_members(track_id);

                CREATE INDEX idx_track_members_leaf
                    ON leaf_track_members(leaf_id);

                CREATE INDEX idx_change_track
                    ON change_events(track_id, detected_at);

                CREATE INDEX idx_change_type
                    ON change_events(change_type);
                """
            )

    def get_table_names(self):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()

        return {row[0] for row in rows}

    def get_table_columns(self, table_name):
        with self.connect() as connection:
            rows = connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()

        return [row[1] for row in rows]

    def validate_schema(self):
        actual_tables = self.get_table_names()
        missing_tables = self.EXPECTED_TABLES - actual_tables
        extra_tables = actual_tables - self.EXPECTED_TABLES

        if missing_tables:
            raise RuntimeError(
                "Missing tables: " + ", ".join(sorted(missing_tables))
            )

        required_columns = {
            "media_objects": {
                "id",
                "file_name",
                "file_path",
                "file_type",
                "created_at",
            },
            "segmentation_runs": {
                "id",
                "run_name",
                "media_id",
                "source_file",
                "segmentation_date",
                "segmentation_time",
                "roi_enabled",
                "roi_x1",
                "roi_y1",
                "roi_x2",
                "roi_y2",
                "model_name",
                "model_path",
                "status",
                "created_at",
            },
            "leaf_objects": {
                "id",
                "run_id",
                "leaf_number",
                "x1",
                "y1",
                "x2",
                "y2",
                "area",
                "saved",
                "original_path",
                "highlighted_path",
                "segmented_path",
                "crop_path",
                "overlay_path",
                "mask_path",
            },
            "leaf_measurements": {
                "id",
                "leaf_id",
                "measured_at",
                "green_percent",
                "yellow_percent",
                "brown_percent",
                "damage_percent",
                "disease_score",
                "water_stress_score",
                "health_score",
            },
            "segmentation_artifacts": {
                "id",
                "run_id",
                "artifact_type",
                "file_name",
                "file_path",
            },
            "object_tracks": {
                "id",
                "track_code",
                "object_type",
            },
            "leaf_track_members": {
                "id",
                "track_id",
                "leaf_id",
                "match_score",
            },
            "change_events": {
                "id",
                "track_id",
                "from_leaf_id",
                "to_leaf_id",
                "change_type",
                "metric_name",
                "old_value",
                "new_value",
                "change_percent",
            },
        }

        for table_name, expected_columns in required_columns.items():
            actual_columns = set(self.get_table_columns(table_name))
            missing_columns = expected_columns - actual_columns

            if missing_columns:
                raise RuntimeError(
                    f"Missing columns in {table_name}: "
                    + ", ".join(sorted(missing_columns))
                )

        with self.connect() as connection:
            foreign_keys = connection.execute(
                "PRAGMA foreign_keys"
            ).fetchone()[0]

            if foreign_keys != 1:
                raise RuntimeError("SQLite foreign_keys is not enabled")

        return {
            "database_path": str(self.database_path),
            "tables": sorted(actual_tables),
            "extra_tables": sorted(extra_tables),
        }

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
        checksum_sha256=None,
    ):
        created_at = datetime.now().isoformat(timespec="seconds")

        with self.connect() as connection:
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
                    created_at,
                ),
            )
            return cursor.lastrowid

    def create_test_record(self):
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        media_id = self.create_media(
            file_name="db_test.jpg",
            file_path=r"C:\paprika\test\db_test.jpg",
            file_type="image",
            extension=".jpg",
            width=100,
            height=100,
            capture_date=now.strftime("%Y-%m-%d"),
            capture_time=now.strftime("%H:%M:%S"),
        )

        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO segmentation_runs (
                    run_name,
                    media_id,
                    source_file,
                    source_path,
                    segmentation_date,
                    segmentation_time,
                    image_width,
                    image_height,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"DB_TEST_{timestamp}",
                    media_id,
                    "db_test.jpg",
                    r"C:\paprika\test\db_test.jpg",
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    100,
                    100,
                    "completed",
                    now.isoformat(timespec="seconds"),
                ),
            )

            run_id = cursor.lastrowid

            cursor = connection.execute(
                """
                INSERT INTO leaf_objects (
                    run_id,
                    leaf_number,
                    x1,
                    y1,
                    x2,
                    y2,
                    center_x,
                    center_y,
                    width,
                    height,
                    area,
                    confidence,
                    saved,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    1,
                    10,
                    20,
                    60,
                    80,
                    35.0,
                    50.0,
                    50,
                    60,
                    3000,
                    0.95,
                    1,
                    now.isoformat(timespec="seconds"),
                ),
            )

            leaf_id = cursor.lastrowid

        return media_id, run_id, leaf_id


if __name__ == "__main__":
    database = PaprikaDatabase()
    database.create_database(reset=True)
    schema = database.validate_schema()

    print("PAPRIKA DATABASE CREATED")
    print(schema["database_path"])
    print("TABLES:")
    for table_name in schema["tables"]:
        print(f"  {table_name}")
