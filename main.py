from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
import time
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.icon_definitions import md_icons
from kivy.animation import Animation, AnimationTransition
from kivy.graphics import Color, Canvas
from kivy.uix.widget import Widget
from kivymd.uix.button import MDIconButton
import random


class BlindSpotObject(MDIconButton):

    def __init__(self, **kwargs):
        super(BlindSpotObject, self).__init__(**kwargs)


class StandbyMode(BoxLayout):

    def __init__(self, monitor_screen=None, **kwargs):
        super(StandbyMode, self).__init__(**kwargs)
        self.monitor_screen = monitor_screen


class MyRectangle(Widget):
    animate = BooleanProperty(False)
    pos_coord = ListProperty([0, 0])
    size_attributes = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super(MyRectangle, self).__init__(**kwargs)
        self.draw_rec()

    def draw_rec(self):
        with self.canvas:
            Color(.1, 1, .1, .9)
            Line(width=2,
                 rectangle=(
                     self.pos_coord[0], self.pos_coord[1], self.size_attributes[0], self.size_attributes[1]))


class CanvasDrawing(Widget):
    widget_width = NumericProperty(0)
    widget_height = NumericProperty(0)
    widget_center_x = NumericProperty(0)
    widget_center_y = NumericProperty(0)
    detected_objects = ListProperty(defaultvalue=[])
    number_of_detected_objects = NumericProperty(defaultvalue=0)
    position_of_detected_objects = ListProperty(defaultvalue=[])

    # Mapping parameters
    bus_top = NumericProperty(0)
    bus_left = NumericProperty(0)
    bus_bottom = NumericProperty(0)
    bus_right = NumericProperty(0)
    boundary_top = NumericProperty(0)
    boundary_left = NumericProperty(0)
    boundary_bottom = NumericProperty(0)
    boundary_right = NumericProperty(0)

    dy = NumericProperty(0)
    dx = NumericProperty(0)
    object_size = NumericProperty(55.0)
    top_offset = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CanvasDrawing, self).__init__(**kwargs)
        self.pos_factors_x = [.1, .2, .25, .3]
        self.pos_factors_y = [.2, .3, .4, .45, .5]
        self.colors = ((1, 0, 0, .9), (0, 1, 0, .9))
        # self.timer = 0
        # self.add_object_now = False
        # self.draw_rec()
        Clock.schedule_interval(self.update_canvas, timeout=10)
        # anim = Animation(rgba=(1, 0, 0, 1)) + Animation(rgba=(0, 1, 0, 1)) + Animation(rgba=(0, 0, 1, 1))
        # anim.repeat = True
        # anim.start

    def update_canvas(self, *args):
        if self.number_of_detected_objects % 2 == 0:
            self.add_object(kind='car', pos_factor=1, color=random.choice(self.colors))
        else:
            self.add_object(kind='car',
                            pos_factor=(random.choice(self.pos_factors_x), random.choice(self.pos_factors_y)),
                            color=random.choice(self.colors))
        print('Changes in x and y: ', self.dx, self.dy)

    def add_object(self, kind, pos_factor, color):
        """
        :param color: a tuple of the color proportions
        :param pos_factor: a numeric value used for computing the position
        :param kind: string options, one of ['car', 'motorbike', 'human-handsdown', 'bike-fast']
        :return:
        """
        if pos_factor == 1:
            center = self.widget_center_x, self.bus_bottom
        else:
            center = self.widget_center_x - self.widget_width * pos_factor[0], self.widget_center_y - \
                     self.widget_height * pos_factor[1]
        obj = MDIconButton(icon=kind, center=center, user_font_size="32sp", theme_text_color="Custom", text_color=color)
        self.detected_objects.append(obj)
        self.number_of_detected_objects += 1
        self.add_widget(obj)

    def print_parameters(self, *args):
        with self.canvas.after:
            Color(1, 0, 0, .9)
            Line(width=5,
                 rectangle=(
                     self.widget_center_x - self.widget_width * .125, self.widget_center_y - self.widget_height * .3,
                     self.widget_width * .25, self.widget_height * .6))
        print('width: {}, height: {}, center_x: {}, center_y: {}'.format(self.widget_width, self.widget_height,
                                                                         self.widget_center_x, self.widget_center_y))

    def draw_rec(self):
        with self.canvas.after:
            Color(1, 1, 0, .9)
            Line(width=2,
                 rectangle=(
                     self.widget_center_x - self.widget_width * .125, self.widget_center_y - self.widget_height * .3,
                     self.widget_width * .25, self.widget_height * .6))


class ActiveMode(BoxLayout):

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
