from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    Generator,
    Generic,
    TypeVar,
)

from pydantic import BaseModel, PrivateAttr
from typing_extensions import Self

from .types import CallbackFilter

if TYPE_CHECKING:
    from .device import ControlHub

ResponceType = TypeVar("ResponceType", bound=Any)


class DeviceMethod(BaseModel, ABC):
    device_id: str
    payload: Any
    ttl: int | None

    __topic__: str

    _client: ControlHub = PrivateAttr()

    @property
    def topic(self) -> str:
        return self.__topic__.format(device_id=self.device_id)

    def as_(self, client: ControlHub) -> Self:
        self._client = client
        return self

    async def emit(self, client: ControlHub) -> None:
        return await client(self, ttl=self.ttl)

    @property
    def coro(self) -> Coroutine[Any, Any, None]:
        return self.emit(self._client)

    def __await__(self) -> Generator[Any, None, None]:
        return self.coro.__await__()


class DeviceMethodWithResponce(DeviceMethod, Generic[ResponceType], ABC):
    @property
    @abstractmethod
    def callback_filters(self) -> list[CallbackFilter]:
        raise NotImplementedError

    def wait_responce(
        self, timeout: float | None = 60
    ) -> ResponceHandler[ResponceType]:
        return ResponceHandler(
            original_method=self,
            callback_filters=self.callback_filters,
            responce_timeout=timeout,
        )


class ResponceHandler(BaseModel, Generic[ResponceType]):
    original_method: DeviceMethodWithResponce
    callback_filters: list[CallbackFilter]
    responce_timeout: float | None

    async def emit(self, client: ControlHub) -> ResponceType:
        return await client(
            method=self.original_method,
            callback_filters=self.callback_filters,
            ttl=self.original_method.ttl,
            timeout=self.responce_timeout,
        )

    @property
    def coro(self) -> Coroutine[Any, Any, ResponceType]:
        return self.emit(self.original_method._client)

    def __await__(self) -> Generator[Any, None, ResponceType]:
        return self.coro.__await__()
