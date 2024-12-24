from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QSlider, QWidget
)
from PyQt5.QtCore import Qt


class FingerprintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fingerprint App")
        self.setGeometry(100, 100, 800, 600)

        # Table for showing results
        self.table = QTableWidget(10, 2)
        self.table.setHorizontalHeaderLabels(["Song", "Similarity"])

        # Slider for song combination
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)

        # Buttons
        self.search_button = QPushButton("Search for Similar Songs")
        self.combine_button = QPushButton("Combine Songs")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.slider)
        layout.addWidget(self.search_button)
        layout.addWidget(self.combine_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

app = QApplication([])
window = FingerprintApp()
window.show()
app.exec()
