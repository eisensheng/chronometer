Chronometer
===========

.. image:: https://img.shields.io/travis/eisensheng/chronometer.svg?style=flat
    :target: https://travis-ci.org/eisensheng/chronometer
    :alt: Continuous Integration

.. image:: https://img.shields.io/coveralls/eisensheng/chronometer/develop.svg?style=flat
    :target: https://coveralls.io/r/eisensheng/chronometer?branch=develop
    :alt: Test Coverage

.. image:: https://readthedocs.org/projects/chronometer/badge/?version=latest&style=flat
    :target: http://chronometer.readthedocs.org/en/latest/
    :alt: Documentation

.. image:: https://img.shields.io/pypi/v/chronometer.svg?style=flat
    :target: https://pypi.python.org/pypi/chronometer/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/chronometer.svg?style=flat
    :target: https://pypi.python.org/pypi/chronometer/
    :alt: Python versions

.. image:: https://img.shields.io/pypi/l/chronometer.svg?style=flat
    :target: https://github.com/eisensheng/chronometer/blob/develop/COPYING
    :alt: MIT License


Yet another simple time measurement tool for Python.  The goal of this
implementation is to avoid as much cruft as possible.  The current version
is 73 lines of actual code long, leaving out blank, doc and comment lines.
Chronometer provides only functions to measure how much wall-clock time
has passed between starting and stopping the timer.

Nothing more.  Nothing less.

Chronometer tries to stay accurate to the actual time spent between
starting and stopping the timer by utilizing a monotonic timer.  According
to the linux manual a monotonic timer is subject to time adjustments so
it stays accurate but will never move backwards or jump.  It will be
adjusted gradually and always moves forward as long as the system runs.


Examples
--------

Easy:

.. code-block:: python

    import time
    from chronometer import Chronometer

    long_running_task = lambda: time.sleep(3.)

    with Chronometer() as t:
        long_running_task()  # that will take a few seconds.
    print('Phew, that took me {:.3f} seconds!'.format(float(t)))


Advanced:

.. code-block:: python

    from time import sleep
    from chronometer import Chronometer

    counter = 0
    def long_running_task_that_can_fail():
        global counter
        counter += 1
        sleep(2.)
        return counter > 3

    with Chronometer() as t:
        while not long_running_task_that_can_fail():
            print('Failed after {:.3f} seconds!'.format(t.reset()))
    print('Success after {:.3f} seconds!'.format(float(t)))


Ridiculous:

.. code-block:: python

    import asyncio
    from chronometer import Chronometer


    class PingEchoServerProtocol(asyncio.StreamReaderProtocol):

        def __init__(self):
            super().__init__(asyncio.StreamReader(), self.client_connected)
            self.reader, self.writer = None, None
            self.latency_timer = Chronometer()

        def client_connected(self, reader, writer):
            self.reader, self.writer = reader, writer
            asyncio.async(self.ping_loop())
            asyncio.async(self.handler())

        @asyncio.coroutine
        def send(self, data):
            self.writer.write(data.encode('utf-8') + b'\n')
            yield from self.writer.drain()

        @asyncio.coroutine
        def ping_loop(self):
            yield from asyncio.sleep(5.)
            while True:
                if self.latency_timer.stopped:
                    self.latency_timer.start()
                    yield from self.send('PING (send me PONG!)')

                sleep_duration = max(2., 10. - self.latency_timer.elapsed)
                yield from asyncio.sleep(sleep_duration)

        @asyncio.coroutine
        def handler(self):
            while True:
                data = (yield from self.reader.readline())
                if data[:4] == b'PONG' and self.latency_timer.started:
                    yield from self.send(('Latency: {:.3f}s'
                                          .format(self.latency_timer.stop())))

    l = asyncio.get_event_loop()

    @asyncio.coroutine
    def startup():
        s = (yield from l.create_server(lambda: PingEchoServerProtocol(),
                                        host='localhost', port=2727))
        print('Now telnet to localhost 2727')
        yield from s.wait_closed()

    l.run_until_complete(startup())
