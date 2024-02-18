import asyncio
import itertools
import json
import logging
import re
from typing import Any, Callable, Coroutine

from aiomqtt import Client as MQTTClient
from aiomqtt import error

from .lock import KeyLock
from .methods import (
    SetPhonesMethod,
    SetPinPayload,
    SetPinsMethod,
    UpdatePinsMethod,
)
from .methods_base import DeviceMethod
from .types import Cache, CallbackFilter, Pin, RawUpdate, UpdatePin

log = logging.getLogger(__name__)


class DeviceCluster:
    def __init__(self, client: MQTTClient) -> None:
        self._client = client
        self._cache: dict[str, Cache] = {}
        self._update_callbacks: list[Callable[[str, RawUpdate], Coroutine]] = []
        self._key_lock = KeyLock()
        self._started = False

    @property
    def cache(self) -> dict[str, Cache]:
        return self._cache

    async def start(self) -> None:
        """
        Start the device cluster and initialize the updates handler.

        """
        asyncio.create_task(self._updates_handler())
        self._started = True

    def add_update_callback(
        self, callback: Callable[[str, RawUpdate], Coroutine]
    ) -> None:
        self._update_callbacks.append(callback)

    def remove_update_callback(
        self, callback: Callable[[str, RawUpdate], Coroutine]
    ) -> None:
        for i, f in enumerate(self._update_callbacks):
            if f is callback:
                del self._update_callbacks[i]
                return

        raise ValueError("Callback not found")

    async def _updates_handler(self):
        """
        Handle incoming pin update messages.
        TODO: add exception handling and reconnection
        TODO: handling "open by phone call" update
        """

        async with self._client.messages() as messages:
            try:
                await self._client.subscribe("device/+/update")
                async for message in messages:
                    m = re.search(r"device/(\w+)/update", str(message.topic))
                    if m is None:
                        log.warning("Invalid topic: %s", message.topic)
                        continue

                    device_id = m.group(1)
                    update = RawUpdate.model_validate_json(message.payload)
                    log.debug("Received update for device %s: %s", device_id, update)

                    cache = self._cache.setdefault(device_id, Cache())

                    if update.pins is not None:
                        for pin in update.pins:
                            cache.pins.update(pin)

                    if update.temperature_on_board is not None:
                        cache.temperature_on_board = update.temperature_on_board

                    if update.temperature_outdoor is not None:
                        cache.temperature_outdoor = update.temperature_outdoor

                    asyncio.gather(
                        *[
                            callback(device_id, update)
                            for callback in self._update_callbacks
                        ]
                    )

            except error.MqttError as e:
                if str(e) == "Disconnected during message iteration":
                    return

                raise

    async def __call__(
        self,
        method: DeviceMethod,
        callback_filters: list[CallbackFilter] | None = None,
        timeout: float | None = 10,
    ) -> Any:
        """
        Send a message to a topic and wait for pin updates if filters and timeout is specified.

        Raises:
            RuntimeError: If the device cluster is not started.
            ValueError: If filters is not specified when timeout is specified.
            TimeoutError: If timeout is reached.

        """
        if not self._started:
            raise RuntimeError("DeviceCluster is not started, call start() first")

        async with self._key_lock(method.topic):
            await self._client.publish(method.topic, json.dumps(method.payload))

            if callback_filters is not None and timeout is not None:
                return await asyncio.wait_for(
                    self.wait_for(device_id=method.device_id, filters=callback_filters),
                    timeout=timeout,
                )

    def set_pins(self, device_id: str, payload: list[SetPinPayload]) -> SetPinsMethod:
        return SetPinsMethod(device_id=device_id, payload=payload).as_(self)

    def set_phones(self, device_id: str, phones: list[str]) -> SetPhonesMethod:
        return SetPhonesMethod(device_id=device_id, payload={"phone_list": phones}).as_(
            self
        )

    def update_pins(self, device_id: str, pins: list[Pin]) -> UpdatePinsMethod:
        return UpdatePinsMethod(device_id=device_id, payload=pins).as_(self)

    def _check_filters_conflicts(self, filters: list[CallbackFilter]):
        """
        Check for conflicts between callback filters.
        """
        for filter1, filter2 in itertools.combinations(filters, 2):
            if filter1(filter2):
                raise ValueError(f"filters have conflicts ({filter1}, {filter2})")

    async def wait_for(
        self,
        device_id: str,
        filters: list[CallbackFilter],
        allow_different_updates: bool = False,
    ) -> list[UpdatePin]:
        """
        Wait for pin updates corresponding to the given callback filters.

        Args:
            filters (list[CallbackFilter]): List of callback filters.
            allow_different_updates (bool, optional): Allow use of different updates for cheking filters. Defaults to False.
        """

        async def update_callback(u_device_id: str, update: RawUpdate):
            if u_device_id != device_id or update.pins is None:
                return

            filters_current = filters.copy()
            curr_pins = []

            for filter_, pin in itertools.product(filters, update.pins):
                if filter_(pin):
                    curr_pins.append(pin)
                    try:
                        filters_current.remove(filter_)
                    except ValueError:
                        pass

            if not filters_current:
                fut.set_result(curr_pins)
                return

            if allow_different_updates:
                pins.extend(curr_pins)
                for key in filters_current:
                    filters.remove(key)

                if not filters:
                    fut.set_result(pins)

        self._check_filters_conflicts(filters)

        pins: list[UpdatePin] = []
        fut = asyncio.Future[list[UpdatePin]]()

        self.add_update_callback(update_callback)

        try:
            return await fut

        finally:
            self.remove_update_callback(update_callback)
