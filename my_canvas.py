# imports
import random
import threading
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from BSDS_firmware.blink_led import BlinkLED
from BSDS_firmware.distant_manager import DistantManager
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, DictProperty
from kivy.clock import Clock
from BSDS_firmware.helpers import ThreadManager
import pygame


# definition of constants
from BSDS_firmware.distant_manager import REFERENCE_DISTANCE


class BlindSpotObject(Widget):

    def __init__(self, kind, coord, color, num_value):
        super(BlindSpotObject, self).__init__()
        obj = MDIconButton(icon=kind, center=coord, user_font_size="40sp",
                           theme_text_color="Custom", text_color=color)
        self.add_widget(obj)

        self.add_widget(MDLabel(text="%.1fm away" % (float(num_value) / 100),
                                theme_text_color="Custom", text_color=(1, 1, 1, 1),
                                center=(obj.center_x + 10, obj.top)))


class CanvasDrawing(Widget):
    monitor_screen = ObjectProperty(None)
    app_window = ObjectProperty()
    object_identity = DictProperty(
    {
            'left': 'shield-alert-outline',
            'bottom': 'shield-alert-outline',
            'right': 'shield-alert-outline',
            'top': 'shield-alert-outline',
        })
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

    # boundary_texture = ObjectProperty(defaultvalue=Image(source="boundary.png").texture)

    def __init__(self, **kwargs):
        super(CanvasDrawing, self).__init__(**kwargs)
        self.pos_factors_x = [.1, .2, .25, .3]
        self.pos_factors_y = [.2, .3, .4, .45, .5]
        self.colors = ((1, 0, 0, .9), (0, 1, 0, .9))
        self.object_kind = {'car': 'Car', 'motorbike': 'Bike', 'human-handsdown': 'Human',
                            'shield-alert-outline': 'Unknown'}
        self.added_objects = {'Top': [], 'Left': [], 'Bottom': [], 'Right': []}
        self.boundary_images = []
        self.boundary_image_index = 0

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

        Clock.schedule_interval(self.update_canvas, timeout=.5)
        Clock.schedule_interval(self._blink_right_led, timeout=.5)
        Clock.schedule_interval(self._blink_left_led, timeout=.5)
        Clock.schedule_interval(self._sound_auditory_alert, timeout=.5)
        Clock.schedule_interval(self.get_objects, 2)

    def initialize_sensors(self):
        self.distant_manager = DistantManager()
        self.left_led = BlinkLED(cathode=5)
        self.right_led = BlinkLED(cathode=6)
        # Loading sound
        pygame.mixer.init()
        pygame.mixer.music.load('assets/BSD_alert.wav')
        # self.right_led = BlinkLED()

    def get_objects(self, *args):
        if not self.app_window.left_object_detector.empty():
            objects = self.app_window.left_object_detector.get(block=False)
            if len(objects) != 0:
                self.object_identity['right'] = objects[0]
            else:
                self.object_identity['right'] = 'shield-alert-outline'

    def _sound_auditory_alert(self, dt):
        if self.monitor_screen is None or not self.monitor_screen.system_status:
            if pygame.mixer.music.get_busy() == 1:
                pygame.mixer.music.stop()
            return False
        if len(self.danger_zone_positions) != 0 and pygame.mixer.music.get_busy() == 0:
            self.auditory_feedback()

        if len(self.danger_zone_positions) == 0 and pygame.mixer.music.get_busy() == 1:
            pygame.mixer.music.stop()

    def _blink_left_led(self, dt=1):
        if self.monitor_screen is None or (self.monitor_screen is not None and not self.monitor_screen.system_status):
            try:
                self.left_led.turn_off()
            except:
                pass
            return False
        if 'Left' in self.danger_zone_positions:
            try:
                self.left_led.run()
                self.auditory_feedback()
            except AttributeError:
                print('Failed to initialize LED')
        elif self.left_led and 'Left' not in self.danger_zone_positions:
            try:
                self.left_led.turn_off()
            except:
                pass

    def _blink_right_led(self, dt):
        if self.monitor_screen is None or (self.monitor_screen is not None and not self.monitor_screen.system_status):
            try:
                self.left_led.turn_off()
                self.auditory_feedback()
            except:
                pass
            return False
        if 'Right' in self.danger_zone_positions:
            try:
                self.right_led.run()
            except AttributeError:
                print('Failed to initialize LED')
        elif self.right_led and 'Right' not in self.danger_zone_positions:
            try:
                self.right_led.turn_off()
            except:
                pass

    def get_distance(self):
        return self._coord_mapper(self.distant_manager.run())

    def _coord_mapper(self, data):
        point = None
        for i in data:
            if data[i]:
                if i == 'left':
                    self.left_sensor_value = data['left']
                    point = self._coord_translator(data['left'], 'left'), data['left'][1], data['left'][0], i
                elif i == 'bottom':
                    self.rear_sensor_value = data['bottom']
                    point = self._coord_translator(data['bottom'], 'bottom'), data['bottom'][1], data['bottom'][0], i
                elif i == 'right':
                    self.right_sensor_value = data['right']
                    point = self._coord_translator(data['right'], 'right'), data['right'][1], data['right'][0], i
                elif i == 'top':
                    self.front_sensor_value = data['top']
                    point = self._coord_translator(data['top'], 'top'), data['top'][1], data['top'][0], i

        return point

    def is_another_object(self, location, sensor_id=''):
        value = False, None, None
        for i in self.added_objects[location]:
            if i['sensor_id'] == sensor_id:
                value = True, self.added_objects[location].index(i), i['ref']
        return value

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

    @staticmethod
    def auditory_feedback():
        pygame.mixer.music.play(loops=-1)
        # pygame.mixer.music.set_volume(.5)

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
            return

        if len(self.safe_coord) == 0:
            self.create_coord()
            # creat coordinate matrix
            self.coord_matrix = self._generate_coord_matrix()

            self.monitor_screen.category_based_numbers = {
                'Car': 0,
                'Bike': 0,
                'Human': 0,
                'Unknown': 0,
            }
            self.monitor_screen.detected_objects = []
            self.monitor_screen.position_of_detected_objects = []
            self.monitor_screen.number_of_detected_objects = 0
            return

        m = ThreadManager()
        t = threading.Thread(target=lambda q: q.put(self.get_distance()), args=(m.que,))
        t.start()
        m.add_thread(t)
        m.join_threads()
        coord = m.check_for_return_value()

        if coord:
            self.add_object(kind=self.object_identity[coord[3]], center=coord[0],
                            color=self.colors[0] if coord[1] == 'in' else self.colors[1],
                            description=coord[1], num_value=coord[2], sensor_id=coord[3])

    def add_object(self, kind, center, color, description='in', sensor_id='left', num_value=None):
        """
        :param num_value:
        :param sensor_id:
        :param description:
        :param center:
        :param color: a tuple of the color proportions
        :param kind: string options, one of ['car', 'motorbike', 'human-handsdown', 'bike-fast', 'shield-alert-outline']
        :return:
        """
        object_info = self.get_object_location(center)
        decision = self.is_another_object(location=object_info['location'], sensor_id=sensor_id)
        if decision[0]:
            self._remove_object(object_info, kind, decision)
        self._add_object(kind, center, color, object_info, description, sensor_id, num_value=num_value)

    def _remove_object(self, object_info, kind, decision):
        orientation_count = 0
        description_count = 0
        kind_count = 0
        for i in self.added_objects[object_info['location']]:
            if i['orientation'] == object_info['location']:
                orientation_count += 1
            if i['description'] == 'in':
                description_count += 1
            if i['kind'] == self.object_kind[kind]:
                kind_count += 1

        if orientation_count == 1 and object_info['location'] in self.monitor_screen.position_of_detected_objects:
            index = self.monitor_screen.position_of_detected_objects.index(object_info['location'])
            del self.monitor_screen.position_of_detected_objects[index]

        if description_count == 1 and object_info['location'] in self.danger_zone_positions:
            index = self.danger_zone_positions.index(object_info['location'])
            del self.danger_zone_positions[index]

        if kind_count == 1 and self.object_kind[kind] in self.monitor_screen.detected_objects:
            index = self.monitor_screen.detected_objects.index(self.object_kind[kind])
            del self.monitor_screen.detected_objects[index]

        if self.added_objects[object_info['location']][decision[1]]:
            del self.added_objects[object_info['location']][decision[1]]

        self.monitor_screen.number_of_detected_objects -= 1
        self.monitor_screen.category_based_numbers[self.object_kind[kind]] -= 1
        self.remove_widget(decision[-1])

    def _add_object(self, kind, center, color, object_info, description, sensor_id, num_value=0):
        obj = BlindSpotObject(kind=kind, coord=center, color=color, num_value=num_value)

        if self.object_kind[kind] not in self.monitor_screen.detected_objects:
            self.monitor_screen.detected_objects.append(self.object_kind[kind])
        if object_info['location'] not in self.monitor_screen.position_of_detected_objects:
            self.monitor_screen.position_of_detected_objects.append(object_info['location'])

        if description == 'in' and object_info['location'] not in self.danger_zone_positions:
            self.danger_zone_positions.append(object_info['location'])

        self.monitor_screen.number_of_detected_objects += 1
        self.monitor_screen.category_based_numbers[self.object_kind[kind]] += 1
        self.add_widget(obj)
        self.added_objects[object_info['location']].append({'ref': obj, 'pos': center,
                                                            'orientation': object_info['location'],
                                                            'description': description,
                                                            'kind': self.object_kind[kind],
                                                            'sensor_id': sensor_id})

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
