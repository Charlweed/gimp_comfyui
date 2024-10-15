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
import time
import zlib
gi.require_version('Gimp', '3.0')  # noqa: E402
gi.require_version('GimpUi', '3.0')  # noqa: E402
gi.require_version("Gtk", "3.0")  # noqa: E402
gi.require_version("Gegl", "0.4")  # noqa: E402
from abc import ABC, abstractmethod
from enum import Enum, auto
from gi.repository import  Gegl, Gio, Gimp, GimpUi,Gtk, GLib, GObject  # noqa
from typing import Dict, Set, Callable
from utilities.babl_gegl_utils import drawable_bytes
from utilities.sd_gui_utils import open_dialog_daemon, close_window_of_widget

# See https://stackoverflow.com/questions/21150914/python-gtk-3-safe-threading

# Constants
LOGGER_CONCURRENCY = logging.getLogger("DrawableChangeNotifier")
LOGGER_CONCURRENCY_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
POLL_FREQUENCY_MS: int = 2000
SLEEP_DURATION_SEC: float = 2.0


def drawable_crc(drawable_in: Gimp.Drawable) -> int:
    return zlib.crc32(drawable_bytes(drawable_in=drawable_in))


def init_logging(level: int):
    LOGGER_CONCURRENCY.setLevel(level)
    logging.basicConfig(format=LOGGER_CONCURRENCY_FORMAT, level=level)


class DrawableChangeListener(ABC):

    @abstractmethod
    def drawable_changed(self, drawable: Gimp.Drawable):
        pass


class NotifierLoopState(Enum):
    LOOPING = auto()
    HALTED = auto()
    TIMEOUT = auto()
    ERROR = auto()
    UNINITIALIZED = auto()

    def continuing_state(self):
        # LOGGER_CONCURRENCY.info(f"{self}")
        if self == NotifierLoopState.LOOPING:
            return True
        # LOGGER_CONCURRENCY.info(f"returning false.")
        return False

    def halting_state(self):
        return not self.continuing_state()


class DefaultDrawableChangeListener(DrawableChangeListener):
    """
    GIMP plug-in procedures are started in a different thread than then main GIMP loop.
    It appears that when a procedure exits, *some* threads forked from the procedure are killed.
    This makes it complicated to start any additional daemon threads, so for now, do not try.
    Instead, do all work in a loop in the plug-in's single thread, EXCEPT processing signals from GUI elements.
    In other words, launch a non-blocking dialog, and exit the plug-in when the work is finished, or appropriate signals
    are received from the dialog.
    """
    def drawable_changed(self, drawable: Gimp.Drawable):
        """
        A stub method that logs the drawable's id to the console.
        :param drawable:
        :return:
        """
        d_id = drawable.get_id()
        change_message: str = f"Drawable {d_id} changed"
        LOGGER_CONCURRENCY.info(change_message)


