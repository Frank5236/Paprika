from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
)


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".heic",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".m4v",
}


class ImageInput(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "PAPRIKA - IMAGE INPUT"
        )

        self.resize(1100, 700)

        self.media_files = []

        self.create_ui()

    def create_ui(self):

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("IMAGE INPUT")

        title.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(title)

        media_group = QGroupBox(
            "MEDIA IMPORT"
        )

        media_layout = QHBoxLayout()
        media_group.setLayout(media_layout)

        import_files_button = QPushButton(
            "IMPORT MEDIA FILES"
        )

        import_folder_button = QPushButton(
            "IMPORT FOLDER"
        )

        clear_button = QPushButton(
            "CLEAR"
        )

        media_layout.addWidget(
            import_files_button
        )

        media_layout.addWidget(
            import_folder_button
        )

        media_layout.addWidget(
            clear_button
        )

        layout.addWidget(media_group)

        test_group = QGroupBox(
            "AI TEST MEDIA"
        )

        test_layout = QHBoxLayout()
        test_group.setLayout(test_layout)

        pexels_tracking = QPushButton(
            "PEXELS - TRACKING"
        )

        pexels_segmentation = QPushButton(
            "PEXELS - SEGMENTATION"
        )

        pexels_texture = QPushButton(
            "PEXELS - TEXTURE / CLASSIFICATION"
        )

        test_layout.addWidget(
            pexels_tracking
        )

        test_layout.addWidget(
            pexels_segmentation
        )

        test_layout.addWidget(
            pexels_texture
        )

        layout.addWidget(test_group)

        dataset_group = QGroupBox(
            "AI DATASETS"
        )

        dataset_layout = QHBoxLayout()
        dataset_group.setLayout(dataset_layout)

        roboflow_button = QPushButton(
            "ROBOFLOW UNIVERSE"
        )

        kaggle_button = QPushButton(
            "KAGGLE DATASETS"
        )

        dataset_layout.addWidget(
            roboflow_button
        )

        dataset_layout.addWidget(
            kaggle_button
        )

        layout.addWidget(dataset_group)

        self.info_label = QLabel(
            "No media files imported"
        )

        layout.addWidget(self.info_label)

        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(
            [
                "FILE NAME",
                "TYPE",
                "SIZE",
                "PATH",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        layout.addWidget(self.table)

        import_files_button.clicked.connect(
            self.import_files
        )

        import_folder_button.clicked.connect(
            self.import_folder
        )

        clear_button.clicked.connect(
            self.clear_files
        )

        pexels_tracking.clicked.connect(
            self.open_pexels_tracking
        )

        pexels_segmentation.clicked.connect(
            self.open_pexels_segmentation
        )

        pexels_texture.clicked.connect(
            self.open_pexels_texture
        )

        roboflow_button.clicked.connect(
            self.open_roboflow
        )

        kaggle_button.clicked.connect(
            self.open_kaggle
        )

    def get_media_type(self, file_path):

        extension = Path(
            file_path
        ).suffix.lower()

        if extension in IMAGE_EXTENSIONS:
            return "IMAGE"

        if extension in VIDEO_EXTENSIONS:
            return "VIDEO"

        return "UNSUPPORTED"

    def add_file(self, file_path):

        path = Path(file_path)

        if not path.is_file():
            return

        media_type = self.get_media_type(path)

        if media_type == "UNSUPPORTED":
            return

        absolute_path = str(
            path.resolve()
        )

        if absolute_path in self.media_files:
            return

        self.media_files.append(
            absolute_path
        )

    def import_files(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Media Files",
            "",
            (
                "Media Files "
                "(*.jpg *.jpeg *.png *.bmp *.tif *.tiff "
                "*.webp *.heic *.mp4 *.avi *.mov *.mkv "
                "*.wmv *.m4v)"
            )
        )

        if not files:
            return

        for file_path in files:
            self.add_file(file_path)

        self.refresh_table()

    def import_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Media Folder"
        )

        if not folder:
            return

        folder_path = Path(folder)

        for file_path in folder_path.iterdir():

            if file_path.is_file():
                self.add_file(file_path)

        self.refresh_table()

    def refresh_table(self):

        self.table.setRowCount(0)

        for file_path in self.media_files:

            path = Path(file_path)

            row = self.table.rowCount()

            self.table.insertRow(row)

            media_type = self.get_media_type(
                file_path
            )

            size_mb = (
                path.stat().st_size
                / (1024 * 1024)
            )

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    path.name
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    media_type
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    f"{size_mb:.2f} MB"
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(path.parent)
                )
            )

        self.info_label.setText(
            f"Imported media files: "
            f"{len(self.media_files)}"
        )

    def clear_files(self):

        self.media_files.clear()

        self.table.setRowCount(0)

        self.info_label.setText(
            "No media files imported"
        )

    def open_url(self, url):

        QDesktopServices.openUrl(
            QUrl(url)
        )

    def open_pexels_tracking(self):

        self.open_url(
            "https://www.pexels.com/search/videos/red%20pepper/"
        )

    def open_pexels_segmentation(self):

        self.open_url(
            "https://www.pexels.com/search/videos/"
            "red%20pepper%20cutting/"
        )

    def open_pexels_texture(self):

        self.open_url(
            "https://www.pexels.com/search/videos/"
            "red%20chili%20pepper/"
        )

    def open_roboflow(self):

        self.open_url(
            "https://universe.roboflow.com/"
        )

    def open_kaggle(self):

        self.open_url(
            "https://www.kaggle.com/datasets"
        )