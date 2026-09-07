from pathlib import Path
import sqlite3
import tempfile

from paprika_database import PaprikaDatabase


def main():
    temp_dir = Path(tempfile.mkdtemp(prefix="paprika_db_test_"))
    database_path = temp_dir / "paprika_test.db"

    database = PaprikaDatabase(database_path)
    database.create_database(reset=True)

    schema = database.validate_schema()

    assert set(schema["tables"]) == database.EXPECTED_TABLES

    media_id, run_id, leaf_id = database.create_test_record()

    with database.connect() as connection:
        media = connection.execute(
            "SELECT * FROM media_objects WHERE id = ?",
            (media_id,),
        ).fetchone()
        run = connection.execute(
            "SELECT * FROM segmentation_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        leaf = connection.execute(
            "SELECT * FROM leaf_objects WHERE id = ?",
            (leaf_id,),
        ).fetchone()

        assert media is not None
        assert run is not None
        assert leaf is not None
        assert run["media_id"] == media_id
        assert leaf["run_id"] == run_id

        connection.execute(
            "DELETE FROM segmentation_runs WHERE id = ?",
            (run_id,),
        )

        deleted_leaf = connection.execute(
            "SELECT * FROM leaf_objects WHERE id = ?",
            (leaf_id,),
        ).fetchone()

        assert deleted_leaf is None

    with sqlite3.connect(database_path) as connection:
        integrity = connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]

    assert integrity == "ok"

    print("ALL DATABASE SCHEMA + CRUD + FOREIGN KEY + INTEGRITY TESTS PASSED")
    print(f"TEST DB: {database_path}")


if __name__ == "__main__":
    main()
