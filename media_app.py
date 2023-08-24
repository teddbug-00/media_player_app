import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QListWidget
import os
import random


class MediaPlayerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player")
        self.resize(800, 600)

        self.create_menu_bar()
        self.create_button_bar()
        self.create_seek_bar()

        self.media_player = QtMultimedia.QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)
        self.media_player.setVideoOutput(self.video_widget)

        self.list_widget = QListWidget(self)

        self.timer = QtCore.QTimer()  # Add the QTimer instance
        self.timer.setInterval(100)  # Set the interval to 1000ms (1 second)
        self.timer.timeout.connect(self.update_seek_bar)  # Connect the timeout signal to the update_seek_bar method

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(self.video_widget)
        main_layout.addWidget(self.seek_bar)
        main_layout.addWidget(self.button_container)
        
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    # Rest of the code...


    def create_button_bar(self):
        buttons = [
            ("previous_button", "media-skip-backward", self.play_previous),
            ("play_button", "media-playback-start", self.play),
            ("pause_button", "media-playback-pause", self.pause),
            ("stop_button", "media-playback-stop", self.stop),
            ("next_button", "media-skip-forward", self.play_next),
            ("switch_view_button", "Playlist", self.switch_view),
            ("shuffle_button", "media-playlist-shuffle", self.shuffle_files),
            ("clear_all_button", "edit-clear-all", self.clear_all_files),
            ("remove_selected_button", "edit-delete", self.remove_selected_file),
            ("load_files_button", "document-open", self.load_files),
            ("save_list_button", "document-save", self.save_list),
            ("sort_files_button", "view-sort-ascending", self.sort_files),
            ("fullscreen_button", "view-fullscreen", self.toggle_fullscreen),
            ("volume_slider", "audio-volume-high", None),
            ("repeat_button", "media-playlist-repeat", self.toggle_repeat),
        ]

        self.is_repeating = False  # Add the is_repeating attribute

        self.button_container = QtWidgets.QWidget(self)
        button_layout = QtWidgets.QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        for button_name, icon_name, button_action in buttons:
            if button_name == "volume_slider":
                slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.button_container)
                slider.setRange(0, 100)
                slider.setValue(50)
                slider.valueChanged.connect(self.set_volume)
                button_layout.addWidget(slider)
                setattr(self, button_name, slider)
            else:
                button = QtWidgets.QPushButton(self.button_container)
                button.setIcon(QtGui.QIcon.fromTheme(icon_name))
                button.clicked.connect(button_action)
                button_layout.addWidget(button)
                setattr(self, button_name, button)

        button_layout.addStretch()
        self.button_container.setMaximumHeight(30)


    def create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        add_file_action = QtWidgets.QAction("Add File", self)
        add_folder_action = QtWidgets.QAction("Add Folder", self)
        add_file_action.triggered.connect(self.open_file)
        add_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(add_file_action)
        file_menu.addAction(add_folder_action)

        # Add a new action for the playlist
        playlist_menu = menu_bar.addMenu("Playlist")
        playlist_action = QtWidgets.QAction("Open Playlist", self)
        playlist_action.triggered.connect(self.open_playlist)
        playlist_menu.addAction(playlist_action)


    def open_file(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        file_dialog.setNameFilter("Media Files (*.mp3 *.mp4 *.mkv *.flac)")

        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()

            for file_path in file_paths:
                if file_path:
                    self.add_file(file_path)
                    item = QtWidgets.QListWidgetItem(os.path.basename(file_path))
                    item.setData(QtCore.Qt.UserRole, file_path)
                    self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self.play_selected_file)


    def create_seek_bar(self):
        self.seek_bar = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.seek_bar.setRange(0, 100)
        self.seek_bar.sliderPressed.connect(self.seek_bar_pressed)
        self.seek_bar.sliderReleased.connect(self.seek_bar_released)
        self.seek_bar.sliderMoved.connect(self.seek_bar_moved)


    def play(self):
        self.media_player.play()
        self.timer.start()
        self.video_widget.show()  # Show the video widget when playback starts

    def pause(self):
        self.media_player.pause()
        self.timer.stop()

    def update_seek_bar(self):
        if self.media_player.duration() > 0:
            position = self.media_player.position()
            duration = self.media_player.duration()
            self.seek_bar.setValue(int(position / duration * 100))
            self.media_player.duration()
            self.seek_bar.setValue(int(position / duration * 100))

    def seek_bar_pressed(self):
        self.timer.stop()


    def update_seek_bar_value(self, event):
        position = event.pos().x()
        bar_width = self.seek_bar.width()
        bar_min = self.seek_bar.minimum()
        bar_max = self.seek_bar.maximum()
        value = bar_min + ((bar_max - bar_min) * position) / bar_width
        self.seek_bar.setValue(int(value))
        self.seek_bar_released()


    def seek_bar_released(self):
        duration = self.media_player.duration()
        position = self.seek_bar.value() * duration // self.seek_bar.maximum()
        self.media_player.setPosition(position)
        self.media_player.play()
        self.timer.start()

    def seek_bar_moved(self):
        duration = self.media_player.duration()
        position = self.seek_bar.value() * duration / 100
        self.seek_bar.setToolTip(f"{self.format_time(position)} / {self.format_time(duration)}")

    def stop(self):
        self.media_player.stop()
        self.timer.stop()
        self.seek_bar.setValue(0)

    def format_time(self, milliseconds):
        total_seconds = int(milliseconds / 1000)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def add_folder(self, folder_path):
        self.list_widget.clear()
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.add_file(file_path)
                item = QtWidgets.QListWidgetItem(file)  # Create a QListWidgetItem object
                item.setData(QtCore.Qt.UserRole, file_path)  # Set the file path as user data
                self.list_widget.addItem(item)  # Add the item to the list widget
        self.list_widget.itemDoubleClicked.connect(self.play_selected_file)  # Connect the double-click signal

    def play_selected_file(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            file_path = current_item.data(QtCore.Qt.UserRole)
            self.add_file(file_path)
            self.play()
            if self.is_video_file(file_path):
                self.video_widget.show()  # Show the video widget if it's a video file
                self.list_widget.hide()  # Hide the list widget if it's a video file
            else:
                self.video_widget.hide()  # Hide the video widget if it's an audio file
                self.list_widget.show()  # Show the list widget if it's an audio file
            
        # Always show the seek bar and buttons
        self.seek_bar.show()
        self.button_container.show()


    def add_file(self, file_path):
        if file_path.endswith((".mp3", ".mp4", ".mkv", ".flac")):
            media = QMediaContent(QtCore.QUrl.fromLocalFile(file_path))
            self.media_player.setMedia(media)
    
    def open_folder(self):
        folder_dialog = QtWidgets.QFileDialog()
        folder_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        folder_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if folder_dialog.exec_():
            folder_path = folder_dialog.selectedFiles()[0]
            if folder_path:
                self.add_folder(folder_path)
    
    def switch_view(self):
        if self.video_widget.isHidden():
            self.video_widget.show()
            self.list_widget.hide()
        else:
            self.video_widget.hide()
            self.list_widget.show()
    
    def is_video_file(self, file_path):
        video_extensions = ['.mp4', '.avi', '.mkv']  # Add more video extensions if needed
        file_extension = os.path.splitext(file_path)[1]
        return file_extension in video_extensions

    def play_previous(self):
        current_index = self.list_widget.currentRow()
        if current_index > 0:
            self.list_widget.setCurrentRow(current_index - 1)
            self.play_selected_file()

    def play_next(self):
        current_index = self.list_widget.currentRow()
        if current_index < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(current_index + 1)
            self.play_selected_file()

    def shuffle_files(self):
        items = self.list_widget.count()
        if items > 1:
            current_index = self.list_widget.currentRow()
            indexes = list(range(items))
            indexes.remove(current_index)
            random.shuffle(indexes)

            shuffled_items = [self.list_widget.takeItem(current_index)]

            for index in indexes:
                shuffled_items.append(self.list_widget.takeItem(index))

            for item in shuffled_items:
                self.list_widget.addItem(item)

            self.list_widget.setCurrentRow(0)

    def clear_all_files(self):
        self.list_widget.clear()

    def remove_selected_file(self):
        current_row = self.list_widget.currentRow()
        self.list_widget.takeItem(current_row)
    
    def load_files(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
    
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
    
            for file_path in file_paths:
                self.list_widget.addItem(file_path)
    
    def save_list(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]

            with open(file_path, "w") as file:
                for index in range(self.list_widget.count()):
                    file.write(f"{self.list_widget.item(index).text()}\n")

    def sort_files(self):
        self.list_widget.sortItems()
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def set_volume(self, volume):
        self.media_player.setVolume(volume)
    
    def show_playlist(self):
        self.list_widget.show()
        self.video_widget.hide()
    
    def open_playlist(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Playlist Files (*.m3u *.m3u8)")
    
        if file_dialog.exec_():
            playlist_path = file_dialog.selectedFiles()[0]
            # Implement the logic to open and load the playlist file in your app
    
    def toggle_repeat(self):
        self.is_repeating = not self.is_repeating

        if self.is_repeating:
            self.repeat_button.setIcon(QtGui.QIcon.fromTheme("media-playlist-repeat-activated"))
        else:
            self.repeat_button.setIcon(QtGui.QIcon.fromTheme("media-playlist-repeat"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = MediaPlayerApp()
    player.show()
    sys.exit(app.exec_())
