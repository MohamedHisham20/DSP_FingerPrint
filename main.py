from PyQt5 import QtWidgets, uic
import sys
from song_widget import ScrollableSongList
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
#from matchmaker import Match_Maker

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load the UI file
        self.ui= uic.loadUi('main_window.ui', self)
        self.selected_song = None
        self.song_list = ScrollableSongList()
        self.ui.rank_wgt.layout().addWidget(self.song_list)
        self.connections()
        self.ui.play_song_btn.setText("▶")
        self.ui.play_song_btn.setStyleSheet("font-size: 24px; color: white;")
        self.ui.play_song_btn_2.setText("▶")
        self.ui.play_song_btn_2.setStyleSheet("font-size: 24px; color: white;")
        self.ui.play_song_btn_3.setText("▶")
        self.ui.play_song_btn_3.setStyleSheet("font-size: 24px; color: white;")
        self.ui.play_song_btn.hide()
        self.ui.play_song_btn_2.hide()
        self.ui.play_song_btn_3.hide()
        self.player = QMediaPlayer()
        self.player_mix1 = QMediaPlayer()
        self.player_mix2 = QMediaPlayer()
        self.mix_song1 = None
        self.mix_song2 = None
        # self.player.setMedia(QMediaContent(QUrl.fromLocalFile(wav_file)))
        self.ui.show()
    
    def connections(self):
        self.ui.choose_file.clicked.connect(self.choose_song)
        self.ui.play_song_btn.clicked.connect(self.play_stop_selected_song)

        self.ui.choose_file_2.clicked.connect(self.choose_mix_song1)
        self.ui.play_song_btn_2.clicked.connect(self.play_stop_mix_song1)
        self.ui.choose_file_3.clicked.connect(self.choose_mix_song2)
        self.ui.play_song_btn_3.clicked.connect(self.play_stop_mix_song2)


    def choose_song(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Audio files (*.wav *.mp3)")
        file_path, _ = file_dialog.getOpenFileName(self, "Choose Audio File", "", "Audio files (*.wav *.mp3)")
        if file_path:
            self.selected_song = file_path
            name = file_path.split("/")[-1]
            self.ui.song_name.setText(name)
            self.ui.play_song_btn.show()
    def choose_mix_song1(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Audio files (*.wav *.mp3)")
        file_path, _ = file_dialog.getOpenFileName(self, "Choose Audio File", "", "Audio files (*.wav *.mp3)")
        if file_path:
            self.mix_song1 = file_path
            name = file_path.split("/")[-1]
            self.ui.song_name_2.setText(name)
            self.ui.play_song_btn_2.show()
    def choose_mix_song2(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Audio files (*.wav *.mp3)")
        file_path, _ = file_dialog.getOpenFileName(self, "Choose Audio File", "", "Audio files (*.wav *.mp3)")
        if file_path:
            self.mix_song2 = file_path
            name = file_path.split("/")[-1]
            self.ui.song_name_3.setText(name)
            self.ui.play_song_btn_3.show()
    def play_stop_mix_song1(self):
        if self.mix_song1:
            if self.ui.play_song_btn_2.text() == "▶":
                self.ui.play_song_btn_2.setText("◻")
                self.player_mix1.setMedia(QMediaContent(QUrl.fromLocalFile(self.mix_song1)))
                self.player_mix1.play() 
            else:
                self.ui.play_song_btn_2.setText("▶")
                self.player_mix1.stop()
        else:
            print("No song selected")
    def play_stop_mix_song2(self):
        if self.mix_song2:
            if self.ui.play_song_btn_3.text() == "▶":
                self.ui.play_song_btn_3.setText("◻")
                self.player_mix2.setMedia(QMediaContent(QUrl.fromLocalFile(self.mix_song2)))
                self.player_mix2.play()
            else:
                self.ui.play_song_btn_3.setText("▶")
                self.player_mix2.stop()
        else:
            print("No song selected")
    

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
            
    def get_top_matches(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())