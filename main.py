import sys

from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
import time
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.icon_definitions import md_icons
from BSDS_firmware.accelerometer import Accelerometer
import pygame
from kivymd.uix.dialog import MDDialog
import threading
import queue
import sys
import RPi.GPIO as GPIO


class MessageItem(BoxLayout):

    def __init__(self, **kwargs):
        super(MessageItem, self).__init__(**kwargs)


class StandbyMode(BoxLayout):

    def __init__(self, monitor_screen=None, **kwargs):
        super(StandbyMode, self).__init__(**kwargs)
        self.monitor_screen = monitor_screen


class ActiveMode(BoxLayout):
    monitor_screen = ObjectProperty(None)

    def __init__(self, monitor_screen=None, **kwargs):
        super(ActiveMode, self).__init__(**kwargs)
        self.monitor_screen = monitor_screen


class SplashScreen(BoxLayout):
    screen_manager = ObjectProperty(None)
    app_window = ObjectProperty(None)
    monitor_screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_progress_bar, .2)

    def update_progress_bar(self, *args):
        if (self.ids.progress_bar.value + 5) < 100:
            raw_value = self.ids.progress_bar_label.text.split('[')[-1]
            value = raw_value[:-2]
            value = eval(value.strip())
            new_value = value + 5
            self.ids.progress_bar.value = new_value
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(new_value)
        else:
            self.ids.progress_bar.value = 100
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(100)
            time.sleep(2)
            self.screen_manager.current = 'main_screen'
            # self.resize_window(800, 600)
            Window.borderless = False
            Window.maximize()
            return False

    @staticmethod
    def resize_window(width=0, height=0):
        center0 = Window.center
        Window.size = (width, height)
        center1 = Window.center
        Window.left -= center1[0] - center0[0]
        Window.top -= center1[1] - center0[1]


class MonitorScreen(ScrollView):
    nav_drawer = ObjectProperty()
    # Defining global variables
    system_status = BooleanProperty(defaultvalue=False)
    mute = BooleanProperty(defaultvalue=False)
    detected_objects = ListProperty(defaultvalue=[])
    number_of_detected_objects = NumericProperty(defaultvalue=0)
    position_of_detected_objects = ListProperty(defaultvalue=[])
    app_window = ObjectProperty()

    def __init__(self, **kwargs):
        super(MonitorScreen, self).__init__(**kwargs)
        # initialize accelerometer "MPU6050"
        self.motion_queue = queue.Queue()
        Clock.schedule_once(self.initialize_accelerometer, 5)
        # Clock.schedule_interval(self.get_objects, 2)
        self.mode = 'standby'
        pygame.mixer.init()

    def initialize_accelerometer(self, *args):
        threading.Thread(target=self.accelerometer_process, args=(self.motion_queue,), daemon=True).start()
        Clock.schedule_interval(self.detect_motion, 2)

    def get_objects(self, *args):
        if not self.app_window.left_object_detector.empty():
            print('Detected: ', self.app_window.left_object_detector.get(block=False))
        else:
            print('Got nothing!')

    @staticmethod
    def accelerometer_process(q):
        accel_obj = Accelerometer()
        while True:
            if accel_obj.sensor:
                accel_obj.vehicle_moving()
                accel_obj.vehicle_rotating()
                status = accel_obj.moving or accel_obj.rotating
                q.put(status)
                time.sleep(3)
            else:
                accel_obj = Accelerometer()

    def detect_motion(self, dt):
        if not self.motion_queue.empty():
            status = self.motion_queue.get(block=False)
            if self.mode == 'standby' and status and not self.system_status:
                self.switch_view(switch=status, auto=True)
                self.system_status = True
                self.ids.system_switch.active = True
        else:
            pass

    def switch_view(self, switch=None, auto=False):
        container = self.ids.monitor_body
        container.clear_widgets()
        self.detected_objects = []
        self.number_of_detected_objects = 0
        self.position_of_detected_objects = []
        self._switch_view(switch=switch, container=container)

    def _switch_view(self, switch, container):
        if switch:
            container.add_widget(ActiveMode(monitor_screen=self))
            self.mode = 'active'
        else:
            container.add_widget(StandbyMode(monitor_screen=self))
            self.mode = 'standby'
        self.system_status = switch

    # @staticmethod
    def set_volume(self, value=0, disable=False):
        if disable and self.mute:
            self.mute = False
        elif disable and not self.mute:
            self.mute = True
        new_value = 0 if self.mute else value / 100
        pygame.mixer.music.set_volume(new_value)


class BSDSApp(MDApp):
    dialog = None
    # left_object_detector = ObjectProperty(defaultvalue=queue.Queue())
    # detection_model_left = DetectionModel()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        SplashScreen.resize_window(400, 300)
        Window.borderless = True
        Window.allow_screensaver = True

        screen = Builder.load_file('root.kv')

        return screen
        
    def on_stop(self):
        GPIO.cleanup()
        sys.exit(0)

    # def initialize_object_detectors(self):
    #     threading.Thread(target=self.detection_model_left.run, args=(self.left_object_detector,), daemon=True).start()


if __name__ == '__main__':
    BSDSApp().run()
