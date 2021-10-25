import sys

from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from detect_object import DetectionModel
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivy.clock import Clock
import threading
import queue


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detection_model = DetectionModel()
        self.label = MDLabel(
                text='Detected none',
                pos_hint={"center_x": 0.5, "center_y": 0.5},
            )
        self.objects = queue.Queue()

    def build(self):
        screen = Screen()
        container = MDBoxLayout(
                orientation='vertical'
            )
        screen.add_widget(container)
        container.add_widget(
            MDRectangleFlatButton(
                text="Hello, World",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_press=self.start_object_detection,
            )
        )
        screen.add_widget(self.label)
        return screen

    def start_object_detection(self, *args):
        threading.Thread(target=self.detection_model.run, args=(self.objects,)).start()
        Clock.schedule_interval(self.get_objects, 2)

    def get_objects(self, *args):
        if not self.objects.empty():
            self.label.text = ', '.join(self.objects.get(block=False))
        else:
            print('Got nothing!')


if __name__ == '__main__':
    MainApp().run()
