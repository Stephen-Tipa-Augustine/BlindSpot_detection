from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
import time
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.icon_definitions import md_icons


class StandbyMode(BoxLayout):

    def __init__(self, monitor_screen = None, **kwargs):
        super(StandbyMode, self).__init__(**kwargs)
        self.monitor_screen = monitor_screen


class ActiveMode(BoxLayout):

    def __init__(self, monitor_screen = None, **kwargs):
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
            self.resize_window(800, 600)
            Window.borderless = False
            # Window.maximize()
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
    detected_objects = ListProperty(defaultvalue=[])
    number_of_detected_objects = NumericProperty(defaultvalue=0)
    position_of_detected_objects = ListProperty(defaultvalue=[])

    def __init__(self, **kwargs):
        super(MonitorScreen, self).__init__(**kwargs)

    def switch_view(self, switch):
        container = self.ids.monitor_body
        container.clear_widgets()
        self.detected_objects = []
        self.number_of_detected_objects = 0
        self.position_of_detected_objects = []
        if not switch.active:
            self.system_status = True
            container.add_widget(ActiveMode(monitor_screen=self))
        else:
            self.system_status = False
            container.add_widget(StandbyMode(monitor_screen=self))


class BSDSApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        SplashScreen.resize_window(400, 300)
        Window.borderless = True
        Window.allow_screensaver = True


if __name__ == '__main__':
    BSDSApp().run()
