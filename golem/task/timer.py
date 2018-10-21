import logging
import time
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class ActionTimer:
    """ Keeps track of started / finished timestamps of an action """

    def __init__(self):
        self._started: Optional[float] = None
        self._finished: Optional[float] = time.time()

    @property
    def finished(self) -> bool:
        return self._finished is not None

    @property
    def time(self) -> Optional[float]:
        """ Returns the time spent on an action or None
        """
        if None in (self._started, self._finished):
            return None
        return self._finished - self._started

    def start(self) -> None:
        """ Updates the started and finished (= None) timestamps.
        """
        logger.debug("ActionTimer.comp_started() at %r", time.time())

        if self._finished is None:
            logger.error("action was not finished")

        self._started = time.time()
        self._finished = None

    def finish(self) -> None:
        """ Updates the finished timestamp.
        """
        logger.debug("ActionTimer.comp_finished() at %r", time.time())

        if self._finished is None:
            self._finished = time.time()
        else:
            logger.warning("action is not running")


class ActionTimers:
    """ Keeps track of started / finished timestamps of multiple actions """

    def __init__(self):
        self._history: Dict[str, ActionTimer] = dict()

    def time(self, identifier: str) -> Optional[float]:
        """ Returns time spent on an action; None if action hasn't
            been finished yet. Throws a KeyError if identifier is not known.
        """
        return self._history[identifier].time

    def start(self, identifier: str) -> None:
        """ Initializes the start and finished (= None) timestamps.
        """
        logger.debug("ActionTimers: started action of %s at %r",
                     identifier, time.time())

        timer = ActionTimer()
        timer.start()
        self._history[identifier] = timer

    def finish(self, identifier: str) -> None:
        """ Updates the finished timestamp.
        """
        timer = self._history.get(identifier)
        if timer and not timer.finished:
            logger.debug("ActionTimers: finished action of %s at %r",
                         identifier, time.time())
            timer.finish()

    def remove(self, identifier: str) -> Optional[float]:
        """ Removes the identifier from history. Throws a KeyError if identifier
            is not known.
        """
        return self._history.pop(identifier).time


ProviderIdleTimer = ActionTimer()  # noqa
ProviderComputeTimers = ActionTimers()  # noqa

