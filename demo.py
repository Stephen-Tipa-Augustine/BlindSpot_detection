from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from multiprocessing import Process, Queue, set_start_method, freeze_support
from detect_object import ObjectDetectionModel
from kivy.clock import Clock
import threading
import queue


class MainApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.objects = None

    def build(self):
        screen = Screen()
        screen.add_widget(
            MDRectangleFlatButton(
                text="Hello, World",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_press=self.start_object_detection,
            )
        )
        return screen

    def start_object_detection(self, *args):
        self.objects = queue.Queue()
        threading.Thread(target=ObjectDetectionModel().run, args=(self.objects,), daemon=True).start()
        Clock.schedule_interval(self.get_objects, 2)

    def get_objects(self, *args):
        if not self.objects.empty():
            print(self.objects.get(block=False))
        else:
            print('Got nothing!')


if __name__ == '__main__':
    MainApp().run()
