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
from typing import Any, Callable

LOGGER_FORMAT_AU = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
LOGGER_AU = logging.getLogger("asynch_utils")


class Status(Enum):
    UNFINISHED = auto()
    DONE = auto()
    ERROR = auto()


def gtk_idle_add(func: Callable) -> Callable:
    """
    Decorator to run a function in the GTK main loop.
    Functions decorated with this will not run if there's no main loop running. Functions that create top-Level Windows
    and Dialogs are a special case, they MOSTLY need to run before a Gtk.MainLoop has started, so GENERALLY don't
    decorate such functions with this, it will cause lockups. DO NOT use this decorator on functions
    that need to return a value derived from a Gtk.Widget, use @gtk_producer instead.
    @param func function to wrap.
    @type func: Callable
    """

    def wrapper(*args, **kwargs):
        GLib.idle_add(lambda: func(*args, **kwargs))

    # If already running on "the main thread", don't wrap the function. Instead, return the original.
    if is_main_thread():
        return func

    return wrapper


def gtk_producer(func: Callable) -> Callable:
    """
    Decorator for functions that need to return a value derived from a function run in the GTK main loop. Use this on
    functions that read any values from Gtk.Widgets, even names, colors etc. DO NOT use this decorator on functions that
    don't return a value, or always return None. Use the @gtk_idle_add decorator instead.
    Also, functions that create top-Level Windows and Dialogs are a special case, they MOSTLY need to run before a
    Gtk.MainLoop has started, so GENERALLY don't decorate such functions with this, it will cause lockups.
    Functions decorated with this will not run, and might deadlock block if there's no main loop running.
    @param func function to wrap.
    @type func: Callable
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
            result[0] = read()
            if result[0] is None:
                LOGGER_AU.debug("read() returned None")
            else:
                # LOGGER_AU.debug("Obtained non-null \"result[0]\" from read()")
                pass
            return False  # Remove idle callback

        GLib.idle_add(idle_callback)

        while status == Status.UNFINISHED:
            # noinspection PyUnresolvedReferences
            Gtk.main_iteration_do(False)
            if status != Status.UNFINISHED:
                LOGGER_AU.debug(f"\"result[0]\" not None, breaking loop.")
                break
        LOGGER_AU.debug("accessor() returning \"result[0]\"")
        return result[0]

    def wrapper(*args, **kwargs):
        return accessor(func, *args, **kwargs)

    # If already running on "the main thread", don't wrap the function. Instead, return the original.
    if is_main_thread():
        return func

    return wrapper


def is_main_thread() -> bool:
    """
    Returns True if the current thread is the "main" Gtk thread. But this is more complex than it seems, because an app
    can use GLib.idle_source_new() that "Creates a new idle source." The documentation is unclear.
    The purpose of this function is to enable code to determine if a callable needs to be scheduled with GLib.idle_add()
    or if it can be invoked directly.
    @return True if the current thread is the "main" Gtk thread, by comparing the current thread to the result of
    threading.main_thread().
    """
    return threading.current_thread() == threading.main_thread()

##########################
#  Code below is for testing and debugging
##########################


@gtk_producer
def _name_of_widget(some_widget: Gtk.Widget) -> str:
    return some_widget.get_name()


@gtk_idle_add
def _print_widget_name(a_widget: Gtk.Widget):
    # Print order can get scrambled in multithreaded code
    sys.stdout.flush()
    sys.stderr.flush()
    print(a_widget.get_name())


@gtk_producer
def _new_button() -> Gtk.Button:
    # Print order can get scrambled in multithreaded code
    sys.stdout.flush()
    sys.stderr.flush()
    LOGGER_AU.warning("Constructing another button")
    fresh_button = Gtk.Button(label="Another button")
    fresh_button.set_name("Sweet Paprika")
    fresh_button.connect("clicked", lambda txt: print(txt))
    return fresh_button


@gtk_idle_add
def _insert_button(box: Gtk.Box, another_button: Gtk.Button):
    # Print order can get scrambled in multithreaded code
    sys.stdout.flush()
    sys.stderr.flush()
    LOGGER_AU.warning("Adding button to Box")
    box.add(another_button)
    box.show_all()


# Notice no decoration for this function
def _example_asynch_0():
    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)  # noqa
    vbox: Gtk.Box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    first_button = Gtk.Button(label="First button")
    vbox.add(first_button)
    win.add(vbox)  # noqa
    win.show_all()  # noqa
    return win, vbox


def _in_another_thread(window: Gtk.Window, box: Gtk.Box):
    # Wait for Main loop to start, then all our thread safety stuff makes sense.
    time.sleep(4)
    # Print order can get scrambled in multithreaded code
    sys.stdout.flush()
    sys.stderr.flush()
    LOGGER_AU.warning("making button")
    my_button: Gtk.Button = _new_button()
    if my_button is None:
        raise ValueError("my_button not obtained.")
    LOGGER_AU.warning("button obtained")
    LOGGER_AU.warning("Adding button to window.")
    _insert_button(box=box, another_button=my_button)
    window.show_all()  # noqa
    LOGGER_AU.warning("invoking print widget name")
    _print_widget_name(my_button)
    LOGGER_AU.warning("print invoked")


def main() -> int:
    LOGGER_AU.warning("main")
    logging.basicConfig(format=LOGGER_FORMAT_AU, level=logging.INFO)
    window: Gtk.Window | None = None
    try:
        # No decorations. This is invoked in the application thread, which MIGHT be the main thread, but no loop yet.
        window, vbox = _example_asynch_0()
        # Now we start a new thread, but the first thing it must do is wait for the MainLoop to start.
        # That's an unusual situation that is contrived for testing.
        thread: threading.Thread = threading.Thread(target=lambda: _in_another_thread(window=window, box=vbox))
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
