from datetime import datetime
from pathlib import Path
import sqlite3
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QScrollArea,
    QFrame,
)


DATABASE_PATH = Path(
    r"C:\paprika\data\paprika.db"
)


class LeafSearch(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "PAPRIKA - SEARCH LEAF"
        )

        self.resize(
            1250,
            760
        )

        self.rows = []

        self.create_ui()
        self.load_leaves()

    def create_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "SEARCH LEAF"
        )

        title.setStyleSheet(
            "font-size: 26px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        filters_frame = QFrame()

        filters_frame.setFrameShape(
            QFrame.Shape.Box
        )

        filters_layout = QGridLayout(
            filters_frame
        )

        file_label = QLabel(
            "FILE NAME:"
        )

        self.file_edit = QLineEdit()

        self.file_edit.setPlaceholderText(
            "Enter image filename"
        )

        from_label = QLabel(
            "FROM DATE:"
        )

        self.from_date = QDateEdit()

        self.from_date.setCalendarPopup(
            True
        )

        self.from_date.setDate(
            self.from_date.minimumDate()
        )

        to_label = QLabel(
            "TO DATE:"
        )

        self.to_date = QDateEdit()

        self.to_date.setCalendarPopup(
            True
        )

        self.to_date.setDate(
            self.to_date.maximumDate()
        )

        leaf_label = QLabel(
            "LEAF NUMBER:"
        )

        self.leaf_number_edit = QLineEdit()

        self.leaf_number_edit.setPlaceholderText(
            "Optional"
        )

        sort_label = QLabel(
            "SORT BY:"
        )

        self.sort_combo = QComboBox()

        self.sort_combo.addItems(
            [
                "DATE / TIME",
                "FILE NAME",
                "LEAF NUMBER",
                "LEAF ID",
            ]
        )

        self.order_combo = QComboBox()

        self.order_combo.addItems(
            [
                "NEWEST FIRST",
                "OLDEST FIRST",
                "A-Z",
                "Z-A",
            ]
        )

        self.search_button = QPushButton(
            "SEARCH"
        )

        self.clear_button = QPushButton(
            "CLEAR"
        )

        filters_layout.addWidget(
            file_label,
            0,
            0
        )

        filters_layout.addWidget(
            self.file_edit,
            0,
            1
        )

        filters_layout.addWidget(
            from_label,
            0,
            2
        )

        filters_layout.addWidget(
            self.from_date,
            0,
            3
        )

        filters_layout.addWidget(
            to_label,
            0,
            4
        )

        filters_layout.addWidget(
            self.to_date,
            0,
            5
        )

        filters_layout.addWidget(
            leaf_label,
            1,
            0
        )

        filters_layout.addWidget(
            self.leaf_number_edit,
            1,
            1
        )

        filters_layout.addWidget(
            sort_label,
            1,
            2
        )

        filters_layout.addWidget(
            self.sort_combo,
            1,
            3
        )

        filters_layout.addWidget(
            self.order_combo,
            1,
            4
        )

        filters_layout.addWidget(
            self.search_button,
            1,
            5
        )

        filters_layout.addWidget(
            self.clear_button,
            1,
            6
        )

        main_layout.addWidget(
            filters_frame
        )

        self.table = QTableWidget()

        self.table.setColumnCount(
            10
        )

        self.table.setHorizontalHeaderLabels(
            [
                "DATE",
                "TIME",
                "FILE",
                "LEAF",
                "LEAF ID",
                "RUN ID",
                "MEDIA ID",
                "X1,Y1",
                "X2,Y2",
                "SIZE",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(
            True
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        main_layout.addWidget(
            self.table
        )

        bottom_layout = QHBoxLayout()

        self.count_label = QLabel(
            "FOUND: 0"
        )

        bottom_layout.addWidget(
            self.count_label
        )

        bottom_layout.addStretch()

        self.open_button = QPushButton(
            "OPEN SELECTED LEAF"
        )

        self.open_button.setEnabled(
            False
        )

        bottom_layout.addWidget(
            self.open_button
        )

        refresh_button = QPushButton(
            "REFRESH"
        )

        bottom_layout.addWidget(
            refresh_button
        )

        main_layout.addLayout(
            bottom_layout
        )

        self.search_button.clicked.connect(
            self.load_leaves
        )

        self.clear_button.clicked.connect(
            self.clear_filters
        )

        self.open_button.clicked.connect(
            self.open_selected_leaf
        )

        refresh_button.clicked.connect(
            self.load_leaves
        )

        self.table.itemSelectionChanged.connect(
            self.on_selection_changed
        )

        self.table.itemDoubleClicked.connect(
            self.open_selected_leaf
        )

    def connect(self):

        if not DATABASE_PATH.exists():
            raise FileNotFoundError(
                "PAPRIKA database not found:\n"
                f"{DATABASE_PATH}"
            )

        connection = sqlite3.connect(
            str(DATABASE_PATH)
        )

        connection.row_factory = sqlite3.Row
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def load_leaves(self):

        try:

            self.table.setRowCount(
                0
            )

            file_name = (
                self.file_edit.text().strip()
            )

            leaf_number_text = (
                self.leaf_number_edit.text().strip()
            )

            from_date = (
                self.from_date.date().toString(
                    "yyyy-MM-dd"
                )
            )

            to_date = (
                self.to_date.date().toString(
                    "yyyy-MM-dd"
                )
            )

            conditions = []
            parameters = []

            conditions.append(
                "COALESCE(m.capture_date, r.segmentation_date) >= ?"
            )

            parameters.append(
                from_date
            )

            conditions.append(
                "COALESCE(m.capture_date, r.segmentation_date) <= ?"
            )

            parameters.append(
                to_date
            )

            if file_name:

                conditions.append(
                    "m.file_name LIKE ?"
                )

                parameters.append(
                    f"%{file_name}%"
                )

            if leaf_number_text:

                try:

                    leaf_number = int(
                        leaf_number_text
                    )

                except ValueError:

                    raise ValueError(
                        "LEAF NUMBER must be an integer."
                    )

                conditions.append(
                    "l.leaf_number = ?"
                )

                parameters.append(
                    leaf_number
                )

            sort_choice = (
                self.sort_combo.currentText()
            )

            order_choice = (
                self.order_combo.currentText()
            )

            if sort_choice == "FILE NAME":

                order_column = "m.file_name"

                direction = (
                    "ASC"
                    if order_choice == "A-Z"
                    else "DESC"
                )

            elif sort_choice == "LEAF NUMBER":

                order_column = "l.leaf_number"

                direction = (
                    "DESC"
                    if order_choice == "NEWEST FIRST"
                    else "ASC"
                )

            elif sort_choice == "LEAF ID":

                order_column = "l.id"

                direction = (
                    "DESC"
                    if order_choice == "NEWEST FIRST"
                    else "ASC"
                )

            else:

                order_column = (
                    "COALESCE(m.capture_date, r.segmentation_date) || ' ' || "
                    "COALESCE(m.capture_time, r.segmentation_time)"
                )

                direction = (
                    "ASC"
                    if order_choice == "OLDEST FIRST"
                    else "DESC"
                )

            sql = (
                "SELECT "
                "l.id AS leaf_id, "
                "l.leaf_number, "
                "l.x1, l.y1, l.x2, l.y2, "
                "l.width, l.height, l.area, "
                "l.original_path, "
                "l.highlighted_path, "
                "l.segmented_path, "
                "l.crop_path, "
                "l.overlay_path, "
                "l.mask_path, "
                "r.id AS run_id, "
                "r.run_name, "
                "r.segmentation_date, "
                "r.segmentation_time, "
                "m.id AS media_id, "
                "m.file_name, "
                "m.file_path, "
                "m.capture_date, "
                "m.capture_time "
                "FROM leaf_objects l "
                "INNER JOIN segmentation_runs r "
                "ON r.id = l.run_id "
                "INNER JOIN media_objects m "
                "ON m.id = r.media_id "
                "WHERE "
                + " AND ".join(conditions)
                + f" ORDER BY {order_column} {direction}, l.id DESC"
            )

            with self.connect() as connection:

                rows = connection.execute(
                    sql,
                    parameters
                ).fetchall()

            self.rows = [
                dict(row)
                for row in rows
            ]

            for row_data in self.rows:

                row_index = (
                    self.table.rowCount()
                )

                self.table.insertRow(
                    row_index
                )

                date_value = (
                    row_data.get("capture_date")
                    or row_data.get("segmentation_date")
                    or ""
                )

                time_value = (
                    row_data.get("capture_time")
                    or row_data.get("segmentation_time")
                    or ""
                )

                values = [
                    date_value,
                    time_value,
                    row_data.get(
                        "file_name",
                        ""
                    ),
                    f"Leaf {row_data['leaf_number']}",
                    str(row_data["leaf_id"]),
                    str(row_data["run_id"]),
                    str(row_data["media_id"]),
                    f"{row_data['x1']},{row_data['y1']}",
                    f"{row_data['x2']},{row_data['y2']}",
                    f"{row_data['width']} x {row_data['height']}",
                ]

                for column_index, value in enumerate(values):

                    item = QTableWidgetItem(
                        str(value)
                    )

                    item.setData(
                        Qt.ItemDataRole.UserRole,
                        row_data["leaf_id"]
                    )

                    self.table.setItem(
                        row_index,
                        column_index,
                        item
                    )

            self.count_label.setText(
                f"FOUND: {len(self.rows)}"
            )

            self.open_button.setEnabled(
                False
            )

        except Exception as exc:

            self.count_label.setText(
                "FOUND: 0"
            )

            QMessageBox.critical(
                self,
                "SEARCH LEAF ERROR",
                str(exc)
            )

    def clear_filters(self):

        self.file_edit.clear()
        self.leaf_number_edit.clear()

        self.load_leaves()

    def on_selection_changed(self):

        self.open_button.setEnabled(
            self.table.currentRow() >= 0
        )

    def get_selected_row(self):

        row_index = (
            self.table.currentRow()
        )

        if row_index < 0:

            return None

        if row_index >= len(self.rows):

            return None

        return self.rows[row_index]

    def open_selected_leaf(
        self,
        item=None
    ):

        row_data = self.get_selected_row()

        if row_data is None:

            return

        dialog = LeafViewer(
            row_data,
            self
        )

        dialog.exec()


class LeafViewer(QDialog):

    def __init__(
        self,
        row_data,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.row_data = row_data

        self.setWindowTitle(
            (
                "PAPRIKA - LEAF "
                f"{row_data['leaf_id']}"
            )
        )

        self.resize(
            1200,
            850
        )

        self.create_ui()

    def create_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            (
                f"LEAF {self.row_data['leaf_number']}"
                f"   |   LEAF ID {self.row_data['leaf_id']}"
            )
        )

        title.setStyleSheet(
            "font-size: 24px; "
            "font-weight: bold;"
        )

        main_layout.addWidget(
            title
        )

        details = QLabel(
            (
                f"FILE: {self.row_data['file_name']}\n"
                f"DATE: {self.row_data.get('capture_date') or self.row_data.get('segmentation_date') or ''}"
                f"   TIME: {self.row_data.get('capture_time') or self.row_data.get('segmentation_time') or ''}\n"
                f"RUN ID: {self.row_data['run_id']}"
                f"   MEDIA ID: {self.row_data['media_id']}\n"
                f"BBOX: ({self.row_data['x1']},{self.row_data['y1']}) - "
                f"({self.row_data['x2']},{self.row_data['y2']})"
                f"   SIZE: {self.row_data['width']} x {self.row_data['height']}\n"
                f"AREA: {self.row_data['area']}"
            )
        )

        main_layout.addWidget(
            details
        )

        scroll_area = QScrollArea()

        scroll_area.setWidgetResizable(
            True
        )

        container = QWidget()

        layout = QVBoxLayout(
            container
        )

        images = [
            (
                "ORIGINAL IMAGE",
                self.row_data.get("file_path")
            ),
            (
                "HIGHLIGHTED ORIGINAL",
                self.row_data.get("highlighted_path")
            ),
            (
                "SEGMENTED LEAF",
                self.row_data.get("segmented_path")
            ),
            (
                "LEAF CROP",
                self.row_data.get("crop_path")
            ),
            (
                "LEAF OVERLAY",
                self.row_data.get("overlay_path")
            ),
            (
                "MASK",
                self.row_data.get("mask_path")
            ),
        ]

        for title_text, path_value in images:

            self.add_image_block(
                layout,
                title_text,
                path_value
            )

        scroll_area.setWidget(
            container
        )

        main_layout.addWidget(
            scroll_area
        )

        close_button = QPushButton(
            "CLOSE"
        )

        close_button.clicked.connect(
            self.accept
        )

        main_layout.addWidget(
            close_button
        )

    def add_image_block(
        self,
        layout,
        title_text,
        path_value
    ):

        frame = QFrame()

        frame.setFrameShape(
            QFrame.Shape.Box
        )

        frame_layout = QVBoxLayout(
            frame
        )

        title = QLabel(
            title_text
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            "font-size: 18px; "
            "font-weight: bold;"
        )

        frame_layout.addWidget(
            title
        )

        if not path_value:

            missing = QLabel(
                "FILE NOT REGISTERED"
            )

            missing.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            frame_layout.addWidget(
                missing
            )

            layout.addWidget(
                frame
            )

            return

        image_path = Path(
            path_value
        )

        if not image_path.exists():

            missing = QLabel(
                (
                    "FILE NOT FOUND:\n"
                    f"{image_path}"
                )
            )

            missing.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            frame_layout.addWidget(
                missing
            )

            layout.addWidget(
                frame
            )

            return

        pixmap = QPixmap(
            str(image_path)
        )

        if pixmap.isNull():

            missing = QLabel(
                "COULD NOT LOAD IMAGE"
            )

            missing.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            frame_layout.addWidget(
                missing
            )

            layout.addWidget(
                frame
            )

            return

        info = QLabel(
            (
                f"FILE: {image_path.name}"
                f"   |   "
                f"SIZE: {pixmap.width()} x {pixmap.height()}"
                f"   |   "
                f"CREATED: {self.creation_time(image_path)}"
            )
        )

        info.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        frame_layout.addWidget(
            info
        )

        label = QLabel()

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        label.setPixmap(
            pixmap
        )

        label.setMinimumHeight(
            min(
                pixmap.height(),
                700
            )
        )

        frame_layout.addWidget(
            label
        )

        layout.addWidget(
            frame
        )

    def creation_time(
        self,
        path
    ):

        try:

            return datetime.fromtimestamp(
                path.stat().st_ctime
            ).strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        except Exception:

            return "UNKNOWN"


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = LeafSearch()
    window.show()

    sys.exit(
        app.exec()
    )
