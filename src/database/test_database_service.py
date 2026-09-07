from pathlib import Path
import shutil
import tempfile

from database_service import DatabaseService
from paprika_database import PaprikaDatabase


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():

    temp_root = Path(tempfile.mkdtemp(prefix="paprika_service_test_"))
    test_db = temp_root / "paprika_test.db"

    try:
        database = PaprikaDatabase(test_db)
        database.create_database(reset=True)
        database.validate_schema()

        service = DatabaseService(test_db)

        media_id = service.create_media(
            file_name="service_test.jpg",
            file_path=r"C:\paprika\test\service_test.jpg",
            file_type="image",
            extension=".jpg",
            width=640,
            height=480,
            capture_date="2026-09-07",
            capture_time="15:00:00",
        )

        check(media_id is not None, "MEDIA CREATE FAILED")

        run_id = service.create_run(
            run_name="SERVICE_TEST_RUN",
            media_id=media_id,
            source_file="service_test.jpg",
            source_path=r"C:\paprika\test\service_test.jpg",
            image_width=640,
            image_height=480,
            roi=(10, 20, 300, 400),
            model_name="sam2.1_b",
            model_path=r"C:\paprika\images\sam2.1_b.pt",
            status="completed",
            duration_seconds=12.5,
        )

        check(run_id is not None, "RUN CREATE FAILED")

        run = service.get_run(run_id)
        check(run is not None, "RUN GET FAILED")
        check(run["media_id"] == media_id, "RUN MEDIA LINK FAILED")
        check(run["roi_enabled"] == 1, "ROI FLAG FAILED")
        check(run["roi_x1"] == 10, "ROI X1 FAILED")
        check(run["roi_y2"] == 400, "ROI Y2 FAILED")

        runs = service.list_runs()
        check(len(runs) == 1, "RUN LIST FAILED")

        updated = service.update_run(
            run_id,
            status="processing",
            duration_seconds=20.0,
        )
        check(updated is not None, "RUN UPDATE FAILED")

        run = service.get_run(run_id)
        check(run["status"] == "processing", "RUN STATUS UPDATE FAILED")
        check(run["duration_seconds"] == 20.0, "RUN DURATION UPDATE FAILED")

        leaf_id = service.create_leaf(
            run_id=run_id,
            leaf_number=1,
            x1=100,
            y1=120,
            x2=220,
            y2=300,
            center_x=160.0,
            center_y=210.0,
            width=120,
            height=180,
            area=15000,
            confidence=0.94,
            selected=True,
            saved=True,
            original_path=r"C:\paprika\results\original.jpg",
            highlighted_path=r"C:\paprika\results\highlighted.jpg",
            segmented_path=r"C:\paprika\results\segmented.png",
            crop_path=r"C:\paprika\results\crop.png",
            overlay_path=r"C:\paprika\results\overlay.png",
            mask_path=r"C:\paprika\results\mask.png",
        )

        check(leaf_id is not None, "LEAF CREATE FAILED")

        leaf = service.get_leaf(leaf_id)
        check(leaf is not None, "LEAF GET FAILED")
        check(leaf["run_id"] == run_id, "LEAF RUN LINK FAILED")
        check(leaf["saved"] == 1, "LEAF SAVED FLAG FAILED")
        check(leaf["mask_path"] == r"C:\paprika\results\mask.png", "LEAF MASK PATH FAILED")

        leaves = service.list_leaves(run_id)
        check(len(leaves) == 1, "LEAF LIST FAILED")

        updated = service.update_leaf(
            leaf_id,
            confidence=0.98,
            selected=False,
        )
        check(updated is not None, "LEAF UPDATE FAILED")

        leaf = service.get_leaf(leaf_id)
        check(leaf["confidence"] == 0.98, "LEAF CONFIDENCE UPDATE FAILED")
        check(leaf["selected"] == 0, "LEAF SELECTED UPDATE FAILED")

        deleted_leaf = service.delete_leaf(leaf_id)
        check(deleted_leaf is True, "LEAF DELETE FAILED")
        check(service.get_leaf(leaf_id) is None, "LEAF STILL EXISTS")

        deleted_run = service.delete_run(run_id)
        check(deleted_run is True, "RUN DELETE FAILED")
        check(service.get_run(run_id) is None, "RUN STILL EXISTS")

        print("DATABASE SERVICE CRUD TEST PASSED")
        print(f"TEST DB: {test_db}")

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
