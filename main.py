#!.venv/bin/python3 main.py

# -*- coding: utf-8 -*-

"""
@Author: Ahmet Can GÜNAY
@Version: 1.0
@Description: A GUI application for Name Entity Recognition and BIRADS Classification
@Date: 2024-09-19
@License: MIT
"""

import sys
import os
import json
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPalette, QFont, QPainter, QLinearGradient
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QFileDialog, QLabel,
                             QSplitter, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QProgressBar,
                             QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from spacy import displacy

from src.models.ner_model import NerModel
from src.models.birads_classifier import BiradsClassifier

birads_model_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "data/nlp_models/classification_model")
ner_model_path = ner_model_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "data/nlp_models/ner_model")


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super(CustomTitleBar, self).__init__(parent)
        self.parent = parent
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(
            "Mammo Lingua | Name Entity Recognition and BIRADS Classification Program")
        title.setStyleSheet(
            "color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        layout.addStretch(1)

        self.minimize_button = QPushButton("−")
        self.minimize_button.clicked.connect(self.parent.showMinimized)

        self.maximize_button = QPushButton("⬜")
        self.maximized = False
        self.maximize_button.clicked.connect(self.toggle_maximize_restore)

        self.close_button = QPushButton("×")
        self.close_button.clicked.connect(self.parent.close)

        for button in [self.minimize_button, self.maximize_button, self.close_button]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    font-size: 16px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            layout.addWidget(button)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: #2C2C2C;")
        self.setFixedHeight(30)

    def toggle_maximize_restore(self):
        if self.maximized:
            self.parent.showNormal()
            self.maximize_button.setText("⬜")
        else:
            self.parent.showMaximized()
            self.maximize_button.setText("🗗")
        self.maximized = not self.maximized

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing and not self.maximized:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                    self.mapToGlobal(self.movement).y(),
                                    self.parent.width(),
                                    self.parent.height())
            self.start = self.end

    def mouseReleaseEvent(self, event):
        self.pressing = False


