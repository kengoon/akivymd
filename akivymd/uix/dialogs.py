from kivy.lang.builder import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty, OptionProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window, WindowBase
from kivy.animation import Animation
from kivy.uix.modalview import ModalView

from kivymd.theming import ThemableBehavior
from kivymd.uix.dialog import BaseDialog
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.app import MDApp

Builder.load_string(
    """
#:import images_path kivymd.images_path
#:import md_icons kivymd.icon_definitions.md_icons

<AKAlertDialog>:
    auto_dismiss: False
    size_hint: None , None
    background: '%s/transparent.png'%images_path
    background_color: 0,0,0,0
    elevation: 10
    size: root.size_portrait if root._orientation == 'portrait'\
        else root.size_landscape


    BoxLayout:

        orientation: 'vertical' if root._orientation == 'portrait' \
            else 'horizontal'

        canvas.before:
            Color:
                rgba: root.bg_color if root.bg_color else root.theme_cls.bg_normal
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [root.radius,]

        canvas.after:
            Color:
                rgba: root.progress_color if root.progress_color else root.theme_cls.primary_dark
            RoundedRectangle:
                pos: self.pos[0] + root.radius , self.pos[1] + root.height - root.progress_width
                size: root._progress_value , root.progress_width
                radius: [root.progress_width/2,]

        BoxLayout:
            size_hint_y: None if root._orientation == 'portrait' \
                else 1

            size_hint_x: None if root._orientation == 'landscape' \
                else 1

            size: (root.width, root.header_height_portrait) if root._orientation == 'portrait' \
                else (root.header_width_landscape , root.height)

            canvas.before:
                Color:
                    rgba: root.header_bg if root.header_bg else root.theme_cls.primary_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [root.radius, root.radius, 0, 0] if root._orientation == 'portrait' \
                        else [root.radius, 0, 0, root.radius]

            MDLabel:
                font_style: "Icon" if root.header_text_type=='icon' else "Body1"
                bold: True
                text: u"{}".format(md_icons[root.header_icon]) if root.header_text_type=='icon' else root.header_text
                theme_text_color: 'Custom'
                text_color: root.header_color if root.header_color else [1,1,1,1]
                valign: root.header_v_pos
                halign: root.header_h_pos
                font_size: root.header_font_size

        BoxLayout:
            id: content


    """
)


class AKAlertDialog(RectangularElevationBehavior, BaseDialog):
    radius = NumericProperty('10dp')
    bg_color = ListProperty()
    size_portrait = ListProperty(['250dp', '350dp'])
    size_landscape = ListProperty(['400dp', '250dp'])
    header_width_landscape = NumericProperty('110dp')
    header_height_portrait = NumericProperty('110dp')
    fixed_orientation = OptionProperty(None, options=['portrait', 'landscape'])
    header_bg = ListProperty()
    header_text_type = OptionProperty('icon', options=['icon', 'text'])
    header_text = StringProperty()
    header_icon = StringProperty('android')
    header_color = ListProperty()
    header_h_pos = StringProperty('center')
    header_v_pos = StringProperty('center')
    header_font_size = NumericProperty('55dp')
    progress_interval = NumericProperty(None)
    progress_width = NumericProperty('2dp')
    progress_color = ListProperty()
    content_cls = ObjectProperty()
    opening_duration = NumericProperty(0.2)
    dismiss_duration = NumericProperty(0.2)

    _orientation = StringProperty()
    _progress_value = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self._get_orientation)
        self.register_event_type('on_progress_finish')
        Clock.schedule_once(self._update)
        Window.bind(on_touch_down=self._window_touch_down)

    def _update(self, *args):
        self._get_orientation()

    def on_touch_down(self, touch):
        MDApp.get_running_app().root.dispatch('on_touch_down', touch)
        return super().on_touch_down(touch)

    def _window_touch_down(self, instance, touch):
        self.dispatch('on_touch_down', touch)

    def _get_orientation(self, *args):
        if self.fixed_orientation:
            self._orientation = self.fixed_orientation
        elif self.theme_cls.device_orientation == 'portrait':
            self._orientation = 'portrait'
        else:
            self._orientation = 'landscape'

    def on_content_cls(self, *args):
        if not self.content_cls:
            return

        self.ids.content.clear_widgets()
        self.ids.content.add_widget(self.content_cls)

    def on_open(self):
        self._start_progress()
        return super().on_open()

    def on_pre_open(self):
        self._opening_animation()
        return super().on_pre_open()

    def on_pre_dismiss(self):
        self._dismiss_animation()
        return super().on_pre_dismiss()

    def _opening_animation(self):
        self.opacity = 0
        anim = Animation(
            opacity=1, duration=self.opening_duration, t='out_quad')
        anim.start(self)

    def _dismiss_animation(self):
        anim = Animation(
            opacity=0, duration=self.dismiss_duration, t='out_quad')
        anim.start(self)

    def _start_progress(self):
        if not self.progress_interval:
            return
        max_width = self.size[0] - self.radius * 2
        anim = Animation(_progress_value=max_width,
                         duration=self.progress_interval)
        anim.bind(on_complete=lambda x, y: self.dispatch('on_progress_finish'))
        anim.start(self)

    def on_progress_finish(self, *args):
        pass