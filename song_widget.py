#imports 
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QWidget, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from stylesheet import set_stylesheet

class SongListElement(QFrame):
    def __init__(self, parent, song_name, wav_file, similarity, rank=None):
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
        self.similarity = similarity
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
        layout.addStretch()  # This will push similarity label to align with header

        # Add spacing to align with header
        layout.addSpacing(20)

        # Create the similarity label
        self.similarity_label = QLabel(f"Similarity: {similarity:.1f}%")
        self.similarity_label.setStyleSheet("color: #1DB954; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.similarity_label)

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

    def add_song(self, song_name, wav_file, similarity):
        # Create new song element with rank based on insertion position
        insert_pos = 0
        for song in self.songs:
            if similarity <= song.similarity:
                insert_pos += 1
            else:
                break
                
        new_song = SongListElement(self.container, song_name, wav_file, similarity, rank=insert_pos + 1)
        self.songs.insert(insert_pos, new_song)
        
        # Insert widget before the stretch spacer
        self.layout.insertWidget(insert_pos + 1, new_song)  # +1 to account for header
        
        # Update ranks for all songs after the insertion point
        for i in range(insert_pos + 1, len(self.songs)):
            self.songs[i].rank_label.setText(f"#{i + 1}")



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Song UI")

        # Create the main layout
        layout = QVBoxLayout()

        # Create the scrollable song list
        self.song_list = ScrollableSongList()
        layout.addWidget(self.song_list)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Add some example songs
        self.song_list.add_song("Song 1", "Task 5 Data/original data/songs/wen_elkhael[music+vocals].wav", 95.5)
        self.song_list.add_song("Song 2", "Task 5 Data/original data/music/wen_elkhael [music].wav", 87.3)
        self.song_list.add_song("Song 3", "Task 5 Data/original data/music/wen_elkhael [music].wav", 82.1)
        self.song_list.add_song("Song 1", "Task 5 Data/original data/songs/wen_elkhael[music+vocals].wav", 95.5)
        self.song_list.add_song("Song 2", "Task 5 Data/original data/music/wen_elkhael [music].wav", 87.3)
        self.song_list.add_song("Song 3", "Task 5 Data/original data/music/wen_elkhael [music].wav", 82.1)
        self.song_list.add_song("Song 1", "Task 5 Data/original data/songs/wen_elkhael[music+vocals].wav", 95.5)
        self.song_list.add_song("Song 2", "Task 5 Data/original data/music/wen_elkhael [music].wav", 87.3)
        self.song_list.add_song("Song 3", "Task 5 Data/original data/music/wen_elkhael [music].wav", 82.1)
        self.resize(400, 600)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
