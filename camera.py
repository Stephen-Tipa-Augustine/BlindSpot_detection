import threading

from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Ellipse
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
import time

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.camera import Camera as CoreCamera
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, StringProperty

# Camera handler
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatterlayout import ScatterLayout

core_camera = None


class MyCamera(AnchorLayout):
    camera_name = StringProperty('')
    webcam_started = BooleanProperty(defaultvalue=False)

    def __init__(self, **kwargs):
        super(MyCamera, self).__init__(**kwargs)
        self.camera = None
        threading.Thread(target=self.create_camera, daemon=True).start()

    def create_camera(self):
        self.camera = MyCamera2(resolution=(1920, 768), allow_stretch=True, size_hint=(1, 1))
        self.webcam_started = True
        self.add_widget(self.camera)
        self.play()

    def play(self):
        self.camera.play = True

    def stop(self):
        self.camera.play = False

    def switch_to_main(self):
        print('{} Camera'.format(self.camera_name))

    def capture(self):
        """
        Function to capture the images and give them the names
        according to their captured time and date.
        """
        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")


class MyCamera2(Image):
    """Camera class. See module documentation for more information.
    """

    play = BooleanProperty(True)
    '''Boolean indicating whether the camera is playing or not.
    You can start/stop the camera by setting this property::
        # start the camera playing at creation (default)
        cam = Camera(play=True)
        # create the camera, and start later
        cam = Camera(play=False)
        # and later
        cam.play = True
    :attr:`play` is a :class:`~kivy.properties.BooleanProperty` and defaults to
    True.
    '''

    index = NumericProperty(-1)
    '''Index of the used camera, starting from 0.
    :attr:`index` is a :class:`~kivy.properties.NumericProperty` and defaults
    to -1 to allow auto selection.
    '''

    resolution = ListProperty([-1, -1])
    '''Preferred resolution to use when invoking the camera. If you are using
    [-1, -1], the resolution will be the default one::
        # create a camera object with the best image available
        cam = Camera()
        # create a camera object with an image of 320x240 if possible
        cam = Camera(resolution=(320, 240))
    .. warning::
        Depending on the implementation, the camera may not respect this
        property.
    :attr:`resolution` is a :class:`~kivy.properties.ListProperty` and defaults
    to [-1, -1].
    '''


    def __init__(self, **kwargs):
        super(MyCamera2, self).__init__(**kwargs)  # `MyCamera2` instead of `Camera`
        self._camera = None
        if self.index == -1:
            self.index = 0
        on_index = self._on_index
        fbind = self.fbind
        fbind('index', on_index)
        fbind('resolution', on_index)
        on_index()
        # self.add_widget(Button(text='Click'))

    def on_tex(self, *l):
        self.canvas.ask_update()

    def _on_index(self, *largs):
        global core_camera
        self._camera = None
        if self.index < 0:
            return
        if self.resolution[0] < 0 or self.resolution[1] < 0:
            return
        # access to camera
        while core_camera is None:
            time.sleep(2)
        self._camera = core_camera

        self._camera.bind(on_load=self._camera_loaded)
        if self.play:
            self._camera.start()
            self._camera.bind(on_texture=self.on_tex)

    def _camera_loaded(self, *largs):
        self.texture = self._camera.texture
        self.texture_size = list(self.texture.size)

    def on_play(self, instance, value):
        if not self._camera:
            return
        if value:
            self._camera.start()
        else:
            self._camera.stop()

    @staticmethod
    def access_camera():
        global core_camera
        core_camera = CoreCamera(index=0, resolution=(1920, 768), stopped=True)


threading.Thread(target=MyCamera2.access_camera, daemon=True).start()
