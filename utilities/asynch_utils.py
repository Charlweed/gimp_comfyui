#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# The two lines above, the shebang and the encoding hint, are required!
# Otherwise, GIMP for unix-like systems will fail to load this plug-in.
# Also, verify that all plug-in python files have execute permissions.
# 755 or 775 if you're social.
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

import logging
import sys
import threading
import time
from enum import Enum, auto

import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GLib
from typing import Any

LOGGER_FORMAT_AU = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
LOGGER_AU = logging.getLogger("asynch_utils")


class Status(Enum):
    UNFINISHED = auto()
    DONE = auto()
    ERROR = auto()


def gtk_idle_add(func):
    """
    Decorator to run a function in the GTK main loop.
    functions decorated with this will not run if there's no main loop running.
    """

    def wrapper(*args, **kwargs):
        GLib.idle_add(lambda: func(*args, **kwargs))

    return wrapper


def gtk_duty_performer(func):
    """
    Decorator to obtain a value from a function run in the GTK main loop.
    functions decorated with this will block run if there's no main loop running.
    """

    def accessor(reader, *args, **kwargs) -> Any:

        result = [None]
        status: Status = Status.UNFINISHED

        def read():
            nonlocal status
            inner_result = None
            try:
                inner_result = reader(*args, **kwargs)
                status = Status.DONE
            except Exception as read_error:
                LOGGER_AU.exception(read_error)
                status = Status.ERROR
            finally:
                return inner_result

        def idle_callback():
            nonlocal result
            LOGGER_AU.warning("invoking read and assigning whatever to \"result[0]\"")
            result[0] = read()
            if result[0] is None:
                raise ValueError("read returned None")
            else:
                LOGGER_AU.warning("Obtained non-null \"result[0]\" from read()")  # This is the last line seen...
            return False  # Remove idle callback

        GLib.idle_add(idle_callback)

        counter: int = 0
        max_loops: int = 800
        LOGGER_AU.warning("Starting loop waiting on \"result[0]\"")
        sys.stdout.flush()
        sys.stderr.flush()
        while status == Status.UNFINISHED:
            # LOGGER_AU.warning(f" In wait Loop, counter={counter}")
            # noinspection PyUnresolvedReferences
            Gtk.main_iteration_do(False)
            if status != Status.UNFINISHED:
                sys.stdout.flush()
                sys.stderr.flush()
                LOGGER_AU.warning(f"\"result[0]\" not None, breaking loop at {counter}")
                sys.stdout.flush()
                sys.stderr.flush()
                break
            counter += 1
            if counter >= max_loops:
                raise ValueError("Loop count exceeded.")
        LOGGER_AU.warning("accessor() returning \"result[0]\"")
        return result[0]

    def wrapper(*args, **kwargs):
        return accessor(func, *args, **kwargs)

    return wrapper


@gtk_duty_performer
def name_of_widget(some_widget: Gtk.Widget) -> str:
    return some_widget.get_name()


@gtk_idle_add
def print_widget_name(a_widget: Gtk.Widget):
    sys.stdout.flush()
    sys.stderr.flush()
    print(a_widget.get_name())


@gtk_duty_performer
def new_button() -> Gtk.Button:
    sys.stdout.flush()
    sys.stderr.flush()
    LOGGER_AU.warning("Constructing another button")
    fresh_button = Gtk.Button(label="Another button")
    fresh_button.set_name("Sweet Paprika")
    fresh_button.connect("clicked", lambda txt: print(txt))
    return fresh_button


@gtk_idle_add
def insert_button(box: Gtk.Box, another_button: Gtk.Button):
    sys.stdout.flush()
    sys.stderr.flush()
    LOGGER_AU.warning("Adding button to Box")
    box.add(another_button)
    box.show_all()


# Notice no decoration for this function
def example_asynch_0():
    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)  # noqa
    vbox: Gtk.Box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    first_button = Gtk.Button(label="First button")
    vbox.add(first_button)
    win.add(vbox)  # noqa
    win.show_all()  # noqa
    return win, vbox


def in_another_thread(window: Gtk.Window, box: Gtk.Box):
    # Wait for Main loop to start, then all our thread safety stuff makes sense.
    time.sleep(4)
    LOGGER_AU.warning("making button")
    my_button: Gtk.Button = new_button()
    if my_button is None:
        raise ValueError("my_button not obtained.")
    LOGGER_AU.warning("button obtained")
    LOGGER_AU.warning("Adding button to window.")
    insert_button(box=box, another_button=my_button)
    window.show_all()  # noqa
    LOGGER_AU.warning("invoking print widget name")
    print_widget_name(my_button)
    LOGGER_AU.warning("print invoked")


def main() -> int:
    LOGGER_AU.warning("main")
    logging.basicConfig(format=LOGGER_FORMAT_AU, level=logging.DEBUG)
    window: Gtk.Window | None = None
    try:
        # No decorations. This is invoked in the application thread, which MIGHT be the main thread, but no loop yet.
        window, vbox = example_asynch_0()
        # Now we start a new thread, but first thing it must do is wait for the MainLoop to start.
        # That's an unusual situation that is contrived for this example.
        thread: threading.Thread = threading.Thread(target=lambda: in_another_thread(window=window, box=vbox))
        thread.start()
        # Gtk.main() does not return until quit
        Gtk.main()  # noqa
    except Exception as an_exception:
        logging.exception(an_exception)
        return -1
    LOGGER_AU.warning("Exiting")
    return 0


if __name__ == '__main__':
    sys.exit(main())