class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                background-color: #2C2C2C;
                border: 1px solid #555555;
                border-radius: 5px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                  stop:0 #4A4A4A, stop:1 #6A6A6A);
                border-radius: 5px;
            }
        """)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(1500)  # 1.5 saniye
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def start_animation(self):
        self.animation.start()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Mammo Lingua | Name Entity Recognition and BIRADS Classification Program")
        self.setGeometry(100, 100, 1200, 800)

        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowMinMaxButtonsHint)

        self.title_bar = CustomTitleBar(self)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Progress Bar and Loading Label
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        self.loading_label = QLabel("Models are loading...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet(
            "font-size: 18px; color: #CCCCCC; margin-bottom: 10px;")
        self.progress_bar = AnimatedProgressBar(self)
        loading_layout.addWidget(self.loading_label)
        loading_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.loading_widget)

        # Start Loading Process
        QTimer.singleShot(100, self.start_loading)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

        self.file_content = None
        self.file_name = None
        self.ner_results = None
        self.birads_result = None

        self.apply_dark_mode()

        self.showFullScreen()

    def start_loading(self):
        self.progress_bar.start_animation()
        self.load_models()

    def load_models(self):
        # Load NER Model
        self.loading_label.setText("NER model is loading...")
        self.repaint()
        self.ner_model = NerModel(ner_model_path)

        # Load BIRADS Model
        self.loading_label.setText("BIRADS model is loading...")
        self.repaint()
        self.birads_model = BiradsClassifier(birads_model_path)

        # When Loading is Finished
        QTimer.singleShot(500, self.finish_loading)

    def finish_loading(self):
        self.loading_widget.hide()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Left Side
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.file_button = QPushButton("Upload File")
        self.file_button.clicked.connect(self.load_file)
        self.text_edit = QTextEdit()
        self.show_results_button = QPushButton("Show Results")
        self.show_results_button.clicked.connect(self.show_results)
        self.show_results_button.setEnabled(False)  # Inactive at the beginning
        self.save_results_button = QPushButton("Save Results")
        self.save_results_button.clicked.connect(self.save_results)
        self.save_results_button.setEnabled(False)  # Inactive at the beginning
        left_layout.addWidget(self.file_button)
        left_layout.addWidget(self.text_edit)
        left_layout.addWidget(self.show_results_button)
        left_layout.addWidget(self.save_results_button)

        # Right Side
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Create a WebView widget for displaying NER results
        web_view_widget = QWidget()
        web_view_layout = QVBoxLayout(web_view_widget)
        self.web_view = QWebEngineView()
        web_view_layout.addWidget(QLabel("NER Results:"))
        web_view_layout.addWidget(self.web_view)

        # Create text boxes for displaying NER results
        text_boxes_widget = QWidget()
        text_boxes_layout = QVBoxLayout(text_boxes_widget)

        self.patient_id = QTextEdit()
        self.anatomy = QTextEdit()
        self.obs_present = QTextEdit()
        self.obs_absent = QTextEdit()
        self.obs_uncertain = QTextEdit()
        self.predicted_birads = QTextEdit()

        for widget, label in [
            (self.patient_id, "Patient ID"),
            (self.anatomy, "ANATOMY"),
            (self.obs_present, "OBSERVATION-PRESENT"),
            (self.obs_absent, "OBSERVATION-ABSENT"),
            (self.obs_uncertain, "OBS-UNCERTAIN"),
            (self.predicted_birads, "PREDICTED BIRADS")
        ]:
            temp_layout = QVBoxLayout()
            temp_layout.addWidget(QLabel(label))
            widget.setFixedHeight(60)  # Limit height of text boxes
            temp_layout.addWidget(widget)
            text_boxes_layout.addLayout(temp_layout)

        # Split the right side vertically
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(web_view_widget)
        right_splitter.addWidget(text_boxes_widget)
        right_splitter.setSizes([600, 200])  # Give more space to WebView

        right_layout.addWidget(right_splitter)

        # Split the main layout horizontally
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([400, 800])  # Give more space to the right side

        main_layout.addWidget(main_splitter)

        # Add the main layout to the content layout
        self.layout().itemAt(1).widget().layout().addLayout(main_layout)

    def load_file(self):
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Text Files (*.txt)")
        if self.file_name:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                self.file_content = file.read().replace(r'\n', ' ')
                self.text_edit.setText(self.file_content)

            # Activate the "Show Results" button when a file is loaded
            self.show_results_button.setEnabled(True)

    def show_results(self):
        if self.file_content and self.file_name:
            # Get the patient ID from the file name
            patient_id = os.path.basename(self.file_name).split('.')[0]
            self.patient_id.setText(patient_id)

            # Call NER and BIRADS models and process the results
            self.process_ner_results(self.file_content)
            self.process_birads_results(self.file_content)

            # When showing results, enable the "Save Results" button
            self.save_results_button.setEnabled(True)

    def process_ner_results(self, text):
        # Call the NER model and process the results
        doc, options = self.ner_model.get_entities(text)
        self.ner_results = doc

        # Format NER results as HTML
        html = displacy.render(doc, style="ent", options=options)

        # Specify the background and text color for dark mode
        dark_html = html.replace("background: #ddd", "background: #2C2C2C")
        dark_html = dark_html.replace("color: #000", "color: #FFF")

        # Show HTML in the WebView
        self.web_view.setHtml(dark_html)

        # Updates other text boxes based on NER results
        self.update_text_boxes(doc.ents)

    def process_birads_results(self, text):
        # Call the BIRADS model and get the classification
        self.birads_result = self.birads_model.get_classification(text)
        self.predicted_birads.setText(str(self.birads_result))

    def update_text_boxes(self, ner_results):
        # Update the text boxes based on NER results
        self.anatomy.clear()
        self.obs_present.clear()
        self.obs_absent.clear()
        self.obs_uncertain.clear()

        for entity in ner_results:
            if entity.label_ == "ANAT":
                self.anatomy.append(entity.text + " ")
            elif entity.label_ == "OBS-PRESENT":
                self.obs_present.append(entity.text + " ")
            elif entity.label_ == "OBS-ABSENT":
                self.obs_absent.append(entity.text + " ")
            elif entity.label_ == "OBS-UNCERTAIN":
                self.obs_uncertain.append(entity.text + " ")

    def save_results(self):
        if not self.file_name or not self.ner_results or self.birads_result is None:
            QMessageBox.warning(
                self, "Warning", "Please load a file and show the results first.")
            return

        # Format the results as a JSON object
        results = {
            "patient_id": self.patient_id.toPlainText(),
            "ner_results": {
                "anatomy": self.anatomy.toPlainText().split(" \n"),
                "observation_present": self.obs_present.toPlainText().split(" \n"),
                "observation_absent": self.obs_absent.toPlainText().split(" \n"),
                "observation_uncertain": self.obs_uncertain.toPlainText().split(" \n")
            },
            "birads_result": self.birads_result
        }

        # Select the save path
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "JSON Files (*.json)")

        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            QMessageBox.information(
                self, "Successfull", f"Successfully saved results at {save_path}")

    def apply_dark_mode(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QWidget {
                background-color: #353535;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit, QWebEngineView {
                background-color: #2C2C2C;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4A4A4A;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
            }
            QPushButton:pressed {
                background-color: #3A3A3A;
            }
            QSplitter::handle {
                background-color: #2C2C2C;
            }
            QLabel {
                color: #CCCCCC;
            }
            AnimatedProgressBar {
                background-color: #2C2C2C;
                border: 1px solid #555555;
                border-radius: 5px;
                height: 20px;
            }
            AnimatedProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                  stop:0 #4A4A4A, stop:1 #6A6A6A);
                border-radius: 5px;
            }
        """)


# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
