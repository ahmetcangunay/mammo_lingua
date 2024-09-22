import sys
import os
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QFileDialog, QLabel,
                             QSplitter, QFrame, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from spacy import displacy

from src.models.ner_model import NerModel
from src.models.birads_classifier import BiradsClassifier

birads_model_path = "data/nlp_models/classification_model/model-last"
ner_model_path = "data/nlp_models/ner_model/model-last"


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super(CustomTitleBar, self).__init__(parent)
        self.parent = parent
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık etiketi
        title = QLabel("NER ve BIRADS Sınıflandırma")
        title.setStyleSheet(
            "color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Araya stretch ekliyoruz
        layout.addStretch(1)

        # Minimize ve Maximize Butonları
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
        # Başlığın tüm genişliği kaplaması için gerekli
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

    def __init__(self, parent):
        super(CustomTitleBar, self).__init__(parent)
        self.parent = parent
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("NER ve BIRADS Sınıflandırma")
        title.setStyleSheet(
            "color: white; font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        layout.addStretch(10)

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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NER ve BIRADS Sınıflandırma")
        self.setGeometry(100, 100, 1200, 800)

        # Pencerenin çerçevesiz ve yeniden boyutlandırılabilir olmasını sağla
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

        # Yükleme etiketi
        self.loading_label = QLabel("Modeller yükleniyor...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 24px; color: white;")
        content_layout.addWidget(self.loading_label)

        # Yükleme işlemini başlat
        QTimer.singleShot(100, self.start_loading)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

        self.file_content = None
        self.file_name = None

        self.apply_dark_mode()

        # Uygulamayı fullscreen başlat
        self.showFullScreen()

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
        """)

    def start_loading(self):
        # Modelleri yükle
        self.load_models()

        # GUI bileşenlerini oluştur
        self.init_ui()

        # Yükleme etiketini kaldır
        self.loading_label.hide()

    def load_models(self):
        # NER modelini yükle
        self.loading_label.setText("NER modeli yükleniyor...")
        self.repaint()  # Ekranı yenile
        self.ner_model = NerModel(ner_model_path)

        # BIRADS modelini yükle
        self.loading_label.setText("BIRADS modeli yükleniyor...")
        self.repaint()  # Ekranı yenile
        self.birads_model = BiradsClassifier(birads_model_path)

    def init_ui(self):
        main_layout = QHBoxLayout()

        # Sol taraf
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.file_button = QPushButton("Dosya Yükle")
        self.file_button.clicked.connect(self.load_file)
        self.text_edit = QTextEdit()
        self.show_results_button = QPushButton("Sonuçları Göster")
        self.show_results_button.clicked.connect(self.show_results)
        self.show_results_button.setEnabled(False)  # Başlangıçta devre dışı
        left_layout.addWidget(self.file_button)
        left_layout.addWidget(self.text_edit)
        left_layout.addWidget(self.show_results_button)

        # Sağ taraf
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # WebView için yeni bir widget oluştur
        web_view_widget = QWidget()
        web_view_layout = QVBoxLayout(web_view_widget)
        self.web_view = QWebEngineView()
        web_view_layout.addWidget(QLabel("NER Sonuçları:"))
        web_view_layout.addWidget(self.web_view)

        # Diğer metin kutuları için yeni bir widget oluştur
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
            widget.setFixedHeight(60)  # Metin kutularının yüksekliğini sınırla
            temp_layout.addWidget(widget)
            text_boxes_layout.addLayout(temp_layout)

        # Sağ tarafı dikey olarak böl
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(web_view_widget)
        right_splitter.addWidget(text_boxes_widget)
        right_splitter.setSizes([600, 200])  # WebView'a daha fazla alan ver

        right_layout.addWidget(right_splitter)

        # Ana pencereyi yatay olarak böl
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([400, 800])  # Sağ tarafa daha fazla alan ver

        main_layout.addWidget(main_splitter)

        # Ana layout'u mevcut content_layout'a ekle
        self.layout().itemAt(1).widget().layout().addLayout(main_layout)

    def load_file(self):
        self.file_name, _ = QFileDialog.getOpenFileName(
            self, "Dosya Seç", "", "Text Files (*.txt)")
        if self.file_name:
            with open(self.file_name, 'r', encoding='utf-8') as file:
                self.file_content = file.read().replace(r'\n', ' ')
                self.text_edit.setText(self.file_content)

            # Dosya yüklendiğinde butonu etkinleştir
            self.show_results_button.setEnabled(True)

    def show_results(self):
        if self.file_content and self.file_name:
            # Dosya adından patient_id'yi çıkarın ve ayarlayın
            patient_id = os.path.basename(self.file_name).split('.')[0]
            self.patient_id.setText(patient_id)

            # NER ve BIRADS modellerini çağırın ve sonuçları işleyin
            self.process_ner_results(self.file_content)
            self.process_birads_results(self.file_content)
        else:
            print("Lütfen önce bir dosya yükleyin.")

    def process_ner_results(self, text):
        # NER modelini çağırın ve sonuçları işleyin
        doc, options = self.ner_model.get_entities(text)

        # NER sonuçlarını HTML olarak biçimlendirin
        html = displacy.render(doc, style="ent", options=options)

        # Dark mode için HTML'i özelleştir
        dark_html = html.replace("background: #ddd", "background: #2C2C2C")
        dark_html = dark_html.replace("color: #000", "color: #FFF")

        # HTML'i WebView'da gösterin
        self.web_view.setHtml(dark_html)
        print("WebView updated with NER results")  # Debug mesajı

        # Diğer metin kutularını güncelleyin
        self.update_text_boxes(doc.ents)

    def process_birads_results(self, text):
        # BIRADS modelini çağırın ve sonucu işleyin
        birads_result = self.birads_model.get_classification(text)
        self.predicted_birads.setText(str(birads_result))

    def update_text_boxes(self, ner_results):
        # NER sonuçlarına göre metin kutularını güncelleyin
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
