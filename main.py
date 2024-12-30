from PyQt5 import QtWidgets, uic
import sys
from song_widget import ScrollableSongList
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load the UI file
        self.ui= uic.loadUi('main_window.ui', self)
        self.selected_song = None
        self.song_list = ScrollableSongList()
        self.ui.rank_wgt.layout().addWidget(self.song_list)
        self.song_list.add_song("Song 1", "Task 5 Data/original data/songs/wen_elkhael[music+vocals].wav", 95.5)
        self.song_list.add_song("Song 2", "Task 5 Data/original data/music/wen_elkhael [music].wav", 87.3)
        self.song_list.add_song("Song 3", "Task 5 Data/original data/music/wen_elkhael [music].wav", 82.1)
        self.song_list.add_song("Song 1", "Task 5 Data/original data/songs/wen_elkhael[music+vocals].wav", 95.5)
        self.song_list.add_song("Song 2", "Task 5 Data/original data/music/wen_elkhael [music].wav", 87.3)
        self.song_list.add_song("Song 3", "Task 5 Data/original data/music/wen_elkhael [music].wav", 82.1)
        self.song_list.add_song("Song 1", "Task 5 Data/original data/songs/wen_elkhael[music+vocals].wav", 95.5)
        self.song_list.add_song("Song 2", "Task 5 Data/original data/music/wen_elkhael [music].wav", 87.3)
        self.song_list.add_song("Song 3", "Task 5 Data/original data/music/wen_elkhael [music].wav", 82.1)
        self.connections()
        self.ui.play_song_btn.setText("▶")
        self.ui.play_song_btn.setStyleSheet("font-size: 24px; color: white;")
        self.ui.play_song_btn.hide()
        self.player = QMediaPlayer()
        # self.player.setMedia(QMediaContent(QUrl.fromLocalFile(wav_file)))
        self.ui.show()
    def connections(self):
        self.ui.choose_file.clicked.connect(self.choose_song)
        self.ui.play_song_btn.clicked.connect(self.play_stop_selected_song)
    def choose_song(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Audio files (*.wav *.mp3)")
        file_path, _ = file_dialog.getOpenFileName(self, "Choose Audio File", "", "Audio files (*.wav *.mp3)")
        if file_path:
            self.selected_song = file_path
            name = file_path.split("/")[-1]
            self.ui.song_name.setText(name)
            self.ui.play_song_btn.show()

    
    def play_stop_selected_song(self):
        if self.selected_song:
            if self.ui.play_song_btn.text() == "▶":
                self.ui.play_song_btn.setText("◻")
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.selected_song)))
                self.player.play()
            else:
                self.ui.play_song_btn.setText("▶")
                self.player.stop()
        else:
            print("No song selected")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())