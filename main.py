from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaContent
from matchmaker import Match_Maker
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QWidget, QScrollArea, QSpacerItem, QSizePolicy
from stylesheet import set_stylesheet


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Insatntiate match maker class
        # Database will be created in the background
        self.mk = Match_Maker()
        # Load the UI file
        self.ui= uic.loadUi('main_window.ui', self)
        self.curr_audio_file = None
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
        self.ui.Play_stop_mix.setText("▶")
        self.ui.Play_stop_mix.setStyleSheet("font-size: 24px; color: white;")
        self.ui.play_song_btn.hide()
        self.ui.play_song_btn_2.hide()
        self.ui.play_song_btn_3.hide()
        self.player = QMediaPlayer()
        self.player_mix1 = QMediaPlayer()
        self.player_mix2 = QMediaPlayer()
        self.mixer_player = QMediaPlayer()
        self.mix_song1 = None
        self.mix_song2 = None
        self.w1 = 0.5
        self.w2 = 0.5
        self.ui.show()
    
    def connections(self):
        self.ui.choose_file.clicked.connect(lambda: self.choose_audio_file(1))
        self.ui.play_song_btn.clicked.connect(lambda: self.play_stop_song(1))
        self.ui.choose_file_2.clicked.connect(lambda: self.choose_audio_file(2))
        self.ui.play_song_btn_2.clicked.connect(lambda: self.play_stop_song(2))
        self.ui.choose_file_3.clicked.connect(lambda: self.choose_audio_file(3))
        self.ui.play_song_btn_3.clicked.connect(lambda: self.play_stop_song(3))
        self.ui.Mix_btn.clicked.connect(lambda: self.get_top_matches(True))
        self.ui.weighting.valueChanged.connect(self.update_weightes)
        self.ui.Play_stop_mix.clicked.connect(self.play_stop_mix)
        
    def choose_audio_file(self, player_id):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter("Audio files (*.wav *.mp3)")
        file_path, _ = file_dialog.getOpenFileName(self, "Choose Audio File", "", "Audio files (*.wav *.mp3)")
        if file_path:
            if player_id == 1:
                self.selected_song = file_path
                if (self.curr_audio_file!=self.selected_song) or (self.curr_audio_file==None):
                    self.curr_audio_file = self.selected_song
                    self.ui.song_name.setText(file_path.split("/")[-1])
                    self.ui.play_song_btn.show()
                    self.get_top_matches()
            elif player_id == 2:
                self.mix_song1 = file_path
                self.ui.song_name_2.setText(file_path.split("/")[-1])
                self.ui.play_song_btn_2.show()
            else:
                self.mix_song2 = file_path
                self.ui.song_name_3.setText(file_path.split("/")[-1])
                self.ui.play_song_btn_3.show()
            
        
    def get_top_matches(self, mix=False):
        """
        return the top matches
        """
        if self.song_list.songs:
            self.song_list.clear_all_songs()    
            
        if mix and self.mix_song1 and self.mix_song2:
            self.mk.new_search(self.mix_song1, self.mix_song2, True,self.w1)
        else:       
            self.mk.new_search(self.selected_song)  
                   
        matches = self.mk.get_top_matches()
        self.add_matches(matches)

    
    def update_weightes(self):
        slider_current_value = self.ui.weighting.value()
        w2 = slider_current_value/100
        w1 = 1 - w2
        self.song1_w.setText(f"Song1: {int(w1*100)}")
        self.song2_w.setText(f"Song2: {int(w2*100)}")
        self.w1 = w1
        self.w2 = w2
        
    def add_matches(self, matches):
        for match in matches:
            name = match['audio_name']
            path = match['file_path']
            score = match['score']      
            
            self.song_list.add_song(song_name=name, wav_file=path, similarity_index=score)


    def play_stop_mix(self):
        path = self.mk.mix_path
        if path:
            if self.ui.play_mix_btn.text() == "▶":
                self.ui.play_mix_btn.setText("◻")
                self.mixer_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
                self.mixer_player.play()
            else:
                self.ui.play_mix_btn.setText("▶")
                self.mixer_player.stop()
        
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
            

class ScrollableSongList(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        set_stylesheet(self)
        
        # Create container widget and layout
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        
        # Remove extra spacing
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setWidget(self.container)
        self.songs = []

        # Add header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        rank_header = QLabel("")
        name_header = QLabel("") 
        similarity_header = QLabel("")
        
        header_layout.addWidget(rank_header)
        header_layout.addWidget(name_header)
        header_layout.addStretch()
        header_layout.addWidget(similarity_header)
        header_layout.addSpacing(40)  # Space for play button
        
        self.layout.addWidget(header)
        
        # Add spacing at the end
        self.layout.addStretch()

    def clear_all_songs(self):
        for song in self.songs:
            song.deleteLater()
        self.songs = []
        self.layout.addStretch()

        
    def add_song(self, song_name, wav_file, similarity_index):
        # Create new song element with rank based on insertion position
        insert_pos = 0
        for song in self.songs:
            if similarity_index <= song.similarity_index:
                insert_pos += 1
            else:
                break
                
        new_song = SongListElement(self.container, song_name, wav_file, similarity_index, rank=insert_pos + 1)
        self.songs.insert(insert_pos, new_song)
        
        # Insert widget before the stretch spacer
        self.layout.insertWidget(insert_pos + 1, new_song)  # +1 to account for header
        
        # Update ranks for all songs after the insertion point
        for i in range(insert_pos + 1, len(self.songs)):
            self.songs[i].rank_label.setText(f"#{i + 1}")

class SongListElement(QFrame):
    def __init__(self, parent, song_name, wav_file, similarity_index, rank=None):
        super().__init__(parent)
        
        # Configure the frame
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #3E3E3E;
                border-radius: 10px;
                background-color: #1E1E1E;
            }

        """)
        self.setFixedHeight(60)

        # Store song information
        self.song_name = song_name
        self.wav_file = wav_file
        self.similarity_index = similarity_index

        # Create layout
        layout = QHBoxLayout(self)

        # Create rank label if provided
        self.rank_label = QLabel(f"#{rank}")
        self.rank_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.rank_label)

        # Create the song name label
        self.name_label = QLabel(song_name)
        self.name_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.name_label)
        layout.addStretch()  # This will push similarity_index label to align with header

        # Add spacing to align with header
        layout.addSpacing(20)

        # Create the similarity_index label
        self.similarity_index_label = QLabel(f"similarity_score: {similarity_index:.3f}%")
        self.similarity_index_label.setStyleSheet("color: #1DB954; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.similarity_index_label)

        # Create spacer to push play button to the right
        layout.addStretch()

        # Create the play button
        self.play_button = QPushButton("▶")
        #font 
        self.play_button.setStyleSheet("font-size: 24px; color: white;")
        self.is_playing = False
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(wav_file)))
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setFixedSize(40, 40)

        layout.addWidget(self.play_button)

    def toggle_playback(self):
        if self.is_playing:
            self.player.stop()
            self.play_button.setText("▶")
        else:
            self.player.play()
            self.play_button.setText("◻")
        self.is_playing = not self.is_playing

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()    
    sys.exit(app.exec_())