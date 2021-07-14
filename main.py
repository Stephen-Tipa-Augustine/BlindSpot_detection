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
        self.object_kind = {'car': 'Car', 'motorbike': 'Bike', 'human-handsdown': 'human', 'bike-fast': 'Unknown'}
        Clock.schedule_interval(self.update_canvas, timeout=10)
        Clock.schedule_interval(self._blink_right_led, timeout=.5)
        Clock.schedule_interval(self._blink_left_led, timeout=.5)
        # anim = Animation(rgba=(1, 0, 0, 1)) + Animation(rgba=(0, 1, 0, 1)) + Animation(rgba=(0, 0, 1, 1))
        # anim.repeat = True
        # anim.start

    def blink_led(self, *args):
        Clock.schedule_interval(self._blink_right_led, timeout=.5)
        Clock.schedule_interval(self._blink_left_led, timeout=.5)

    def _blink_left_led(self, dt):
        if not self.monitor_screen.system_status:
            return False
        if self.monitor_screen is None:
            return
        if 'Left' in self.monitor_screen.position_of_detected_objects:
            print('blinking left LED')

    def _blink_right_led(self, dt):
        if not self.monitor_screen.system_status:
            return False
        if self.monitor_screen is None:
            return
        if 'Right' in self.monitor_screen.position_of_detected_objects:
            print('blinking right LED')

    def auditory_feedback(self, *args):
        pass

    def _generate_coord(self, inner=True):
        if inner:
            boundary_top = self.boundary_top
            boundary_bottom = self.boundary_bottom
            boundary_left = self.boundary_left
            boundary_right = self.boundary_right
            inner_top = self.bus_top
            inner_right = self.bus_right
            inner_bottom = self.bus_bottom
            inner_left = self.bus_left
        else:
            boundary_top = self.top
            boundary_bottom = self.top - self.widget_height
            boundary_left = self.right - self.widget_width
            boundary_right = self.right
            inner_top = self.boundary_top
            inner_right = self.boundary_right
            inner_bottom = self.boundary_bottom
            inner_left = self.boundary_left
        vert_points_entire = [i for i in range(round(boundary_bottom) + 60, round(boundary_top), 60) if
                              boundary_top - i >= 60]
        hor_points_entire = [i for i in range(round(boundary_left) + 60, round(boundary_right), 60) if
                             boundary_right - i >= 5]
        top_vert_points = [i for i in range(round(inner_top) + 60, round(boundary_top), 60) if
                           boundary_top - i >= 5]
        bottom_vert_points = [i for i in vert_points_entire if i <= inner_bottom]
        bus_width_hor_points = [i for i in hor_points_entire if inner_left < i < inner_right]
        left_hor_points = [i for i in hor_points_entire if i <= inner_left]
        right_hor_points = [i for i in range(round(boundary_right) - 5, round(inner_right), -60) if
                            i - inner_right >= 60]
        return [(i, j) for i in left_hor_points for j in vert_points_entire], \
               [(i, j) for i in bus_width_hor_points for j in top_vert_points], \
               [(i, j) for i in right_hor_points for j in vert_points_entire], \
               [(i, j) for i in bus_width_hor_points for j in bottom_vert_points]

    def create_coord(self):
        # Coordinates in the danger region
        self.left_coord_in, self.top_coord_in, self.right_coord_in, self.bottom_coord_in = self._generate_coord(True)

        # Coordinates in the safe region
        self.left_coord_out, self.top_coord_out, self.right_coord_out, self.bottom_coord_out = \
            self._generate_coord(False)

        self.danger_coord = [j for i in
                             (self.left_coord_in, self.right_coord_in, self.top_coord_in, self.bottom_coord_in) for j in
                             i]
        self.safe_coord = [j for i in
                           (self.left_coord_out, self.right_coord_out, self.top_coord_out, self.bottom_coord_out) for
                           j in i]

    def update_canvas(self, *args):
        if not self.monitor_screen.system_status:
            return False
        if len(self.safe_coord) == 0:
            self.create_coord()

        if self.monitor_screen.number_of_detected_objects % 2 == 0:
            self.add_object(kind='car', pos_factor=1, color=self.colors[1])
        else:
            self.add_object(kind='car',
                            pos_factor=(random.choice(self.pos_factors_x), random.choice(self.pos_factors_y)),
                            color=self.colors[0])

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

        if self.object_kind[kind] not in self.monitor_screen.detected_objects:
            self.monitor_screen.detected_objects.append(self.object_kind[kind])

        object_location = self.get_object_location(center)
        if object_location not in self.monitor_screen.position_of_detected_objects:
            self.monitor_screen.position_of_detected_objects.append(object_location)

        self.monitor_screen.number_of_detected_objects += 1
        self.add_widget(obj)

    def get_object_location(self, coord):
        if coord in self.left_coord_in or coord in self.left_coord_out:
            location = 'Left'
        elif coord in self.top_coord_in or coord in self.top_coord_out:
            location = 'Top'
        elif coord in self.right_coord_in or coord in self.right_coord_out:
            location = 'Right'
        elif coord in self.bottom_coord_in or coord in self.bottom_coord_out:
            location = 'Bottom'
        else:
            location = 'Unknown'
        return location



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

        screen = Builder.load_file('root.kv')

        return screen


if __name__ == '__main__':
    BSDSApp().run()
