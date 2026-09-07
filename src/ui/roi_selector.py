import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QRubberBand,
)


class ROIImageLabel(QLabel):

    roi_selected = Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.setMouseTracking(True)

        self.setCursor(
            Qt.CursorShape.CrossCursor
        )

        self.rubber_band = QRubberBand(
            QRubberBand.Shape.Rectangle,
            self
        )

        self.selection_start = None
        self.selection_end = None

        self.original_width = 0
        self.original_height = 0

        self.displayed_pixmap_rect = QRect()

        self.selected_roi = None

    def set_image(self, pixmap):

        if pixmap.isNull():
            return

        self.original_width = pixmap.width()
        self.original_height = pixmap.height()

        self.setPixmap(pixmap)

        self.update_display_rect()

    def update_display_rect(self):

        pixmap = self.pixmap()

        if pixmap is None:
            self.displayed_pixmap_rect = QRect()
            return

        if pixmap.isNull():
            self.displayed_pixmap_rect = QRect()
            return

        x = (
            self.width()
            - pixmap.width()
        ) // 2

        y = (
            self.height()
            - pixmap.height()
        ) // 2

        self.displayed_pixmap_rect = QRect(
            x,
            y,
            pixmap.width(),
            pixmap.height()
        )

        self.update()

    def clear_selection(self):

        self.selection_start = None
        self.selection_end = None
        self.selected_roi = None

        self.rubber_band.hide()

        self.update()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.update_display_rect()

    def mousePressEvent(self, event):

        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            return

        if self.displayed_pixmap_rect.isNull():
            return

        point = event.position().toPoint()

        if not self.displayed_pixmap_rect.contains(
            point
        ):
            return

        self.selection_start = point
        self.selection_end = point

        self.rubber_band.setGeometry(
            QRect(
                point,
                point
            )
        )

        self.rubber_band.show()

    def mouseMoveEvent(self, event):

        if self.selection_start is None:
            return

        if self.displayed_pixmap_rect.isNull():
            return

        point = event.position().toPoint()

        point.setX(
            max(
                self.displayed_pixmap_rect.left(),
                min(
                    point.x(),
                    self.displayed_pixmap_rect.right()
                )
            )
        )

        point.setY(
            max(
                self.displayed_pixmap_rect.top(),
                min(
                    point.y(),
                    self.displayed_pixmap_rect.bottom()
                )
            )
        )

        self.selection_end = point

        rectangle = QRect(
            self.selection_start,
            self.selection_end
        ).normalized()

        self.rubber_band.setGeometry(
            rectangle
        )

    def mouseReleaseEvent(self, event):

        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            return

        if self.selection_start is None:
            return

        point = event.position().toPoint()

        point.setX(
            max(
                self.displayed_pixmap_rect.left(),
                min(
                    point.x(),
                    self.displayed_pixmap_rect.right()
                )
            )
        )

        point.setY(
            max(
                self.displayed_pixmap_rect.top(),
                min(
                    point.y(),
                    self.displayed_pixmap_rect.bottom()
                )
            )
        )

        self.selection_end = point

        display_rect = QRect(
            self.selection_start,
            self.selection_end
        ).normalized()

        self.selection_start = None
        self.selection_end = None

        if (
            display_rect.width() < 5
            or display_rect.height() < 5
        ):
            self.rubber_band.hide()
            return

        roi = self.display_to_original(
            display_rect
        )

        if roi is None:
            return

        self.selected_roi = roi

        self.rubber_band.setGeometry(
            display_rect
        )

        self.roi_selected.emit(
            roi
        )

    def display_to_original(self, display_rect):

        if self.displayed_pixmap_rect.isNull():
            return None

        if (
            self.original_width <= 0
            or self.original_height <= 0
        ):
            return None

        display_width = (
            self.displayed_pixmap_rect.width()
        )

        display_height = (
            self.displayed_pixmap_rect.height()
        )

        scale_x = (
            self.original_width
            / display_width
        )

        scale_y = (
            self.original_height
            / display_height
        )

        relative_x = (
            display_rect.left()
            - self.displayed_pixmap_rect.left()
        )

        relative_y = (
            display_rect.top()
            - self.displayed_pixmap_rect.top()
        )

        x1 = int(
            relative_x * scale_x
        )

        y1 = int(
            relative_y * scale_y
        )

        x2 = int(
            (
                relative_x
                + display_rect.width()
                - 1
            )
            * scale_x
        )

        y2 = int(
            (
                relative_y
                + display_rect.height()
                - 1
            )
            * scale_y
        )

        x1 = max(
            0,
            min(
                x1,
                self.original_width - 1
            )
        )

        y1 = max(
            0,
            min(
                y1,
                self.original_height - 1
            )
        )

        x2 = max(
            x1,
            min(
                x2,
                self.original_width - 1
            )
        )

        y2 = max(
            y1,
            min(
                y2,
                self.original_height - 1
            )
        )

        return (
            x1,
            y1,
            x2,
            y2
        )

    def paintEvent(self, event):

        super().paintEvent(event)

        if self.selected_roi is None:
            return

        if self.displayed_pixmap_rect.isNull():
            return

        if (
            self.original_width <= 0
            or self.original_height <= 0
        ):
            return

        x1, y1, x2, y2 = (
            self.selected_roi
        )

        scale_x = (
            self.displayed_pixmap_rect.width()
            / self.original_width
        )

        scale_y = (
            self.displayed_pixmap_rect.height()
            / self.original_height
        )

        display_x = (
            self.displayed_pixmap_rect.left()
            + int(x1 * scale_x)
        )

        display_y = (
            self.displayed_pixmap_rect.top()
            + int(y1 * scale_y)
        )

        display_width = max(
            1,
            int(
                (x2 - x1 + 1)
                * scale_x
            )
        )

        display_height = max(
            1,
            int(
                (y2 - y1 + 1)
                * scale_y
            )
        )

        painter = QPainter(self)

        pen = QPen(
            Qt.GlobalColor.green
        )

        pen.setWidth(3)

        painter.setPen(pen)

        painter.drawRect(
            QRect(
                display_x,
                display_y,
                display_width,
                display_height
            )
        )

        painter.end()


