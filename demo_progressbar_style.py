#  Copyright (c) 2024. Charles Hymes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import gi
import logging
import sys
gi.require_version('Gtk', '3.0')  # noqa: E402
from gi.repository import Gtk, GLib, Gdk
from gi.repository.Gtk import Box, CheckButton, ProgressBar

print(f"Gtk Version Information: major:{Gtk.MAJOR_VERSION}, minor:{Gtk.MINOR_VERSION}, micro: {Gtk.MICRO_VERSION}")

PB_NAME_CORRECT = "progressbar_demo_css"
PB_NAME_WRONG = "zaphod_bacardi"


def new_progressbar_css_bytes(widget: Gtk.Widget) -> bytes:
    widget_name: str = widget.get_name()
    if widget_name is None:
        raise ValueError("Widget does not have a name")
    if not widget_name.strip():
        raise ValueError("Widget name cannot be empty nor whitespace.")

    # css code from
    # https://stackoverflow.com/questions/48097764/gtkprogressbar-with-css-for-progress-colour-not-functioning
    css_string = (f"""
    progressbar#{widget_name} text {{
        color: DarkOrange;
        font-weight: bold;
    }}
    progressbar#{widget_name} > trough > progress {{
      background-image: none;
      background-color: fuchsia;
    }}
    progressbar#{widget_name} progress{{
        background-image: linear-gradient(90deg, yellow, red);
        background-color: blue;
    }}
    """)
    return css_string.encode('utf-8')


def install_css_styles(style_bytes: bytes):
    if style_bytes is None:
        raise ValueError("style_bytes cannot be None.")
    try:
        style_provider = Gtk.CssProvider().new()
        # Verified in
        # https://lazka.github.io/pgi-docs/Gtk-3.0/classes/StyleContext.html#Gtk.StyleContext.add_provider_for_screen
        # and
        # https://lazka.github.io/pgi-docs/Gdk-3.0/classes/Screen.html#Gdk.Screen
        Gtk.StyleContext.add_provider_for_screen( # noqa
            Gdk.Screen.get_default(),  # noqa
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        style_provider.load_from_data(style_bytes)  # noqa
    except Exception as problem:
        logging.exception(problem)


class ProgressBarWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="ProgressBar Demo")
        self.set_border_width(10)  # noqa

        vbox: Box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)  # noqa

        self.progressbar: ProgressBar = Gtk.ProgressBar()
        self.progressbar.set_name(PB_NAME_CORRECT)
        vbox.pack_start(self.progressbar, True, True, 0)

        button: CheckButton = Gtk.CheckButton(label="Show text")
        button.connect("toggled", self.on_show_text_toggled)
        vbox.pack_start(button, True, True, 0)

        button: CheckButton = Gtk.CheckButton(label="Activity mode")
        button.connect("toggled", self.on_activity_mode_toggled)
        vbox.pack_start(button, True, True, 0)

        button: CheckButton = Gtk.CheckButton(label="Right to Left")
        button.connect("toggled", self.on_right_to_left_toggled)
        vbox.pack_start(button, True, True, 0)

        self.timeout_id = GLib.timeout_add(50, self.on_timeout, None)
        self.activity_mode = False

        progressbar_style_bytes: bytes = new_progressbar_css_bytes(widget=self.progressbar)
        install_css_styles(style_bytes=progressbar_style_bytes)

    def on_show_text_toggled(self, button):
        show_text = button.get_active()
        if show_text:
            text = "some text"
        else:
            text = None
        self.progressbar.set_text(text)
        self.progressbar.set_show_text(show_text)

    def on_activity_mode_toggled(self, button):
        self.activity_mode = button.get_active()
        if self.activity_mode:
            self.progressbar.pulse()
        else:
            self.progressbar.set_fraction(0.0)

    def on_right_to_left_toggled(self, button):
        value = button.get_active()
        self.progressbar.set_inverted(value)

    # noinspection PyUnusedLocal
    def on_timeout(self, user_data):
        """
        Update value on the progress bar
        """
        if self.activity_mode:
            self.progressbar.pulse()
        else:
            new_value = self.progressbar.get_fraction() + 0.01
            if new_value > 1:
                new_value = 0
            self.progressbar.set_fraction(new_value)
        # As this is a timeout function, return True so that it
        # continues to get called
        return True


def main() -> int:
    try:
        win = ProgressBarWindow()
        win.connect("destroy", Gtk.main_quit)  # noqa
        win.show_all()  # noqa
        Gtk.main()  # noqa
    except Exception as an_exception:
        logging.exception(an_exception)
        return -1
    return 0


if __name__ == '__main__':
    sys.exit(main())
