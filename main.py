from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
import time
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.icon_definitions import md_icons
from kivymd.uix.button import MDIconButton
from BSDS_firmware.accelerometer import Accelerometer
import pygame


class BlindSpotObject(MDIconButton):

    def __init__(self, **kwargs):
        super(BlindSpotObject, self).__init__(**kwargs)


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

    def __init__(self, **kwargs):
        super(MonitorScreen, self).__init__(**kwargs)
        # initialize accelerometer "MPU6050"
        self.accel_obj = Accelerometer()
        Clock.schedule_interval(self.detect_motion, 10)
        self.mode = 'standby'
        pygame.mixer.init()

    def detect_motion(self, dt):
        try:
            self.accel_obj.vehicle_moving()
            self.accel_obj.vehicle_rotating()
            status = self.accel_obj.moving or self.accel_obj.rotating
            if self.mode == 'standby' and status and not self.system_status:
                self.switch_view(switch=self.accel_obj.moving or self.accel_obj.rotating, auto=True)
                self.system_status = status
        except:
            pass

    def switch_view(self, switch=None, auto=False):
        container = self.ids.monitor_body
        container.clear_widgets()
        self.detected_objects = []
        self.number_of_detected_objects = 0
        self.position_of_detected_objects = []
        self._switch_view(switch=switch, container=container)

    def _switch_view(self, switch, container):
        print('The system status is: ', self.system_status)
        print('The switch status is: ', switch)
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
        new_value = 0 if self.mute else value/100
        print('New vol is: ', new_value)
        pygame.mixer.music.set_volume(new_value)


class BSDSApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        SplashScreen.resize_window(400, 300)
        Window.borderless = True
        Window.allow_screensaver = True

        screen = Builder.load_file('root.kv')

        return screen


if __name__ == '__main__':
    BSDSApp().run()
