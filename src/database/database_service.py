from datetime import datetime
from pathlib import Path

from paprika_database import PaprikaDatabase


class DatabaseService:

    def __init__(
        self,
        database_path=None
    ):

        if database_path is None:

            self.database = PaprikaDatabase()

        else:

            self.database = PaprikaDatabase(
                Path(database_path)
            )

        self.database.create_database()

    def create_run(
        self,
        run_name,
        source_file,
        source_path=None,
        capture_date=None,
        capture_time=None,
        image_width=None,
        image_height=None,
        roi=None
    ):

        if roi is not None:

            if len(roi) != 4:

                raise ValueError(
                    "ROI must contain X1, Y1, X2, Y2."
                )

            roi_x1, roi_y1, roi_x2, roi_y2 = roi
            roi_enabled = True

        else:

            roi_x1 = None
            roi_y1 = None
            roi_x2 = None
            roi_y2 = None
            roi_enabled = False

        now = datetime.now()

        return self.database.create_segmentation_run(
            run_name=run_name,
            source_file=source_file,
            source_path=source_path,
            capture_date=capture_date,
            capture_time=capture_time,
            segmentation_date=now.strftime("%Y-%m-%d"),
            segmentation_time=now.strftime("%H:%M:%S"),
            image_width=image_width,
            image_height=image_height,
            roi_enabled=roi_enabled,
            roi_x1=roi_x1,
            roi_y1=roi_y1,
            roi_x2=roi_x2,
            roi_y2=roi_y2
        )

    def get_run(
        self,
        run_id
    ):

        return self.database.get_segmentation_run(
            run_id
        )

    def list_runs(
        self
    ):

        return self.database.list_segmentation_runs()

    def update_run(
        self,
        run_id,
        **fields
    ):

        return self.database.update_segmentation_run(
            run_id,
            **fields
        )

    def delete_run(
        self,
        run_id
    ):

        return self.database.delete_segmentation_run(
            run_id
        )

    def create_leaf(
        self,
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
        original_path=None,
        highlighted_path=None,
        segmented_path=None,
        crop_path=None,
        overlay_path=None,
        mask_path=None
    ):

        return self.database.create_leaf(
            run_id=run_id,
            leaf_number=leaf_number,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            center_x=center_x,
            center_y=center_y,
            width=width,
            height=height,
            area=area,
            original_path=original_path,
            highlighted_path=highlighted_path,
            segmented_path=segmented_path,
            crop_path=crop_path,
            overlay_path=overlay_path,
            mask_path=mask_path
        )

    def get_leaf(
        self,
        leaf_id
    ):

        return self.database.get_leaf(
            leaf_id
        )

    def list_leaves(
        self,
        run_id
    ):

        return self.database.list_leaves_by_run(
            run_id
        )

    def update_leaf(
        self,
        leaf_id,
        **fields
    ):

        return self.database.update_leaf(
            leaf_id,
            **fields
        )

    def delete_leaf(
        self,
        leaf_id
    ):

        return self.database.delete_leaf(
            leaf_id
        )


if __name__ == "__main__":

    service = DatabaseService()

    print(
        "DATABASE SERVICE READY:"
    )

    print(
        service.database.database_path
    )
