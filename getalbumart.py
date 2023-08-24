import sys
import vlc
import tempfile
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap

class AlbumArtApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Album Art Display")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        self.load_button = QPushButton("Load Music File", self)
        self.load_button.clicked.connect(self.load_music_file)
        self.layout.addWidget(self.load_button)

        self.central_widget.setLayout(self.layout)

    def load_music_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Music File", "", "Music Files (*.mp3 *.ogg *.flac);;All Files (*)", options=options)

        if file_name:
            instance = vlc.Instance()
            media = instance.media_new(file_name)
            media.parse()  # Necessary for metadata retrieval

            album_art = None
            for i in range(media.get_meta(vlc.Meta.ArtworkURL, 0).count()):
                album_art_url = media.get_meta(vlc.Meta.ArtworkURL, i)
                album_art = media.get_meta(vlc.Meta.ArtworkURL, i).encode()
                break

            if album_art:
                temp_dir = tempfile.mkdtemp()
                temp_file_path = os.path.join(temp_dir, "temp_album_art.jpg")
                with open(temp_file_path, "wb") as f:
                    f.write(album_art)

                pixmap = QPixmap(temp_file_path)
                self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_label.setText("No Album Art Found")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlbumArtApp()
    window.show()
    sys.exit(app.exec_())
