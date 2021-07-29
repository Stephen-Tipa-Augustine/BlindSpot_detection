# imports
import random
import threading

from kivymd.uix.button import MDIconButton

from BSDS_firmware.blink_led import BlinkLED
from BSDS_firmware.distant_manager import DistantManager
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from BSDS_firmware.helpers import ThreadManager

# definition of constants
from BSDS_firmware.distant_manager import REFERENCE_DISTANCE, MAXIMUM_DISTANCE, DRIFT


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
        self.object_kind = {'car': 'Car', 'motorbike': 'Bike', 'human-handsdown': 'human',
                            'shield-alert-outline': 'Unknown'}

        # initializing sensors
        self.left_led = None
        self.right_led = None
        self.distant_manager = None

        self.left_sensor_value = None
        self.rear_sensor_value = None
        self.right_sensor_value = None
        self.front_sensor_value = None

        self.danger_zone_positions = []
        self.coord_matrix = None

        self.initialize_sensors()

        Clock.schedule_interval(self.update_canvas, timeout=10)
        Clock.schedule_interval(self._blink_right_led, timeout=.5)
        Clock.schedule_interval(self._blink_left_led, timeout=.5)
        # anim = Animation(rgba=(1, 0, 0, 1)) + Animation(rgba=(0, 1, 0, 1)) + Animation(rgba=(0, 0, 1, 1))
        # anim.repeat = True
        # anim.start

    def initialize_sensors(self):
        self.distant_manager = DistantManager()
        # self.left_led = BlinkLED()
        # self.right_led = BlinkLED()

    def blink_led(self, *args):
        Clock.schedule_interval(self._blink_right_led, timeout=2)
        Clock.schedule_interval(self._blink_left_led, timeout=2)

    def _blink_left_led(self, dt):
        if not self.monitor_screen.system_status:
            return False
        if self.monitor_screen is None:
            return
        if 'Left' in self.danger_zone_positions:
            print('Blinking left LED')
            try:
                self.left_led.run(delay=2)
            except ImportError:
                print('Failed to import modules')
        elif self.left_led is not None and 'Left' not in self.danger_zone_positions:
            self.left_led.stop()

    def _blink_right_led(self, dt):
        if not self.monitor_screen.system_status:
            return False
        if self.monitor_screen is None:
            return
        if 'Right' in self.danger_zone_positions:
            print('Blinking right LED')
            try:
                self.right_led.run(delay=2)
            except ImportError:
                print('Failed to import modules')
        elif self.right_led is not None and 'Right' not in self.danger_zone_positions:
            self.right_led.stop()

    def get_distance(self):
        return self._coord_mapper(self.distant_manager.run())

    def _coord_mapper(self, data):
        point = None
        for i in data:
            if data[i]:
                if i == 'left':
                    if self.left_sensor_value:
                        if self.is_another_object(self.left_sensor_value[0], data['left'][0]):
                            self.left_sensor_value = data['left']
                            point = self._coord_translator(data['left'], 'left')
                    else:
                        self.left_sensor_value = data['left']
                        point = self._coord_translator(data['left'], 'left')
                elif i == 'bottom':
                    if self.rear_sensor_value:
                        if self.is_another_object(self.rear_sensor_value[0], data['bottom'][0]):
                            self.rear_sensor_value = data['bottom']
                            point = self._coord_translator(data['bottom'], 'bottom')
                    else:
                        self.rear_sensor_value = data['bottom']
                        point = self._coord_translator(data['bottom'], 'bottom')
                elif i == 'right':
                    if self.right_sensor_value:
                        if self.is_another_object(self.right_sensor_value[0], data['right'][0]):
                            self.right_sensor_value = data['right']
                            point = self._coord_translator(data['right'], 'right')
                    else:
                        self.right_sensor_value = data['right']
                        point = self._coord_translator(data['right'], 'right')
                elif i == 'top':
                    if self.front_sensor_value:
                        if self.is_another_object(self.front_sensor_value[0], data['top'][0]):
                            self.front_sensor_value = data['top']
                            point = self._coord_translator(data['top'], 'top')
                    else:
                        self.front_sensor_value = data['top']
                        point = self._coord_translator(data['top'], 'top')

        return point

    @staticmethod
    def is_another_object(value1, value2):
        if value1 is None or value2 is None:
            return True
        else:
            return True if abs(value2 - value1) <= DRIFT else False

    def _coord_translator(self, coord, orientation='left'):
        point = None
        if orientation == 'left' and coord[1] == 'in':
            r, c = self.coord_matrix['left_in']
            point = self._pixels_from_matrix((r, c), coord, self.left_coord_in)
        elif orientation == 'left' and coord[1] == 'out':
            r, c = self.coord_matrix['left_out']
            point = self._pixels_from_matrix((r, c), coord, self.left_coord_out)
        elif orientation == 'bottom' and coord[1] == 'in':
            r, c = self.coord_matrix['bottom_in']
            point = self._pixels_from_matrix((r, c), coord, self.bottom_coord_in)
        elif orientation == 'bottom' and coord[1] == 'out':
            r, c = self.coord_matrix['bottom_out']
            point = self._pixels_from_matrix((r, c), coord, self.bottom_coord_out)
        elif orientation == 'right' and coord[1] == 'in':
            r, c = self.coord_matrix['right_in']
            point = self._pixels_from_matrix((r, c), coord, self.right_coord_in)
        elif orientation == 'right' and coord[1] == 'out':
            r, c = self.coord_matrix['right_out']
            point = self._pixels_from_matrix((r, c), coord, self.right_coord_out)
        elif orientation == 'top' and coord[1] == 'in':
            r, c = self.coord_matrix['top_in']
            point = self._pixels_from_matrix((r, c), coord, self.top_coord_in)
        elif orientation == 'top' and coord[1] == 'out':
            r, c = self.coord_matrix['top_out']
            point = self._pixels_from_matrix((r, c), coord, self.top_coord_out)
        return point

    def _generate_coord_matrix(self):
        return {'left_in': self._get_rows_n_columns(data=self.left_coord_in),
                'bottom_in': self._get_rows_n_columns(data=self.bottom_coord_in),
                'right_in': self._get_rows_n_columns(data=self.right_coord_in),
                'top_in': self._get_rows_n_columns(data=self.top_coord_in),
                'left_out': self._get_rows_n_columns(data=self.left_coord_out),
                'bottom_out': self._get_rows_n_columns(data=self.bottom_coord_out),
                'right_out': self._get_rows_n_columns(data=self.right_coord_out),
                'top_out': self._get_rows_n_columns(data=self.top_coord_out)
                }

    def _pixels_from_matrix(self, matrix, coord, data):
        r, c = matrix
        estimates = [i * int(REFERENCE_DISTANCE / c) + int(REFERENCE_DISTANCE / c) for i in range(c)]
        expected_column = 0
        drift = abs(coord[0] - estimates[0])
        for i in estimates:
            if abs(i - coord[0]) < drift:
                drift = abs(i - coord[0])
                expected_column = estimates.index(i)
        return self._get_rows_n_columns_rev((random.choice([i for i in range(r)]), expected_column), data)

    @staticmethod
    def _get_rows_n_columns_rev(matrix, data):
        return data[matrix[0]]

    @staticmethod
    def _get_rows_n_columns(data):
        r = 0
        c = 0
        if len(data) == 0:
            return r, c
        initial_row = data[0][0]
        initial_column = data[0][1]
        for i in data:
            if i[0] == initial_row and r == 0:
                r = 1
            if i[0] != initial_row:
                r += 1
                initial_row = i[0]

            if i[1] == initial_column and c == 0:
                c = 1
            if i[1] != initial_column:
                c += 1
                initial_column = i[1]
        return r, c

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
            # creat coordinate matrix
            self.coord_matrix = self._generate_coord_matrix()

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
        :param kind: string options, one of ['car', 'motorbike', 'human-handsdown', 'bike-fast', 'shield-alert-outline']
        :return:
        """

        m = ThreadManager()
        t = threading.Thread(target=lambda q: q.put(self.get_distance()), args=(m.que, ))
        t.start()
        m.add_thread(t)
        m.join_threads()
        print("The measured distance is: ", m.check_for_return_value())

        if pos_factor == 1:
            coord = random.choice(self.safe_coord)
            center = coord
        else:
            center = random.choice(self.danger_coord)
        obj = MDIconButton(icon=kind, center=center, user_font_size="32sp", theme_text_color="Custom", text_color=color)

        if self.object_kind[kind] not in self.monitor_screen.detected_objects:
            self.monitor_screen.detected_objects.append(self.object_kind[kind])

        object_info = self.get_object_location(center)
        if object_info['location'] not in self.monitor_screen.position_of_detected_objects:
            self.monitor_screen.position_of_detected_objects.append(object_info['location'])
            if object_info['in-danger-zone']:
                self.danger_zone_positions.append(object_info['location'])

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
        in_danger_zone = True if coord in self.danger_coord else False
        return {'location': location, 'in-danger-zone': in_danger_zone}
