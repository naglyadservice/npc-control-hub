from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
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

    __topic__: str

    _client: ControlHub = PrivateAttr()

    @property
    def topic(self) -> str:
        return self.__topic__.format(device_id=self.device_id)

    def as_(self, client: ControlHub) -> Self:
        self._client = client
        return self

    async def emit(self, client: ControlHub) -> None:
        return await client(self)

    def __await__(self) -> Generator[Any, None, None]:
        client = self._client
        return self.emit(client).__await__()


class ResponceDeviceMethod(DeviceMethod, Generic[ResponceType], ABC):
    @property
    @abstractmethod
    def callback_filters(self) -> list[CallbackFilter]:
        raise NotImplementedError

    def wait_responce(self, timeout: float = 10) -> ResponceHandler[ResponceType]:
        return ResponceHandler(
            original_method=self,
            callback_filters=self.callback_filters,
            responce_timeout=timeout,
        )


class ResponceHandler(BaseModel, Generic[ResponceType]):
    original_method: ResponceDeviceMethod
    callback_filters: list[CallbackFilter]
    responce_timeout: float

    async def emit(self, client: ControlHub) -> ResponceType:
        return await client(self.original_method, self.callback_filters, self.responce_timeout)

    def __await__(self) -> Generator[Any, None, ResponceType]:
        client = self.original_method._client
        return self.emit(client).__await__()
