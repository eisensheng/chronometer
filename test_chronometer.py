# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import time

import pytest

from chronometer import (Chronometer, RelaxedChronometer,
                         ChronoAlreadyStartedError, ChronoAlreadyStoppedError)


class TimeGun(object):

    def __init__(self):
        self.state = 123456789000

    def __float__(self):
        return self.state / 1000.

    def __call__(self, *args, **kwargs):
        return float(self)

    def advance(self, amount):
        self.state += int(amount * 1000)


@pytest.fixture
def time_gun():
    return TimeGun()


@pytest.fixture
def chronometer(time_gun):
    return Chronometer(time_gun)


@pytest.fixture
def relaxed_chronometer(time_gun):
    return RelaxedChronometer(time_gun)


def test_state_stopped(chronometer):
    assert chronometer.stopped
    assert not chronometer.started
    assert not chronometer
    assert repr(chronometer) == '<ScopeTimer stopped 0.0>'


def test_state_started(chronometer):
    chronometer.start()
    assert not chronometer.stopped
    assert chronometer.started
    assert chronometer
    assert repr(chronometer) == '<ScopeTimer started 0.0>'


def test_state_with_statement(chronometer):
    assert chronometer.stopped
    with chronometer:
        assert chronometer.started
    assert chronometer.stopped


def test_time_progression(time_gun, chronometer):
    # ensure the value is sane.
    assert 0.0001 > float(chronometer) > -0.0001

    time_gun.advance(2.)

    # value is not allowed to change, timer is not started yet.
    assert 0.0001 > float(chronometer) > -0.0001

    chronometer.start()
    assert chronometer.started

    # time didn't progress yet.
    assert 0.0001 > float(chronometer) > -0.0001

    # move 2 seconds forward in time.
    time_gun.advance(2.)

    # ensure the timer noticed that 2 seconds passed by.
    assert 2.0001 > float(chronometer) > -1.9999

    chronometer.stop()
    assert chronometer.stopped

    # ensure the timer won't progress anymore since it is in stopped state.
    assert 2.0001 > float(chronometer) > -1.9999

    # move 2 more seconds forward in time.
    time_gun.advance(2.)

    # ensure the timer still hasn't changed even though time passed by.
    assert 2.0001 > float(chronometer) > -1.9999


def test_state_relaxed_stop_twice(time_gun, relaxed_chronometer):
    relaxed_chronometer.start()

    time_gun.advance(2.)

    a = int(relaxed_chronometer.stop())

    time_gun.advance(2.)

    b = int(relaxed_chronometer.stop())

    assert a == b


def test_state_relaxed_start_twice(time_gun, relaxed_chronometer):
    for x in range(2):
        relaxed_chronometer.start()
        time_gun.advance(2.)

    assert 4.0001 > relaxed_chronometer.stop() > 3.9999


def test_state_stop_twice(chronometer):
    chronometer.start()

    chronometer.stop()

    with pytest.raises(ChronoAlreadyStoppedError):
        chronometer.stop()


def test_state_start_twice(chronometer):
    chronometer.start()

    with pytest.raises(ChronoAlreadyStartedError):
        chronometer.start()


def test_reset_stopped_timer(time_gun, chronometer):
    with chronometer:
        time_gun.advance(2.)

    assert 2.0001 > chronometer.reset() > 1.9999
    assert 0.0001 > float(chronometer) > -0.0001


def test_reset_running_timer(time_gun, chronometer):
    chronometer.start()

    time_gun.advance(2.)

    assert 2.0001 > chronometer.reset() > 1.9999

    time_gun.advance(3.)

    assert 3.0001 > chronometer.reset() > 2.9999


def test_integration():
    t = Chronometer()

    t.start()

    a = t.elapsed
    time.sleep(0.002)
    b = t.elapsed

    assert b > a

    t.stop()

    c = t.elapsed
    time.sleep(0.002)
    d = t.elapsed

    assert (d - c) < 0.000001
