from kivy.uix.video import Video
from kivy.uix.boxlayout import BoxLayout
import threading
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock


class MyVideo(BoxLayout):
    filename = StringProperty(None)
    webcam_started = ObjectProperty(defaultvalue=None)

    def __init__(self, **kwargs):
        super(MyVideo, self).__init__(**kwargs)
        self.video = None
        threading.Thread(target=self.create_video, daemon=True).start()

    def create_video(self):
        self.video = Video(source='wireframe.mp4')
        Clock.schedule_interval(self.play, 1)
        self.add_widget(self.video)

    def play(self, *args):
        if self.webcam_started.webcam_started:
            self.video.play = True
            return False
