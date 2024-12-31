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
        self.ui.choose_file.clicked.connect(lambda: self.choose_audio_file(1))
        self.ui.play_song_btn.clicked.connect(lambda: self.play_stop_song(1))
        self.ui.choose_file_2.clicked.connect(lambda: self.choose_audio_file(2))
        self.ui.play_song_btn_2.clicked.connect(lambda: self.play_stop_song(2))
        self.ui.choose_file_3.clicked.connect(lambda: self.choose_audio_file(3))
        self.ui.play_song_btn_3.clicked.connect(lambda: self.play_stop_song(3))

    def choose_audio_file(self, player_id):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Audio files (*.wav *.mp3)")
        file_path, _ = file_dialog.getOpenFileName(self, "Choose Audio File", "", "Audio files (*.wav *.mp3)")
        if file_path:
            if player_id == 1:
                self.selected_song = file_path
                self.ui.song_name.setText(file_path.split("/")[-1])
                self.ui.play_song_btn.show()
            elif player_id == 2:
                self.mix_song1 = file_path
                self.ui.song_name_2.setText(file_path.split("/")[-1])
                self.ui.play_song_btn_2.show()
            else:
                self.mix_song2 = file_path
                self.ui.song_name_3.setText(file_path.split("/")[-1])
                self.ui.play_song_btn_3.show()

    def play_stop_song(self, player_id):
        if player_id == 1:
            song = self.selected_song
            btn = self.ui.play_song_btn
            player = self.player
        elif player_id == 2:
            song = self.mix_song1
            btn = self.ui.play_song_btn_2
            player = self.player_mix1
        else:
            song = self.mix_song2
            btn = self.ui.play_song_btn_3
            player = self.player_mix2

        if song:
            if btn.text() == "▶":
                btn.setText("◻")
                player.setMedia(QMediaContent(QUrl.fromLocalFile(song)))
                player.play()
            else:
                btn.setText("▶")
                player.stop()
        else:
            print("No song selected")
            
    def get_top_matches(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())