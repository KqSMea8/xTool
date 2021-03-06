# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object


class State(object):
    """
    Static class with task instance states constants and color method to
    avoid hardcoding.
    """

    # scheduler
    NONE = None
    REMOVED = "removed"
    SCHEDULED = "scheduled"

    # set by the executor (t.b.d.)
    # LAUNCHED = "launched"

    # set by a task
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    SHUTDOWN = "shutdown"  # External request to shut down
    FAILED = "failed"
    UP_FOR_RETRY = "up_for_retry"
    UPSTREAM_FAILED = "upstream_failed"
    SKIPPED = "skipped"

    task_states = (
        SUCCESS,
        RUNNING,
        FAILED,
        UPSTREAM_FAILED,
        UP_FOR_RETRY,
        QUEUED,
        NONE,
        SCHEDULED,
    )

    dag_states = (
        SUCCESS,
        RUNNING,
        FAILED,
    )

    state_color = {
        QUEUED: 'gray',
        RUNNING: 'lime',
        SUCCESS: 'green',
        SHUTDOWN: 'blue',
        FAILED: 'red',
        UP_FOR_RETRY: 'gold',
        UPSTREAM_FAILED: 'orange',
        SKIPPED: 'pink',
        REMOVED: 'lightgrey',
        SCHEDULED: 'tan',
        NONE: 'lightblue',
    }

    @classmethod
    def color(cls, state):
        return cls.state_color.get(state, 'white')

    @classmethod
    def color_fg(cls, state):
        """背景色 ."""
        color = cls.color(state)
        if color in ['green', 'red']:
            return 'white'
        else:
            return 'black'

    @classmethod
    def finished(cls):
        """
        A list of states indicating that a task started and completed a
        run attempt. Note that the attempt could have resulted in failure or
        have been interrupted; in any case, it is no longer running.
        """
        return [
            cls.SUCCESS,
            cls.SHUTDOWN,
            cls.FAILED,
            cls.SKIPPED,
        ]

    @classmethod
    def unfinished(cls):
        """
        A list of states indicating that a task either has not completed
        a run or has not even started.
        """
        return [
            cls.NONE,
            cls.SCHEDULED,
            cls.QUEUED,
            cls.RUNNING,
            cls.UP_FOR_RETRY
        ]
