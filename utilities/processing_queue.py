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
import time
from queue import Queue
from typing import Any, Callable


class ProcessingQueueThrottled:
    ENQUEUE_INTERVAL_MINIMUM_NS: int = 4 * 1_000_000_000
    DEQUEUE_INTERVAL_MINIMUM_NS: int = 4 * 1_000_000_000

    def __init__(self, consumer: Callable[[Any,], None]):
        """
        Constructs a ProcessingQueue instance, that will invoke the consumer function on the item from the front of the
         queue if at least DEQUEUE_INTERVAL_MINIMUM_NS have elapsed since the last dequeue.
        :param consumer: The function to run on items at the front of the queue.
        """
        self._queue: Queue = Queue(maxsize=0)
        self._consumer: Callable[[Any,], None] = consumer
        self._current_time = time.monotonic_ns()
        self._enqueued_last = 0  # should be epoch
        self._dequeued_last = 0  # should be epoch

    @property
    def enqueued_last(self):
        return self._enqueued_last

    @property
    def dequeued_last(self):
        return self._dequeued_last

    @property
    def current_monotonic(self):
        return self._current_time

    @property
    def consumer(self) -> Callable[[Any,], None]:
        return self._consumer

    def enqueue(self, item) -> bool:
        """
        If at least ENQUEUE_INTERVAL_MINIMUM time has elapsed since the last enqueue,
        appends an item to the end of the queue if the queue is empty or . If the item is enqueued, the property
        enqueued_last is updated to the current monotonic time.
        :param item: the item to enqueue
        :return: True if the item is enqueued, else False
        """
        # Don't use properties within these methods, because nanoseconds count.
        if self._queue.empty():
            self._queue.put_nowait(item=item)
            self._enqueued_last = time.monotonic_ns()
            return True
        self._current_time = time.monotonic_ns()
        total_elapsed = self._current_time - self._enqueued_last
        if total_elapsed > ProcessingQueueThrottled.ENQUEUE_INTERVAL_MINIMUM_NS:
            self._queue.put_nowait(item=item)
            self._enqueued_last = time.monotonic_ns()
            return True
        return False

    def dequeue(self) -> bool:
        """
        If at least DEQUEUE_INTERVAL_MINIMUM time has elapsed since the last dequeue,
        removes an item from the front of the queue, and passes it as an argument to the consumer that is a property of
        this ProcessingQueue. The item is still removed from the queue, even if the consumer raises an exception.  If
        the item is dequeued, the property dequeued_last is updated to the current monotonic time.
        :return: True if the item is dequeued, else False
        """
        # Don't use properties within these methods, because nanoseconds count.
        if self._queue.empty():
            return False
        dequeued = False
        self._current_time = time.monotonic_ns()
        total_elapsed = self._current_time - self._dequeued_last
        if total_elapsed > ProcessingQueueThrottled.DEQUEUE_INTERVAL_MINIMUM_NS:
            item = self._queue.get_nowait()
            dequeued = True
            try:
                self._consumer(item)
            except Exception as e_err:  # noqa
                logging.exception(e_err)
        return dequeued
