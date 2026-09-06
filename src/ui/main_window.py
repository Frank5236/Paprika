import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

# ============================================================
# PAPRIKA - UI PATH
# ============================================================

UI_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

if str(UI_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(UI_DIR)
    )


# ============================================================
# PAPRIKA - UI MODULES
# ============================================================

from image_input import (
    ImageInput
)

from image_analysis import (
    ImageAnalysis
)

from segmentation_results import (
    SegmentationResults
)


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "PAPRIKA - Pepper Analysis System"
        )

        # Initial size only.
        # Window remains freely resizable.
        self.resize(
            800,
            650
        )

        # ----------------------------------------------------
        # CHILD WINDOWS
        # ----------------------------------------------------

        self.image_input_window = None

        self.image_analysis_window = None

        self.segmentation_results_window = None

        # ----------------------------------------------------
        # CENTRAL WIDGET
        # ----------------------------------------------------

        self.central_widget = QWidget()

        self.setCentralWidget(
            self.central_widget
        )

        layout = QVBoxLayout(
            self.central_widget
        )

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel(
            "PAPRIKA"
        )

        title.setStyleSheet(
            "font-size: 32px; "
            "font-weight: bold;"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            title
        )

        # ====================================================
        # SUBTITLE
        # ====================================================

        subtitle = QLabel(
            "Pepper Analysis System"
        )

        subtitle.setStyleSheet(
            "font-size: 18px;"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            25
        )

        # ====================================================
        # MAIN MENU
        # ====================================================

        image_input_button = QPushButton(
            "IMAGE INPUT"
        )

        image_analysis_button = QPushButton(
            "IMAGE ANALYSIS"
        )

        segmentation_results_button = QPushButton(
            "SHOW SEGMENTATION RESULTS"
        )

        reports_button = QPushButton(
            "REPORTS"
        )

        administration_button = QPushButton(
            "ADMINISTRATION"
        )

        buttons = [
            image_input_button,
            image_analysis_button,
            segmentation_results_button,
            reports_button,
            administration_button,
        ]

        for button in buttons:

            button.setMinimumHeight(
                55
            )

            button.setStyleSheet(
                "font-size: 17px;"
            )

            layout.addWidget(
                button
            )

        # ====================================================
        # SIGNALS
        # ====================================================

        image_input_button.clicked.connect(
            self.open_image_input
        )

        image_analysis_button.clicked.connect(
            self.open_image_analysis
        )

        segmentation_results_button.clicked.connect(
            self.open_segmentation_results
        )

        reports_button.clicked.connect(
            self.open_reports
        )

        administration_button.clicked.connect(
            self.open_administration
        )

    # ========================================================
    # IMAGE INPUT
    # ========================================================

    def open_image_input(self):

        try:

            print(
                "[MAIN WINDOW] Opening IMAGE INPUT...",
                flush=True
            )

            self.image_input_window = (
                ImageInput()
            )

            self.image_input_window.show()

            self.image_input_window.raise_()

            self.image_input_window.activateWindow()

        except Exception as exc:

            self.show_error(
                "IMAGE INPUT ERROR",
                exc
            )

    # ========================================================
    # IMAGE ANALYSIS
    # ========================================================

    def open_image_analysis(self):

        try:

            print(
                "[MAIN WINDOW] Opening IMAGE ANALYSIS...",
                flush=True
            )

            self.image_analysis_window = (
                ImageAnalysis()
            )

            self.image_analysis_window.show()

            self.image_analysis_window.raise_()

            self.image_analysis_window.activateWindow()

        except Exception as exc:

            self.show_error(
                "IMAGE ANALYSIS ERROR",
                exc
            )

    # ========================================================
    # SEGMENTATION RESULTS
    # ========================================================

    def open_segmentation_results(self):

        try:

            print(
                "[MAIN WINDOW] Opening "
                "SEGMENTATION RESULTS...",
                flush=True
            )

            self.segmentation_results_window = (
                SegmentationResults()
            )

            self.segmentation_results_window.show()

            self.segmentation_results_window.raise_()

            self.segmentation_results_window.activateWindow()

        except Exception as exc:

            self.show_error(
                "SEGMENTATION RESULTS ERROR",
                exc
            )

    # ========================================================
    # REPORTS
    # ========================================================

    def open_reports(self):

        QMessageBox.information(
            self,
            "REPORTS",
            "REPORTS module"
        )

    # ========================================================
    # ADMINISTRATION
    # ========================================================

    def open_administration(self):

        QMessageBox.information(
            self,
            "ADMINISTRATION",
            "ADMINISTRATION module"
        )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    def show_error(
        self,
        title,
        exc
    ):

        error_type = type(
            exc
        ).__name__

        error_message = str(
            exc
        )

        print(
            "",
            flush=True
        )

        print(
            "=" * 80,
            flush=True
        )

        print(
            title,
            flush=True
        )

        print(
            f"ERROR TYPE: {error_type}",
            flush=True
        )

        print(
            f"ERROR MESSAGE: {error_message}",
            flush=True
        )

        print(
            "=" * 80,
            flush=True
        )

        QMessageBox.critical(
            self,
            title,
            (
                f"ERROR TYPE:\n"
                f"{error_type}\n\n"
                f"ERROR MESSAGE:\n"
                f"{error_message}"
            )
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():

    print(
        "[PAPRIKA] Starting application...",
        flush=True
    )

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    print(
        "[PAPRIKA] Main window started.",
        flush=True
    )

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()