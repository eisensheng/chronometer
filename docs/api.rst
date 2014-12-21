.. -*- encoding: utf-8 -*-
.. _api:


API
===

.. module:: chronometer

.. autoclass:: Chronometer(timer=monotonic)
    :members:

.. autoclass:: RelaxedStartChronometer(timer=monotonic)
    :members:

.. autoclass:: RelaxedStopChronometer(timer=monotonic)
    :members:

.. autoclass:: RelaxedChronometer(timer=monotonic)
    :members:

.. autoexception:: ChronoRuntimeError

.. autoexception:: ChronoAlreadyStoppedError

.. autoexception:: ChronoAlreadyStartedError
