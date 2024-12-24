import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QSlider, QWidget, QFileDialog
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class FingerprintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fingerprint App")
        self.setGeometry(100, 100, 800, 600)

        # Initialize components
        self.table = QTableWidget(10, 2)
        self.table.setHorizontalHeaderLabels(["Song", "Similarity"])

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)

        self.search_button = QPushButton("Search for Similar Songs")
        self.combine_button = QPushButton("Combine Songs")
        self.load_button = QPushButton("Load .npy File")

        # Create a Matplotlib canvas for plotting
        self.canvas = FigureCanvas(plt.figure(figsize=(5, 3)))

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.slider)
        layout.addWidget(self.search_button)
        layout.addWidget(self.combine_button)
        layout.addWidget(self.load_button)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect buttons to functions
        self.load_button.clicked.connect(self.load_npy_file)

    def load_npy_file(self):
        # Open file dialog to select the .npy file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open .npy File", "", "NumPy Files (*.npy)")

        if file_path:
            try:
                # Load the .npy file
                data = np.load(file_path)

                # Display the shape and type of the data in the table (as an example)
                self.table.setItem(0, 0, QTableWidgetItem(f"File: {file_path}"))
                self.table.setItem(0, 1, QTableWidgetItem(f"Shape: {str(data.shape)}"))

                # Visualize the data (Assuming it's a 1D or 2D array)
                self.plot_data(data)

            except Exception as e:
                print(f"Error loading .npy file: {e}")

    def plot_data(self, data):
        # Clear previous plot and plot the new data
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)

        if data.ndim == 1:
            ax.plot(data)  # Plot 1D data as a line plot
            ax.set_title("1D Data Plot")
            ax.set_xlabel("Index")
            ax.set_ylabel("Value")
        elif data.ndim == 2:
    # If data is 2D, we can use imshow to plot it as an image (e.g.,
    # spectrogram, image data, etc.)
            ax.imshow(data, aspect='auto', origin='lower')
            ax.set_title("2D Data Plot")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FingerprintApp()
    window.show()
    sys.exit(app.exec_())