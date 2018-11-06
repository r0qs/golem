import functools
import logging
from threading import Lock
from typing import Type, Any

from peewee import DatabaseError

from golem.core.common import HandleAttributeError
from golem.model import Stats

logger = logging.getLogger(__name__)


def log_attr_error(*args, **_kwargs):
    logger.warning("Unknown stats %r", args[1])


class StatsKeeper:

    handle_attribute_error = HandleAttributeError(log_attr_error)

    def __init__(self, stat_class: Type, default_value: str = '') -> None:
        self._lock = Lock()
        self.session_stats = stat_class()
        self.global_stats = stat_class()
        self.default_value = default_value

        for stat in vars(self.global_stats):
            val = self._retrieve_stat(stat)
            if val is not None:
                setattr(self.global_stats, stat, val)

    @handle_attribute_error
    def set_stat(self, name: str, value: Any) -> None:
        with self._lock:
            setattr(self.session_stats, name, value)
            setattr(self.global_stats, name, value)

            try:
                Stats.update(value=f"{value}") \
                    .where(Stats.name == name) \
                    .execute()
            except DatabaseError as err:
                logger.error("Exception occurred while updating stat %r: "
                             "%r", name, err)

    @handle_attribute_error
    def increase_stat(self, name: str, increment: Any = 1) -> None:
        with self._lock:
            val = getattr(self.session_stats, name)
            val = self._cast_type(val + increment, name)
            setattr(self.session_stats, name, val)

            global_val = self._retrieve_stat(name)
            if global_val is not None:

                global_val = self._cast_type(global_val + increment, name)
                setattr(self.global_stats, name, global_val)

                try:
                    Stats.update(value=f"{global_val}") \
                        .where(Stats.name == name) \
                        .execute()
                except DatabaseError as err:
                    logger.error("Exception occurred while updating stat %r: "
                                 "%r", name, err)

    def get_stats(self, name):
        return self._get_stats(name) or (None, None)

    @handle_attribute_error
    def _get_stats(self, name):
        return (
            getattr(self.session_stats, name),
            getattr(self.global_stats, name),
        )

    def _retrieve_stat(self, name: str):
        try:
            defaults = {'value': self.default_value}
            stat, _ = Stats.get_or_create(name=name, defaults=defaults)
            return self._cast_type(stat.value, name)
        except (AttributeError, ValueError, TypeError):
            logger.warning("Wrong stat '%s' format:", name, exc_info=True)
        except DatabaseError:
            logger.warning("Cannot retrieve '%s' from the database:", name,
                           exc_info=True)

    def _cast_type(self, value: Any, name: str) -> Any:
        return self._get_type(name)(value)

    @functools.lru_cache(20)
    def _get_type(self, name: str) -> Type:
        return type(getattr(self.global_stats, name))


class IntStatsKeeper(StatsKeeper):

    def __init__(self, stat_class: Type) -> None:
        super(IntStatsKeeper, self).__init__(stat_class, '0')

    def _cast_type(self, value: Any, name: str) -> Any:
        return int(value)