class ROISelector(QDialog):

    confirmed = Signal(tuple)
    cancelled = Signal()

    def __init__(
        self,
        image_path,
        parent=None
    ):
        super().__init__(parent)

        self.image_path = Path(
            image_path
        )

        self.selected_roi = None

        self.setWindowTitle(
            "PAPRIKA - PARTIAL REGION"
        )

        self.resize(
            1100,
            800
        )

        self.setModal(True)

        self.create_ui()

        self.load_image()

    def create_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel(
            "SELECT REGION FOR LEAF SEGMENTATION"
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        layout.addWidget(title)

        instruction = QLabel(
            "Drag a rectangle around the area "
            "you want to analyze."
        )

        layout.addWidget(instruction)

        self.image_label = ROIImageLabel()

        self.image_label.setStyleSheet(
            "border: 1px solid gray;"
        )

        layout.addWidget(
            self.image_label
        )

        self.coordinates_label = QLabel(
            "REGION: NOT SELECTED"
        )

        self.coordinates_label.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            self.coordinates_label
        )

        button_layout = QHBoxLayout()

        self.reset_button = QPushButton(
            "RESET"
        )

        self.cancel_button = QPushButton(
            "CANCEL"
        )

        self.confirm_button = QPushButton(
            "CONFIRM REGION"
        )

        self.confirm_button.setEnabled(
            False
        )

        button_layout.addWidget(
            self.reset_button
        )

        button_layout.addStretch()

        button_layout.addWidget(
            self.cancel_button
        )

        button_layout.addWidget(
            self.confirm_button
        )

        layout.addLayout(
            button_layout
        )

        self.image_label.roi_selected.connect(
            self.on_roi_selected
        )

        self.reset_button.clicked.connect(
            self.reset_selection
        )

        self.cancel_button.clicked.connect(
            self.cancel_selection
        )

        self.confirm_button.clicked.connect(
            self.confirm_selection
        )

    def load_image(self):

        if not self.image_path.exists():

            QMessageBox.critical(
                self,
                "PARTIAL REGION",
                (
                    "Image not found:\n"
                    f"{self.image_path}"
                )
            )

            self.reject()

            return

        pixmap = QPixmap(
            str(self.image_path)
        )

        if pixmap.isNull():

            QMessageBox.critical(
                self,
                "PARTIAL REGION",
                (
                    "Could not load image:\n"
                    f"{self.image_path}"
                )
            )

            self.reject()

            return

        scaled = pixmap.scaled(
            1040,
            620,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.set_image(
            scaled
        )

    def on_roi_selected(
        self,
        roi
    ):

        self.selected_roi = roi

        x1, y1, x2, y2 = roi

        width = (
            x2 - x1 + 1
        )

        height = (
            y2 - y1 + 1
        )

        self.coordinates_label.setText(
            (
                "REGION: "
                f"X1={x1}  "
                f"Y1={y1}  "
                f"X2={x2}  "
                f"Y2={y2}  "
                f"| SIZE={width}x{height}"
            )
        )

        self.confirm_button.setEnabled(
            True
        )

    def reset_selection(self):

        self.selected_roi = None

        self.image_label.clear_selection()

        self.coordinates_label.setText(
            "REGION: NOT SELECTED"
        )

        self.confirm_button.setEnabled(
            False
        )

    def confirm_selection(self):

        if self.selected_roi is None:

            QMessageBox.warning(
                self,
                "PARTIAL REGION",
                "Please select a region first."
            )

            return

        self.confirmed.emit(
            self.selected_roi
        )

        self.accept()

    def cancel_selection(self):

        self.cancelled.emit()

        self.reject()


def main():

    app = QApplication(
        sys.argv
    )

    image_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else r"C:\paprika\images\leafs.jpg"
    )

    dialog = ROISelector(
        image_path
    )

    result = dialog.exec()

    if result == QDialog.DialogCode.Accepted:

        print(
            f"CONFIRMED ROI: "
            f"{dialog.selected_roi}",
            flush=True
        )

    else:

        print(
            "ROI selection cancelled.",
            flush=True
        )


if __name__ == "__main__":
    main()