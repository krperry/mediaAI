import sys  # Import the sys module for system-specific parameters and functions
import json  # Import the json module to work with JSON data
import numpy as np  # Import the numpy library for numerical operations
import soundfile as sf  # Import the soundfile library to read and write sound files
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox, QMessageBox, QSlider
from PySide6.QtCore import QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import requests  # Import the requests library to make HTTP requests
from tunein_api import TuneInAPI  # Import the TuneInAPI class

class StreamPlayer(QMainWindow):
    """
    A class to represent the streaming music player application.
    """
    def __init__(self):
        """
        Initialize the StreamPlayer class.
        """
        super().__init__()
        self.setWindowTitle("Streaming Music Player")
        
        self.settings_file = "settings.json"  # File to save settings
        
        # Initialize media player and audio output
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)  # Set default volume to 50%
        
        # Create UI elements
        self.play_pause_button = QPushButton("Play")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.speed_slider = QSlider(Qt.Horizontal)
        
        # Set focus policies
        self.play_pause_button.setFocusPolicy(Qt.StrongFocus)
        self.volume_slider.setFocusPolicy(Qt.StrongFocus)
        self.speed_slider.setFocusPolicy(Qt.StrongFocus)
        
        # Configure volume slider
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Set default slider value to 50%
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        # Configure speed slider
        self.speed_slider.setRange(-10, 10)
        self.speed_slider.setValue(0)  # Set default slider value to 0
        self.speed_slider.valueChanged.connect(self.change_speed)
        
        # Connect play/pause button
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        
        # Create combo boxes for categories and channels
        self.category_combo_box = QComboBox()
        self.category_combo_box.addItems(["classical", "rock", "jazz", "pop", "news"])
        self.category_combo_box.currentIndexChanged.connect(self.category_selected)
        
        self.channel_combo_box = QComboBox()
        self.channel_combo_box.currentIndexChanged.connect(self.channel_selected)
        
        # Arrange UI elements in a vertical layout
        layout = QVBoxLayout()
        layout.addWidget(self.category_combo_box)
        layout.addWidget(self.play_pause_button)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.channel_combo_box)
        
        # Set the layout to a central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Initialize TuneInAPI and other variables
        self.api = TuneInAPI()  # Initialize the TuneInAPI
        self.current_channel_index = 0  # Initialize current_channel_index
        self.noise_file = "noise.wav"
        self.generate_noise()
        self.noise_url = QUrl.fromLocalFile(self.noise_file)  # Path to the noise file
        
        self.is_playing = False  # Initialize play/pause state
        self.load_settings()  # Load settings from file
        
        # Try to fetch and set the initial channel
        try:
            self.channels = self.get_tunein_stations(self.category_combo_box.currentText())
            if not self.channels:
                raise ValueError("No channels found")
            self.populate_channel_combo_box()
            self.set_channel(self.channels[self.current_channel_index]["URL"])
        except Exception as e:
            self.show_error_message(str(e))
        
        # Connect media player signals
        self.player.mediaStatusChanged.connect(self.media_status_changed)
        self.player.errorOccurred.connect(self.media_error_occurred)
        self.channel_combo_box.setFocus()  # Set focus to the channel combo box
    
    def generate_noise(self):
        """
        Generate a noise file to play when no channels are available.
        """
        duration = 10  # seconds
        sample_rate = 44100  # Hz
        samples = np.random.uniform(-1, 1, duration * sample_rate)
        sf.write(self.noise_file, samples, sample_rate)
    
    def get_tunein_stations(self, category):
        """
        Fetch stations from TuneInAPI based on the selected category.
        
        Args:
            category (str): The category to search for stations.
        
        Returns:
            list: A list of dictionaries containing station information.
        """
        try:
            # Make a request to the TuneInAPI to search for stations in the given category
            stations = self.api.search_stations(category)
            print(f"Fetched stations: {stations}")  # Debug statement
            # Extract URLs from the fetched stations
            urls = [station["URL"] for station in stations if "URL" in station]
            print(f"Extracted URLs: {urls}")  # Debug statement
            return stations
        except Exception as e:
            print(f"Error fetching stations: {e}")
            return []
    
    def populate_channel_combo_box(self):
        """
        Populate the channel combo box with fetched stations.
        """
        self.channel_combo_box.clear()
        for station in self.channels:
            self.channel_combo_box.addItem(station["text"], station["URL"])
        print(f"Populated combo box with {len(self.channels)} channels")  # Debug statement
    
    def category_selected(self, index):
        """
        Handle category selection change.
        
        Args:
            index (int): The index of the selected category.
        """
        category = self.category_combo_box.itemText(index)
        self.channels = self.get_tunein_stations(category)
        self.populate_channel_combo_box()
        if self.channels:
            self.set_channel(self.channels[0]["URL"])
            if self.is_playing:
                self.play()
        else:
            self.play_noise()
    
    def channel_selected(self, index):
        """
        Handle channel selection change.
        
        Args:
            index (int): The index of the selected channel.
        """
        if index >= 0:
            url = self.channel_combo_box.itemData(index)
            self.set_channel(url)
            if self.is_playing:
                self.play()
    
    def set_channel(self, url):
        """
        Set the media player to the selected channel.
        
        Args:
            url (str): The URL of the selected channel.
        """
        print(f"Setting channel to: {url}")  # Debug statement
        try:
            # Make a request to get the content of the URL
            response = requests.get(url)
            # Use the TuneInAPI to resolve the stream URL from the response content
            resolved_url = self.api.resolve_stream_url(response.content)
            print(f"Resolved stream URL: {resolved_url}")  # Debug statement
            # Set the media player source to the resolved URL
            self.player.setSource(QUrl(resolved_url))
        except Exception as e:
            print(f"Error setting channel: {e}")  # Debug statement
            self.play_noise()
    
    def play_noise(self):
        """
        Play noise when no channels are available.
        """
        print("Playing noise")  # Debug statement
        self.player.setSource(self.noise_url)
        self.player.play()
    
    def toggle_play_pause(self):
        """
        Toggle play/pause state.
        """
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """
        Play the media.
        """
        print("Play button clicked")  # Debug statement
        self.player.play()
        self.is_playing = True
        self.play_pause_button.setText("Pause")
        self.save_settings()
    
    def pause(self):
        """
        Pause the media.
        """
        print("Pause button clicked")  # Debug statement
        self.player.pause()
        self.is_playing = False
        self.play_pause_button.setText("Play")
        self.save_settings()
    
    def change_volume(self, value):
        """
        Change the volume based on the slider value.
        
        Args:
            value (int): The value of the volume slider.
        """
        print(f"Volume slider changed to: {value}")  # Debug statement
        self.audio_output.setVolume(value / 100)
        self.save_settings()
    
    def change_speed(self, value):
        """
        Change the playback speed based on the slider value.
        
        Args:
            value (int): The value of the speed slider.
        """
        print(f"Speed slider changed to: {value}")  # Debug statement
        self.player.setPlaybackRate(1 + value / 10)
        self.save_settings()
    
    def media_status_changed(self, status):
        """
        Handle media status changes.
        
        Args:
            status (QMediaPlayer.MediaStatus): The new media status.
        """
        print(f"Media status changed: {status}")  # Debug statement
    
    def media_error_occurred(self, error):
        """
        Handle media errors.
        
        Args:
            error (QMediaPlayer.Error): The error that occurred.
        """
        print(f"Media error occurred: {error}")  # Debug statement
        self.play_noise()
    
    def show_error_message(self, message):
        """
        Show an error message dialog.
        
        Args:
            message (str): The error message to display.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec()
    
    def save_settings(self):
        """
        Save settings to a file.
        """
        settings = {
            "volume": self.audio_output.volume(),
            "playbackRate": self.player.playbackRate(),
            "currentChannelIndex": self.current_channel_index,
            "isPlaying": self.is_playing,
            "currentCategory": self.category_combo_box.currentText()
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
    
    def load_settings(self):
        """
        Load settings from a file.
        """
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                volume = settings.get("volume", 0.5)
                playback_rate = settings.get("playbackRate", 1.0)
                self.current_channel_index = settings.get("currentChannelIndex", 0)
                self.is_playing = settings.get("isPlaying", False)
                current_category = settings.get("currentCategory", "classical")
                
                self.audio_output.setVolume(volume)
                self.volume_slider.setValue(int(volume * 100))  # Update slider value
                self.player.setPlaybackRate(playback_rate)
                self.category_combo_box.setCurrentText(current_category)
                
                self.channels = self.get_tunein_stations(current_category)
                self.populate_channel_combo_box()
                self.set_channel(self.channels[self.current_channel_index]["URL"])
                
                if self.is_playing:
                    self.play()
                else:
                    self.pause()
                
                self.channel_combo_box.setFocus()
        except FileNotFoundError:
            self.category_combo_box.setCurrentIndex(0)
            self.current_channel_index = 0
            self.audio_output.setVolume(0.5)  # Set default volume to 50%
            self.volume_slider.setValue(50)  # Set default slider value to 50%

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StreamPlayer()
    window.show()
    sys.exit(app.exec())
