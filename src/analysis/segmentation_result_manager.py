from datetime import datetime
from pathlib import Path
import json
import re
import shutil


BASE_RESULTS_DIR = Path(
    r"C:\paprika\results\segmentation"
)


class SegmentationResultManager:

    def __init__(
        self,
        media_path
    ):

        self.media_path = Path(
            media_path
        )

        self.run_directory = None

        self.saved_at = None

    def _safe_name(
        self,
        name
    ):

        name = Path(
            name
        ).stem

        name = re.sub(
            r"[^A-Za-z0-9_-]+",
            "_",
            name
        )

        name = name.strip(
            "_"
        )

        if not name:

            name = "media"

        return name

    def create_run_directory(
        self
    ):

        if not self.media_path.exists():

            raise FileNotFoundError(
                "Media file not found:\n"
                f"{self.media_path}"
            )

        BASE_RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        safe_name = self._safe_name(
            self.media_path.name
        )

        self.saved_at = datetime.now()

        timestamp = (
            self.saved_at.strftime(
                "%Y%m%d_%H%M%S_%f"
            )
        )

        run_name = (
            f"{safe_name}_{timestamp}"
        )

        self.run_directory = (
            BASE_RESULTS_DIR
            / run_name
        )

        self.run_directory.mkdir(
            parents=True,
            exist_ok=False
        )

        self._create_subdirectories()

        self.copy_original()

        self.save_metadata()

        print(
            "[RESULT MANAGER] "
            f"Run created: {self.run_directory}",
            flush=True
        )

        print(
            "[RESULT MANAGER] "
            f"Saved at: "
            f"{self.saved_at.strftime('%d/%m/%Y %H:%M:%S')}",
            flush=True
        )

        return self.run_directory

    def _create_subdirectories(
        self
    ):

        if self.run_directory is None:

            raise RuntimeError(
                "Run directory was not created."
            )

        for directory_name in (
            "original",
            "masks",
            "leaves",
            "overlay",
        ):

            directory = (
                self.run_directory
                / directory_name
            )

            directory.mkdir(
                parents=True,
                exist_ok=True
            )

    def copy_original(
        self
    ):

        if self.run_directory is None:

            raise RuntimeError(
                "Run directory was not created."
            )

        destination = (
            self.run_directory
            / "original"
            / self.media_path.name
        )

        shutil.copy2(
            self.media_path,
            destination
        )

        print(
            "[RESULT MANAGER] "
            f"Original copied: {destination}",
            flush=True
        )

        return destination

    def save_metadata(
        self
    ):

        if self.run_directory is None:

            raise RuntimeError(
                "Run directory was not created."
            )

        if self.saved_at is None:

            self.saved_at = datetime.now()

        metadata = {
            "source_file": self.media_path.name,
            "source_path": str(
                self.media_path
            ),
            "saved_at": self.saved_at.isoformat(
                timespec="seconds"
            ),
            "saved_at_display": (
                self.saved_at.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            ),
        }

        metadata_path = (
            self.run_directory
            / "metadata.json"
        )

        with metadata_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4,
                ensure_ascii=False
            )

        return metadata_path

    def get_mask_path(
        self,
        leaf_id
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "masks"
            / f"mask_{int(leaf_id):03d}.png"
        )

    def get_leaf_path(
        self,
        leaf_id
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "leaves"
            / f"leaf_{int(leaf_id):03d}.png"
        )

    def get_overlay_path(
        self
    ):

        self._check_run_directory()

        suffix = (
            self.media_path.suffix.lower()
        )

        if suffix in {
            ".jpg",
            ".jpeg",
        }:

            filename = "overlay.jpg"

        else:

            filename = "overlay.png"

        return (
            self.run_directory
            / "overlay"
            / filename
        )

    def get_original_path(
        self
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "original"
            / self.media_path.name
        )

    def get_masks_directory(
        self
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "masks"
        )

    def get_leaves_directory(
        self
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "leaves"
        )

    def get_overlay_directory(
        self
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "overlay"
        )

    def get_metadata_path(
        self
    ):

        self._check_run_directory()

        return (
            self.run_directory
            / "metadata.json"
        )

    def get_run_directory(
        self
    ):

        self._check_run_directory()

        return self.run_directory

    def _check_run_directory(
        self
    ):

        if self.run_directory is None:

            raise RuntimeError(
                "Run directory has not been created yet."
            )