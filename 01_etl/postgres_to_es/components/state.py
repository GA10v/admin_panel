import abc
from asyncio import constants
import json
from typing import Optional
from .utilities import backoff
from . import constants, models

from redis import Redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище."""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища."""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        """
        Args:        
        file_path: Путь к файлу.
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
    def __init__(self, dsl: models.RedisConf = constants.DSL_REDIS, key: str = constants.REDIS_KEY):
        """
        Args:
            redis_adapter: Клиент для работы с Redis.
            key: Ключ.        
        """
        self.dsl = dsl
        self.key = key
        self.connection = self.get_connection()

    @backoff()
    def get_connection(self) -> Redis:
        """ Реализация отказоустойчивости.

        Returns:
            Redis: Объект класса Redis, конектор.      
        """
        return Redis(**self.dsl, decode_responses=True)

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в Redis.

        Args:
            state: Cостояние.        
        """
        if state:
            self.connection.hset(self.key, mapping=state)
            # key = [_ for _ in state][0]
            # value = state.get(key)
            # self.connection.hset(key=key, value=value)
        else:
            self.connection.delete(self.key)

    def retrieve_state(self) -> dict:
        """Загрузить состояние из Redis."""
        try:
            return self.connection.hgetall(self.key)
        except Exception:
            return {}


class State:
    """
    Класс для хранения состояния при работе с данными.
    """

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
        """
        return self.data.get(key)
