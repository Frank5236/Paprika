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

        self.setMouseTracking(
            True
        )

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

        self.original_pixmap = QPixmap()

        self.displayed_pixmap_rect = QRect()

        self.selected_roi = None

    def set_image(
        self,
        pixmap
    ):

        if pixmap.isNull():
            return

        self.original_width = pixmap.width()
        self.original_height = pixmap.height()

        self.original_pixmap = pixmap.copy()

        self.set_display_pixmap()

    def set_display_pixmap(
        self
    ):

        if self.original_pixmap.isNull():

            self.displayed_pixmap_rect = QRect()
            self.clear()
            return

        available_width = max(
            1,
            self.width() - 2
        )

        available_height = max(
            1,
            self.height() - 2
        )

        scaled = self.original_pixmap.scaled(
            available_width,
            available_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(
            scaled
        )

        x = (
            self.width()
            - scaled.width()
        ) // 2

        y = (
            self.height()
            - scaled.height()
        ) // 2

        self.displayed_pixmap_rect = QRect(
            x,
            y,
            scaled.width(),
            scaled.height()
        )

        self.update()

    def update_display_rect(
        self
    ):

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

    def clear_selection(
        self
    ):

        self.selection_start = None
        self.selection_end = None
        self.selected_roi = None

        self.rubber_band.hide()

        self.update()

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        if not self.original_pixmap.isNull():
            self.set_display_pixmap()
        else:
            self.update_display_rect()

        if self.selected_roi is not None:
            self.rubber_band.setGeometry(
                self.original_to_display_rect(
                    self.selected_roi
                )
            )
            self.rubber_band.show()

    def mousePressEvent(
        self,
        event
    ):

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

    def clamp_display_point(
        self,
        point
    ):

        if self.displayed_pixmap_rect.isNull():
            return point

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

        return point

    def mouseMoveEvent(
        self,
        event
    ):

        if self.selection_start is None:
            return

        if self.displayed_pixmap_rect.isNull():
            return

        point = event.position().toPoint()

        point = self.clamp_display_point(
            point
        )

        self.selection_end = point

        rectangle = QRect(
            self.selection_start,
            self.selection_end
        ).normalized()

        self.rubber_band.setGeometry(
            rectangle
        )

    def mouseReleaseEvent(
        self,
        event
    ):

        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):
            return

        if self.selection_start is None:
            return

        if self.displayed_pixmap_rect.isNull():
            return

        point = event.position().toPoint()

        point = self.clamp_display_point(
            point
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
            self.original_to_display_rect(
                roi
            )
        )

        self.rubber_band.show()

        self.roi_selected.emit(
            roi
        )

    def display_to_original(
        self,
        display_rect
    ):

        if self.displayed_pixmap_rect.isNull():
            return None

        if (
            self.original_width <= 0
            or self.original_height <= 0
        ):
            return None

        display_width = self.displayed_pixmap_rect.width()
        display_height = self.displayed_pixmap_rect.height()

        if display_width <= 0 or display_height <= 0:
            return None

        scale_x = (
            self.original_width
            / display_width
        )

        scale_y = (
            self.original_height
            / display_height
        )

        relative_left = (
            display_rect.left()
            - self.displayed_pixmap_rect.left()
        )

        relative_top = (
            display_rect.top()
            - self.displayed_pixmap_rect.top()
        )

        relative_right = (
            display_rect.right()
            - self.displayed_pixmap_rect.left()
        )

        relative_bottom = (
            display_rect.bottom()
            - self.displayed_pixmap_rect.top()
        )

        relative_left = max(
            0,
            min(
                relative_left,
                display_width - 1
            )
        )

        relative_top = max(
            0,
            min(
                relative_top,
                display_height - 1
            )
        )

        relative_right = max(
            0,
            min(
                relative_right,
                display_width - 1
            )
        )

        relative_bottom = max(
            0,
            min(
                relative_bottom,
                display_height - 1
            )
        )

        x1 = int(
            relative_left * scale_x
        )

        y1 = int(
            relative_top * scale_y
        )

        x2 = int(
            relative_right * scale_x
        )

        y2 = int(
            relative_bottom * scale_y
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

    def original_to_display_rect(
        self,
        roi
    ):

        if self.displayed_pixmap_rect.isNull():
            return QRect()

        if (
            self.original_width <= 0
            or self.original_height <= 0
        ):
            return QRect()

        x1, y1, x2, y2 = roi

        scale_x = (
            self.displayed_pixmap_rect.width()
            / self.original_width
        )

        scale_y = (
            self.displayed_pixmap_rect.height()
            / self.original_height
        )

        display_x1 = (
            self.displayed_pixmap_rect.left()
            + int(x1 * scale_x)
        )

        display_y1 = (
            self.displayed_pixmap_rect.top()
            + int(y1 * scale_y)
        )

        display_x2 = (
            self.displayed_pixmap_rect.left()
            + int(x2 * scale_x)
        )

        display_y2 = (
            self.displayed_pixmap_rect.top()
            + int(y2 * scale_y)
        )

        return QRect(
            display_x1,
            display_y1,
            max(
                1,
                display_x2 - display_x1 + 1
            ),
            max(
                1,
                display_y2 - display_y1 + 1
            )
        )

    def paintEvent(
        self,
        event
    ):

        super().paintEvent(
            event
        )

        if self.selected_roi is None:
            return

        if self.displayed_pixmap_rect.isNull():
            return

        rectangle = self.original_to_display_rect(
            self.selected_roi
        )

        painter = QPainter(
            self
        )

        pen = QPen(
            Qt.GlobalColor.green
        )

        pen.setWidth(
            3
        )

        painter.setPen(
            pen
        )

        painter.drawRect(
            rectangle
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

        super().__init__(
            parent
        )

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

        self.setModal(
            True
        )

        self.create_ui()
        self.load_image()

    def create_ui(
        self
    ):

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "SELECT REGION FOR LEAF SEGMENTATION"
        )

        title.setStyleSheet(
            "font-size: 22px; "
            "font-weight: bold;"
        )

        layout.addWidget(
            title
        )

        instruction = QLabel(
            "Drag a rectangle around the area "
            "you want to analyze."
        )

        layout.addWidget(
            instruction
        )

        self.image_label = ROIImageLabel()

        self.image_label.setMinimumSize(
            400,
            300
        )

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

    def load_image(
        self
    ):

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

        self.image_label.set_image(
            pixmap
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

    def reset_selection(
        self
    ):

        self.selected_roi = None

        self.image_label.clear_selection()

        self.coordinates_label.setText(
            "REGION: NOT SELECTED"
        )

        self.confirm_button.setEnabled(
            False
        )

    def confirm_selection(
        self
    ):

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

    def cancel_selection(
        self
    ):

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
