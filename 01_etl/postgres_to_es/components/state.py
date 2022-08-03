import abc
import json
import logging
from typing import Optional

from redis import Redis
import redis

from . import models, log_config
from .utilities import backoff
from .settings import Settings


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище.

        Args:
            state: Cостояние.
        """
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища."""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        """
        Args:
            file_path: Путь к файлу '*.json'.
        """
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище.

        Args:
            state: Cостояние.
        """
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(state, file, ensure_ascii=False, indent=4)

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища.

        Returns:
            state: Cостояние.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                state = json.load(file)
            return state
        except FileNotFoundError:
            self.save_state({})
            return {}
        except Exception:
            return {}


class RedisStorage(BaseStorage):
    def __init__(self, dsl: models.RedisConf = Settings().dsl_redis, key: str = Settings().redis_key):
        """
        Args:
            dsl: Данные для подключения к Redis.
            key: Ключ для Redis.
        """
        self.dsl = dsl
        self.key = key
        self.connection = self.get_connection()

    @backoff(logger=log_config.get_log)
    def get_connection(self) -> Redis:
        """Реализация отказоустойчивости.

        Returns:
            Redis: Конектор.
        """
        return Redis(**self.dsl, decode_responses=True)

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в Redis.

        Args:
            state: Cостояние.
        """
        if state:
            self.connection.hset(self.key, mapping=state)
        else:
            self.connection.delete(self.key)

    def retrieve_state(self) -> dict:
        """Загрузить состояние из Redis.

        Returns:
            state: Cостояние.
        """
        return self.connection.hgetall(self.key)


class State:
    """Класс для хранения состояния при работе с данными."""

    def __init__(self, storage: BaseStorage):
        """
        Args:
            storage: Объект класса JsonFileStorage | RedisFileStorage.
        """
        self.storage = storage
        self.data = self.storage.retrieve_state()

    def set_state(self, key: str, value: str) -> None:
        """Установить состояние для определённого ключа.

        Args:
            key: Ключ.
            value: Состояние.
        """
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> str:
        """Получить состояние по определённому ключу.

        Args:
            key: Ключ.

        Returns:
            value: Состояние.
        """
        return self.data.get(key)