class DrawableChangeNotifier:
    GIMP_PLUGIN_THREAD_NAME = "MainThread"
    """
    Maintains a Set of drawable_ids and listeners. Every POLL_FREQUENCY_MS it checks to see if the Drawable has changed 
    since the last time it checked. If a Drawable has changed, it notifies each listener that the Drawable changed.
    This implementation does minimal locking, and is therefor subject to races between threads that add & remove, and
    the sending of notifications.
    """

    def __init__(self, dialog_customizer: Callable[[Gtk.Dialog, ], None] | None = None):
        self._id_drawable_map: Dict[int, Gimp.Drawable] = {}
        self._id_crc_map: Dict[int, int] = {}
        self._drawable_change_listeners: Set[DrawableChangeListener] = set()
        self._current_time = 0.0
        self._explicit_halt: bool = False
        self._start_time = 0.0
        self._state: NotifierLoopState = NotifierLoopState.UNINITIALIZED
        self._total_elapsed = 0.0
        self._sleep_duration_sec: float = float(SLEEP_DURATION_SEC)
        self._default_drawable_change_listener: DrawableChangeListener = DefaultDrawableChangeListener()
        self._dialog_customizer: Callable[[Gtk.Dialog, ], None] | None = dialog_customizer

    @property
    def default_drawable_change_notifier(self) -> DrawableChangeListener:
        return self._default_drawable_change_listener

    def add_drawable(self, drawable: Gimp.Drawable):
        d_id: int = drawable.get_id()
        self._id_drawable_map[d_id] = drawable
        d_crc: int = drawable_crc(drawable_in=drawable)
        self._id_crc_map[d_id] = d_crc

    def add_drawable_listener(self, listener: DrawableChangeListener):
        if listener not in self._drawable_change_listeners:
            self._drawable_change_listeners.add(listener)

    def track_drawables(self, drawables: Set[Gimp.Drawable], listener: DrawableChangeListener):
        for drawable in drawables:
            self.add_drawable(drawable=drawable)
        self.add_drawable_listener(listener=listener)
        self.watch_drawables()

    def remove_drawable(self, drawable: Gimp.Drawable):
        self.remove_by_id(drawable.get_id())

    def remove_by_id(self, d_id: int):
        self._id_drawable_map.pop(d_id, None)
        self._id_crc_map.pop(d_id, None)

    def remove_drawable_listener(self, listener: DrawableChangeListener):
        self._drawable_change_listeners.discard(listener)

    def _carry_on(self):
        # LOGGER_CONCURRENCY.info("Carry on check")
        if not self._explicit_halt:
            # LOGGER_CONCURRENCY.info("... not explicit halt")
            if self._state.continuing_state():
                # LOGGER_CONCURRENCY.info("... continuing ...")
                return True
            else:
                # LOGGER_CONCURRENCY.info("self._state.continuing_state() false, implies halt.")
                return False
        else:
            # LOGGER_CONCURRENCY.info("Explicitly halted.")
            self._state = NotifierLoopState.HALTED
            return False

    def _execution_loop(self):
        doomed: Set[int] = set()
        # LOGGER_CONCURRENCY.info("__execution_loop(): Entering outer loop.")
        while self._carry_on():
            # LOGGER_CONCURRENCY.info("Top of loop.")
            self._current_time = time.time_ns()
            # LOGGER_CONCURRENCY.info(f"self._current_time = {self._current_time}")
            self._total_elapsed = self._current_time - self._start_time
            # LOGGER_CONCURRENCY.info(f"self._total_elapsed = {self._total_elapsed}")
            if self._explicit_halt:
                self._state = NotifierLoopState.HALTED
                # LOGGER_CONCURRENCY.info("Explicit halt, breaking loop")
                break  # exit outer loop
            else:
                for d_id, drawable in self._id_drawable_map.items():
                    # LOGGER_CONCURRENCY.info("Looping through items of self._id_drawable_map.")
                    if not Gimp.Drawable.id_is_valid(d_id):
                        LOGGER_CONCURRENCY.info("Found invalid drawable, removing from iteration list.")
                        doomed.add(d_id)
                        continue
                    # calculate crc, compare new crc to previous, if different, fire message via
                    # LOGGER_CONCURRENCY.info(f"Calculating CRC for {d_id}")
                    new_crc = drawable_crc(drawable)
                    # LOGGER_CONCURRENCY.info(f"CRC for {d_id} is {new_crc}")
                    if d_id not in self._id_crc_map:
                        fail_msg = f"Key error:{d_id} not in self._id_crc_map"
                        LOGGER_CONCURRENCY.error(fail_msg)
                        raise KeyError(fail_msg)
                    old_crc = self._id_crc_map[d_id]
                    if old_crc != new_crc:
                        # LOGGER_CONCURRENCY.info(f"Drawable {d_id} changed")
                        listener: DrawableChangeListener
                        for listener in self._drawable_change_listeners:
                            try:
                                listener.drawable_changed(drawable)
                            except Exception as e_except:
                                LOGGER_CONCURRENCY.exception(e_except)
                        self._id_crc_map[d_id] = new_crc
                    else:
                        # LOGGER_CONCURRENCY.info(f"Drawable{d_id} unchanged")
                        pass
                for missing in doomed:
                    self.remove_by_id(missing)
                # LOGGER_CONCURRENCY.info(f"Loop body completed, calling sleep {self._sleep_duration_sec} on condition")
                time.sleep(self._sleep_duration_sec)
                # LOGGER_CONCURRENCY.info("sleep() returned.")
                # LOGGER_CONCURRENCY.info(f"Bottom of loop.")

    def watch_drawables(self):
        self._start_time = time.time_ns() 
        self._current_time = time.time_ns()
        open_dialog_daemon(title_in="Layer ⮕ ComfyUI connection",
                           blurb_in="Click \"Stop Following\" to stop following layer in ComfyUI.",
                           main_button_label="Stop Following",
                           ok_handler=self.halt,  # This function must call close_window_of_widget(source)
                           dialog_populator=self._dialog_customizer
                           )

        self._state = NotifierLoopState.LOOPING
        try:
            self._execution_loop()
        except Exception as invocation_error:  # This does not work, some errors cannot be caught by GIMP plugins.
            exc_info = sys.exc_info()
            fail_message = "An error occurred running the execution loop."
            LOGGER_CONCURRENCY.error(fail_message)
            LOGGER_CONCURRENCY.error(str(invocation_error))
            LOGGER_CONCURRENCY.exception(*exc_info)
            del exc_info

    def halt(self, source: Gtk.Widget, data=None):  # noqa
        """
        Stops Drawable monitor, and calls close_window_of_widget(source)
        :param source: A button in the daemon dialog.
        :param data: Ignored.
        :return: None
        """
        self._state = NotifierLoopState.HALTED
        self._explicit_halt = True
        close_window_of_widget(source)


def main() -> int:
    init_logging(logging.DEBUG)
    notifier_instance: DrawableChangeNotifier = DrawableChangeNotifier()
    notifier_instance.watch_drawables()
    return 0


if __name__ == '__main__':
    sys.exit(main())
