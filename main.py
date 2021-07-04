# from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.lang import Builder
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


'''class MyRectangle(Widget):
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
                     self.pos_coord[0], self.pos_coord[1], self.size_attributes[0], self.size_attributes[1]))'''


class CanvasDrawing(Widget):
    monitor_screen = ObjectProperty(None)
    widget_width = NumericProperty(0)
    widget_height = NumericProperty(0)
    widget_center_x = NumericProperty(0)
    widget_center_y = NumericProperty(0)

    # Mapping parameters
    bus_top = NumericProperty(0)
    bus_left = NumericProperty(0)
    bus_bottom = NumericProperty(0)
    bus_right = NumericProperty(0)
    boundary_top = NumericProperty(0)
    boundary_left = NumericProperty(0)
    boundary_bottom = NumericProperty(0)
    boundary_right = NumericProperty(0)

    # object coordinates
    bottom_coord_in = ListProperty([])
    top_coord_in = ListProperty([])
    right_coord_in = ListProperty([])
    left_coord_in = ListProperty([])
    bottom_coord_out = ListProperty([])
    top_coord_out = ListProperty([])
    right_coord_out = ListProperty([])
    left_coord_out = ListProperty([])
    danger_coord = ListProperty([])
    safe_coord = ListProperty([])

    dy = NumericProperty(0)
    dx = NumericProperty(0)
    object_size = NumericProperty(55.0)
    top_offset = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CanvasDrawing, self).__init__(**kwargs)
        self.pos_factors_x = [.1, .2, .25, .3]
        self.pos_factors_y = [.2, .3, .4, .45, .5]
        self.colors = ((1, 0, 0, .9), (0, 1, 0, .9))
        # self.create_coord()
        # self.timer = 0
        # self.add_object_now = False
        # self.draw_rec()
        Clock.schedule_interval(self.update_canvas, timeout=10)
        # anim = Animation(rgba=(1, 0, 0, 1)) + Animation(rgba=(0, 1, 0, 1)) + Animation(rgba=(0, 0, 1, 1))
        # anim.repeat = True
        # anim.start

    def create_coord(self):
        # Coordinates in the danger region
        vert_points_entire = [i for i in range(round(self.boundary_bottom) + 20, round(self.boundary_top), 60) if
                              self.boundary_top - i >= 60]
        hor_points_entire = [i for i in range(round(self.boundary_left) + 60, round(self.boundary_right), 60) if
                             self.boundary_right - i >= 5]
        top_vert_points = [i for i in range(round(self.boundary_top) - 60, round(self.bus_top), -60) if
                           i - self.bus_top >= 5]
        bottom_vert_points = [i for i in vert_points_entire if i <= self.bus_bottom]
        bus_width_hor_points = [i for i in hor_points_entire if self.bus_left < i < self.bus_right]
        left_hor_points = [i for i in hor_points_entire if i <= self.bus_left]
        right_hor_points = [i for i in range(round(self.boundary_right) - 2, round(self.bus_right), -60) if
                            i - self.bus_right >= 60]
        self.left_coord_in = [(i, j) for i in left_hor_points for j in vert_points_entire]
        self.right_coord_in = [(i, j) for i in right_hor_points for j in vert_points_entire]
        self.top_coord_in = [(i, j) for i in bus_width_hor_points for j in top_vert_points]
        self.bottom_coord_in = [(i, j) for i in bus_width_hor_points for j in bottom_vert_points]

        # Coordinates in the safe region
        vert_points_entire = [i for i in range(round(self.top - self.widget_height) + 20, round(self.top), 60) if
                              self.top - i >= 60]
        hor_points_entire = [i for i in range(round(self.right - self.widget_width) + 60, round(self.right), 60) if
                             self.right - i >= 20]
        top_vert_points = [i for i in range(round(self.top) - 60, round(self.boundary_top), -60) if
                           i - self.boundary_top >= 10]
        bottom_vert_points = [i for i in vert_points_entire if i <= self.boundary_bottom]
        bus_width_hor_points = [i for i in hor_points_entire if self.boundary_left < i < self.boundary_right]
        left_hor_points = [i for i in hor_points_entire if i <= self.boundary_left]
        right_hor_points = [i for i in range(round(self.right) - 10, round(self.boundary_right), -60) if
                            i - self.boundary_right >= 60]
        self.left_coord_out = [(i, j) for i in left_hor_points for j in vert_points_entire]
        self.right_coord_out = [(i, j) for i in right_hor_points for j in vert_points_entire]
        self.top_coord_out = [(i, j) for i in bus_width_hor_points for j in top_vert_points]
        self.bottom_coord_out = [(i, j) for i in bus_width_hor_points for j in bottom_vert_points]

        self.danger_coord = [j for i in
                             (self.left_coord_in, self.right_coord_in, self.top_coord_in, self.bottom_coord_in) for j in
                             i]
        self.safe_coord = [j for i in
                           (self.left_coord_out, self.right_coord_out, self.top_coord_out, self.bottom_coord_out) for
                           j in i]

    def update_canvas(self, *args):
        if len(self.safe_coord) == 0:
            self.create_coord()

        if self.monitor_screen.number_of_detected_objects % 2 == 0:
            self.add_object(kind='car', pos_factor=1, color=self.colors[0])
        else:
            self.add_object(kind='car',
                            pos_factor=(random.choice(self.pos_factors_x), random.choice(self.pos_factors_y)),
                            color=self.colors[1])

    def add_object(self, kind, pos_factor, color):
        """
        :param color: a tuple of the color proportions
        :param pos_factor: a numeric value used for computing the position
        :param kind: string options, one of ['car', 'motorbike', 'human-handsdown', 'bike-fast']
        :return:
        """
        if pos_factor == 1:
            coord = random.choice(self.safe_coord)
            center = coord
        else:
            center = random.choice(self.danger_coord)
        obj = MDIconButton(icon=kind, center=center, user_font_size="32sp", theme_text_color="Custom", text_color=color)

        if kind not in self.monitor_screen.detected_objects:
            self.monitor_screen.detected_objects.append(kind)
        self.monitor_screen.number_of_detected_objects += 1
        self.add_widget(obj)


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

        screen = Builder.load_file('BSDS.kv')

        return screen


if __name__ == '__main__':
    BSDSApp().run()
