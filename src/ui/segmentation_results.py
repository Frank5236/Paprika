from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
)


RESULTS_ROOT = Path(
    r"C:\paprika\results\segmentation"
)


class SegmentationResults(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "PAPRIKA - SEGMENTATION RESULTS"
        )

        self.resize(
            1100,
            750
        )

        self.run_viewer = None

        self.create_ui()

        self.load_runs()

    def create_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        # ==================================================
        # TITLE
        # ==================================================

        title = QLabel(
            "SEGMENTATION RESULTS"
        )

        title.setStyleSheet(
            "font-size: 26px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        # ==================================================
        # RUN LIST
        # ==================================================

        runs_title = QLabel(
            "SEGMENTATION RUNS"
        )

        runs_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            runs_title
        )

        self.run_list = QListWidget()

        self.run_list.setMinimumHeight(
            180
        )

        main_layout.addWidget(
            self.run_list
        )

        # ==================================================
        # OPEN BUTTON
        # ==================================================

        self.open_button = QPushButton(
            "OPEN SELECTED RUN"
        )

        self.open_button.setMinimumHeight(
            45
        )

        self.open_button.setEnabled(
            False
        )

        main_layout.addWidget(
            self.open_button
        )

        # ==================================================
        # REFRESH BUTTON
        # ==================================================

        self.refresh_button = QPushButton(
            "REFRESH RUNS"
        )

        self.refresh_button.setMinimumHeight(
            40
        )

        main_layout.addWidget(
            self.refresh_button
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = QLabel(
            "Ready"
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(
            self.status_label
        )

        # ==================================================
        # SIGNALS
        # ==================================================

        self.run_list.itemSelectionChanged.connect(
            self.on_run_selected
        )

        self.run_list.itemDoubleClicked.connect(
            self.open_selected_run
        )

        self.open_button.clicked.connect(
            self.open_selected_run
        )

        self.refresh_button.clicked.connect(
            self.load_runs
        )

    def load_runs(self):

        self.run_list.clear()

        self.open_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Loading segmentation runs..."
        )

        if not RESULTS_ROOT.exists():

            self.status_label.setText(
                "No segmentation runs found."
            )

            return

        run_directories = sorted(
            [
                path
                for path in RESULTS_ROOT.iterdir()
                if path.is_dir()
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        if not run_directories:

            self.status_label.setText(
                "No segmentation runs found."
            )

            return

        for run_directory in run_directories:

            item = QListWidgetItem(
                run_directory.name
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                str(run_directory)
            )

            self.run_list.addItem(
                item
            )

        self.status_label.setText(
            f"Found {len(run_directories)} segmentation runs."
        )

    def on_run_selected(self):

        item = (
            self.run_list.currentItem()
        )

        self.open_button.setEnabled(
            item is not None
        )

    def open_selected_run(self):

        item = (
            self.run_list.currentItem()
        )

        if item is None:

            return

        run_directory = item.data(
            Qt.ItemDataRole.UserRole
        )

        self.run_viewer = (
            SegmentationRunViewer(
                Path(run_directory)
            )
        )

        self.run_viewer.show()

        self.run_viewer.raise_()

        self.run_viewer.activateWindow()


class SegmentationRunViewer(QWidget):

    def __init__(
        self,
        run_directory
    ):

        super().__init__()

        self.run_directory = Path(
            run_directory
        )

        self.setWindowTitle(
            (
                "PAPRIKA - "
                f"{self.run_directory.name}"
            )
        )

        self.resize(
            1150,
            850
        )

        self.create_ui()

        self.load_run()

    def create_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        # ==================================================
        # TITLE
        # ==================================================

        title = QLabel(
            (
                "SEGMENTATION RUN\n"
                f"{self.run_directory.name}"
            )
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        # ==================================================
        # ORIGINAL IMAGE
        # ==================================================

        original_title = QLabel(
            "ORIGINAL IMAGE"
        )

        original_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            original_title
        )

        self.original_image = QLabel(
            "Original image not found."
        )

        self.original_image.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.original_image.setMinimumHeight(
            250
        )

        self.original_image.setStyleSheet(
            "border: 1px solid gray;"
        )

        main_layout.addWidget(
            self.original_image
        )

        # ==================================================
        # OVERLAY
        # ==================================================

        overlay_title = QLabel(
            "SEGMENTATION OVERLAY"
        )

        overlay_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            overlay_title
        )

        self.overlay_image = QLabel(
            "Overlay not found."
        )

        self.overlay_image.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.overlay_image.setMinimumHeight(
            250
        )

        self.overlay_image.setStyleSheet(
            "border: 1px solid gray;"
        )

        main_layout.addWidget(
            self.overlay_image
        )

        # ==================================================
        # INDIVIDUAL RESULTS
        # ==================================================

        results_title = QLabel(
            "INDIVIDUAL LEAF RESULTS"
        )

        results_title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            results_title
        )

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.results_container = QWidget()

        self.results_layout = QVBoxLayout(
            self.results_container
        )

        self.scroll_area.setWidget(
            self.results_container
        )

        main_layout.addWidget(
            self.scroll_area
        )

    def load_run(self):

        original_directory = (
            self.run_directory
            / "original"
        )

        overlay_directory = (
            self.run_directory
            / "overlay"
        )

        leaves_directory = (
            self.run_directory
            / "leaves"
        )

        masks_directory = (
            self.run_directory
            / "masks"
        )

        # ==================================================
        # ORIGINAL
        # ==================================================

        original_files = sorted(
            [
                path
                for path in original_directory.iterdir()
                if path.is_file()
            ]
        ) if original_directory.exists() else []

        if original_files:

            self.show_image(
                self.original_image,
                original_files[0],
                950,
                300
            )

        # ==================================================
        # OVERLAY
        # ==================================================

        overlay_files = sorted(
            [
                path
                for path in overlay_directory.iterdir()
                if path.is_file()
            ]
        ) if overlay_directory.exists() else []

        if overlay_files:

            self.show_image(
                self.overlay_image,
                overlay_files[0],
                950,
                300
            )

        # ==================================================
        # LEAF FILES
        # ==================================================

        leaf_files = sorted(
            leaves_directory.glob(
                "leaf_*.png"
            )
        ) if leaves_directory.exists() else []

        mask_files = sorted(
            masks_directory.glob(
                "mask_*.png"
            )
        ) if masks_directory.exists() else []

        mask_map = {
            path.stem.replace(
                "mask_",
                ""
            ): path
            for path in mask_files
        }

        if not leaf_files:

            self.add_message(
                "No individual leaf results found."
            )

            return

        for leaf_path in leaf_files:

            leaf_id = (
                leaf_path.stem.replace(
                    "leaf_",
                    ""
                )
            )

            mask_path = (
                mask_map.get(
                    leaf_id
                )
            )

            self.add_leaf_result(
                leaf_id,
                leaf_path,
                mask_path
            )

    def show_image(
        self,
        label,
        image_path,
        width,
        height
    ):

        pixmap = QPixmap(
            str(image_path)
        )

        if pixmap.isNull():

            label.setText(
                (
                    "Could not load image:\n"
                    f"{image_path}"
                )
            )

            return

        scaled = pixmap.scaled(
            width,
            height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        label.setPixmap(
            scaled
        )

    def add_leaf_result(
        self,
        leaf_id,
        leaf_path,
        mask_path
    ):

        frame = QFrame()

        frame.setFrameShape(
            QFrame.Shape.Box
        )

        frame_layout = QVBoxLayout(
            frame
        )

        title = QLabel(
            f"LEAF {leaf_id}"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            "font-size: 17px; "
            "font-weight: bold;"
        )

        frame_layout.addWidget(
            title
        )

        images_layout = QHBoxLayout()

        # ==================================================
        # LEAF
        # ==================================================

        leaf_layout = QVBoxLayout()

        leaf_title = QLabel(
            "LEAF IMAGE"
        )

        leaf_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        leaf_label = QLabel()

        leaf_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        leaf_label.setMinimumSize(
            300,
            220
        )

        self.show_image(
            leaf_label,
            leaf_path,
            300,
            220
        )

        leaf_layout.addWidget(
            leaf_title
        )

        leaf_layout.addWidget(
            leaf_label
        )

        # ==================================================
        # MASK
        # ==================================================

        mask_layout = QVBoxLayout()

        mask_title = QLabel(
            "MASK"
        )

        mask_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        mask_label = QLabel()

        mask_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        mask_label.setMinimumSize(
            300,
            220
        )

        if mask_path is not None:

            self.show_image(
                mask_label,
                mask_path,
                300,
                220
            )

        else:

            mask_label.setText(
                "Mask not found."
            )

        mask_layout.addWidget(
            mask_title
        )

        mask_layout.addWidget(
            mask_label
        )

        images_layout.addLayout(
            leaf_layout
        )

        images_layout.addLayout(
            mask_layout
        )

        frame_layout.addLayout(
            images_layout
        )

        info = QLabel(
            (
                f"Leaf: {leaf_path.name}\n"
                f"Mask: "
                f"{mask_path.name}"
                if mask_path is not None
                else
                f"Leaf: {leaf_path.name}\n"
                "Mask: not found"
            )
        )

        info.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        frame_layout.addWidget(
            info
        )

        self.results_layout.addWidget(
            frame
        )

    def add_message(
        self,
        message
    ):

        label = QLabel(
            message
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.results_layout.addWidget(
            label
        )