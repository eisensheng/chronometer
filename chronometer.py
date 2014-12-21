# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from monotonic import monotonic


__version__ = '1.0'
__all__ = ['Chronometer',
           'RelaxedStartChronometer',
           'RelaxedStopChronometer',
           'RelaxedChronometer',
           'ChronoRuntimeError',
           'ChronoAlreadyStartedError',
           'ChronoAlreadyStoppedError', ]


class ChronoRuntimeError(Exception):
    """Base exceptions for errors which happened inside Chronometer."""


class ChronoAlreadyStoppedError(ChronoRuntimeError):
    """Raised when trying to stop a stopped timer."""


class ChronoAlreadyStartedError(ChronoRuntimeError):
    """raised when trying to start a started timer."""


class Chronometer(object):
    """Simple timer meant to be used for measuring how much time has been
    spent in a certain code region.
    """
    __slots__ = ('timer', 'since', 'until', )

    def __init__(self, timer=monotonic):
        self.since, self.until, self.timer = None, None, timer

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()

    def __repr__(self):
        state = 'stopped' if self.stopped else 'started'
        return '<ScopeTimer {0} {1}>'.format(state, self.elapsed)

    def __float__(self):
        return self.elapsed

    def __bool__(self):
        return self.started

    __nonzero__ = __bool__

    def _set(self, since=None, until=None):
        self.since, self.until = since, until

    def start(self):
        """Starts the timer.

        :return:
            Returns the timer itself.
        :rtype:
            Chronometer
        :raises TimerAlreadyStartedError:
            If the timer is already running.
        """
        if self.started:
            raise ChronoAlreadyStartedError('Timer already started.')
        self._set(self.timer())
        return self

    def stop(self):
        """Stops the timer.

        :return:
            Time passed since the timer has been started in seconds.
        :rtype:
            float
        :raises TimerAlreadyStoppedError:
            If the timer is already stopped.
        """
        if self.stopped:
            raise ChronoAlreadyStoppedError('Timer already stopped.')
        self.until = self.timer()
        return self.elapsed

    def reset(self):
        """Resets the timer.

        :return:
            Elapsed time before the timer was reset.
        :rtype:
            float
        """
        try:
            return self.elapsed
        finally:
            self._set(None if self.stopped else self.timer())

    @property
    def elapsed(self):
        """Returns time passed in seconds.

        :return:
            Time passed since the timer has been started in seconds.
        :rtype:
            float
        """
        pit = self.timer()
        return (self.until or pit) - (self.since or pit)

    @property
    def stopped(self):
        """Returns if the timer is stopped or not.

        :return:
            `True` if the timer is stopped and `False` otherwise.
        :rtype:
            bool
        """
        return self.since is None or self.until is not None

    @property
    def started(self):
        """Returns if the timer is running or not.

        :return:
            `True` if the timer is running and `False` otherwise.
        :rtype:
            bool
        """
        return not self.stopped


class RelaxedStartChronometer(Chronometer):
    """Relaxed verison which won't raise an exception on double starting
    the timer.
    """
    __slots__ = []

    def start(self):
        """Starts the timer or just returns if the timer is already running.

        :return:
            Returns the timer itself.
        :rtype:
            RelaxedStartChronometer
        """
        try:
            return super(RelaxedStartChronometer, self).start()
        except ChronoAlreadyStartedError:
            return self


class RelaxedStopChronometer(Chronometer):
    """Relaxed version which won't raise an exception on double stopping
    the timer.
    """
    __slots__ = []

    def stop(self):
        """Stops the timer or just returns if the timer is already stopped.

        :return:
            Time passed since the timer has been started in seconds.
        :rtype:
            float
        """
        try:
            return super(RelaxedStopChronometer, self).stop()
        except ChronoAlreadyStoppedError:
            return self.elapsed


class RelaxedChronometer(RelaxedStartChronometer, RelaxedStopChronometer):
    """Ultra relaxed version which won't throw any exceptions on its own.
    """
    __slots__ = []
