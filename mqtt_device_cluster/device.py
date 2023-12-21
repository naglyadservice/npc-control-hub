import asyncio
import itertools
import json
import logging
import re

from aiomqtt import Client as MQTTClient
from aiomqtt import error

from mqtt_device_cluster.lock import KeyLock
from mqtt_device_cluster.types import CbKey, ConfigPin, PinCache, SetPin

log = logging.getLogger(__name__)


class DeviceCluster:
    """
    DeviceCluster class for managing MQTT communication with devices and pins.

    Attributes:
        _client (MQTTClient): The MQTT client used for communication.
        _pins (dict[str, dict[int, PinCache]]): Dictionary to store pin information for each device.
        _update_callbacks (list[asyncio.Queue]): List of update callbacks for receiving pin updates.
        _key_lock (KeyLock): Lock for ensuring thread-safe access to MQTT topics.
        _started (bool): Flag indicating if the device cluster has been started.

    Methods:
        pins() -> dict[str, dict[int, PinCache]]: Get the dictionary of pins for each device.
        start() -> None: Start the device cluster and initialize the updates handler.
        _updates_handler() -> None: Handle incoming pin update messages.
        send(topic: str, payload: str, cb_keys: list[CbKey] | None = None, timeout: int | None = None) -> list[PinCache] | None:
            Send a message to a topic and wait for pin updates if cb_keys and timeout is specified.
        config_pins(device_id: str, pins: list[ConfigPin], timeout: int | None = 5) -> list[PinCache] | None:
            Configure pins for a device.
        set_pins(device_id: str, pins: list[SetPin], timeout: int | None = 5) -> list[PinCache] | None:
            Set the state of pins for a device.
        update(device_id: str, pins: list[int] | None = None, timeout: int | None = 5) -> list[PinCache] | None:
            Request pin updates for a device.
        wait_for(cb_keys: list[CbKey]) -> list[PinCache]:
            Wait for pin updates corresponding to the given callback keys.

    Usage:
        mqtt = aiomqtt.Client(...)
        cluster = DeviceCluster(mqtt)

        async with mqtt:
            await cluster.start()
            await cluster.config_pins(
                device_id,
                pins=[
                    {"pin": 13, "mode": PinMode.OUTPUT, "state": PinState.HIGH},
                    {"pin": 14, "mode": PinMode.OUTPUT, "state": PinState.LOW},
                ],
            )
            updates = await cluster.set_pins(
                device_id,
                pins=[
                    {"pin": 13, "state": PinState.LOW, "time": 500},
                    {"pin": 14, "state": PinState.HIGH, "time": 500},
                ],
            )
            print(updates)

    """

    def __init__(self, client: MQTTClient) -> None:
        """
        Initialize the DeviceCluster instance.

        Args:
            client (MQTTClient): The MQTT client used for communication.

        """
        self._client = client
        self._pins: dict[str, dict[int, PinCache]] = {}
        self._update_callbacks: list[asyncio.Queue] = []
        self._key_lock = KeyLock()
        self._started = False

    @property
    def pins(self) -> dict[str, dict[int, PinCache]]:
        """
        Get the dictionary of pins for each device.

        Returns:
            dict[str, dict[int, PinCache]]: The dictionary of pins.

        Usage:
            cluster = DeviceCluster(...)
            device_pins = cluster.pins.get(DEVICE_ID, {})
            pin = device_pins.get(PIN_NUM)
            pin = cluster.pins.get(DEVICE_ID, {}).get(PIN_NUM)
            pin = cluster.pins[DEVICE_ID][PIN_NUM]

        """
        return self._pins

    async def start(self) -> None:
        """
        Start the device cluster and initialize the updates handler.

        """
        asyncio.create_task(self._updates_handler())
        self._started = True

    async def _updates_handler(self):
        """
        Handle incoming pin update messages.
        TODO: add exception handling and reconnection

        """

        async with self._client.messages() as messages:
            try:
                await self._client.subscribe("device/+/pin/update")
                async for message in messages:
                    m = re.search(r"device/(\w+)/pin/update", str(message.topic))
                    if m is None:
                        log.warning("Invalid topic: %s", message.topic)
                        continue

                    device_id = m.group(1)
                    raw_pins = json.loads(message.payload)  # type: ignore

                    for callback in self._update_callbacks:
                        pins = [
                            PinCache(device_id=device_id, **raw_pin)
                            for raw_pin in raw_pins
                        ]
                        device_pins = self._pins.setdefault(device_id, {})
                        device_pins.update({pin.pin: pin for pin in pins})
                        callback.put_nowait(pins)

            except error.MqttError as e:
                if str(e) == "Disconnected during message iteration":
                    return

                raise

    async def send(
        self,
        topic: str,
        payload: str,
        cb_keys: list[CbKey] | None = None,
        timeout: int | None = None,
    ) -> list[PinCache] | None:
        """
        Send a message to a topic and wait for pin updates if cb_keys and timeout is specified.

        Args:
            topic (str): The MQTT topic to publish the message to.
            payload (str): The payload of the message.
            cb_keys (list[CbKey] | None, optional): List of callback keys to wait for. Defaults to None.
            timeout (int | None, optional): Timeout in seconds for waiting for pin updates. Defaults to None.

        Returns:
            list[PinCache] | None: List of pin updates or None if no cb_keys were specified.

        Raises:
            RuntimeError: If the device cluster is not started.
            ValueError: If cb_keys is not specified when timeout is specified.

        """
        if not self._started:
            raise RuntimeError("DeviceCluster is not started, call start() first")

        async with self._key_lock(topic):
            if timeout and not cb_keys:
                raise ValueError("cb_keys must be specified if timeout is specified")

            await self._client.publish(topic, payload)

            if cb_keys is not None and timeout is not None:
                return await asyncio.wait_for(
                    self.wait_for(cb_keys=cb_keys), timeout=timeout
                )

    async def config_pins(
        self, device_id: str, pins: list[ConfigPin], timeout: int | None = 5
    ) -> list[PinCache] | None:
        """
        Configure pins for a device.

        If timeout is specified, wait for confirmation from device and return pin updates or raise TimeoutError.

        Args:
            device_id (str): The ID of the device.
            pins (list[ConfigPin]): List of pins to configure.
            timeout (int | None, optional): Timeout in seconds for waiting for pin updates. Defaults to 5.

        Returns:
            list[PinCache] | None: List of pin updates or None if timeout is None.

        """
        return await self.send(
            topic=f"device/{device_id}/pin/config",
            payload=json.dumps(pins),
            cb_keys=[
                CbKey(device_id=device_id, pin=pin["pin"], mode=pin["mode"])
                for pin in pins
            ],
            timeout=timeout,
        )

    async def set_pins(
        self, device_id: str, pins: list[SetPin], timeout: int | None = 5
    ) -> list[PinCache] | None:
        """
        Set the state of pins for a device.

        If timeout is specified, wait for confirmation from device and return pin updates or raise TimeoutError.

        Args:
            device_id (str): The ID of the device.
            pins (list[SetPin]): List of pins to set.
            timeout (int | None, optional): Timeout in seconds for waiting for pin updates. Defaults to 5.

        Returns:
            list[PinCache] | None: List of pin updates or None if timeout is None.

        """
        return await self.send(
            topic=f"device/{device_id}/pin/set",
            payload=json.dumps(pins),
            cb_keys=[
                CbKey(device_id=device_id, pin=pin["pin"], state=pin["state"])
                for pin in pins
            ],
            timeout=timeout,
        )

    async def update(
        self, device_id: str, pins: list[int] | None = None, timeout: int | None = 5
    ) -> list[PinCache] | None:
        """
        Request pin updates for a device and wait for pin updates.

        If timeout is specified, wait for confirmation from device and return pin updates or raise TimeoutError.

        Args:
            device_id (str): The ID of the device.
            pins (list[int] | None, optional): List of specific pins to request updates for. Defaults to None.
            timeout (int | None, optional): Timeout in seconds for waiting for pin updates. Defaults to 5.

        Returns:
            list[PinCache] | None: List of pin updates or None if timeout is None.

        """
        if pins is None:
            pins = []

        return await self.send(
            topic=f"device/{device_id}/pin/get",
            payload=json.dumps(pins),
            cb_keys=[CbKey(device_id=device_id)],
            timeout=timeout,
        )

    def _check_key_conflicts(self, cb_keys: list[CbKey]):
        """
        Check for conflicts between callback keys.

        Args:
            cb_keys (list[CbKey]): List of callback keys.

        Raises:
            ValueError: If conflicts are found between callback keys.

        """
        for key1, key2 in itertools.combinations(cb_keys, 2):
            if key1 == key2:
                raise ValueError(f"keys have conflicts ({key1}, {key2})")

    async def wait_for(
        self,
        cb_keys: list[CbKey],
    ) -> list[PinCache]:
        """
        Wait for pin updates corresponding to the given callback keys.

        Args:
            cb_keys (list[CbKey]): List of callback keys.

        Returns:
            list[PinCache]: List of pin updates.

        Raises:
            ValueError: If conflicts are found between callback keys.

        """
        self._check_key_conflicts(cb_keys)

        cb_keys = cb_keys.copy()

        update_callback = asyncio.Queue()
        self._update_callbacks.append(update_callback)

        try:
            pins = []
            while cb_keys:
                updates = await update_callback.get()

                for key, pin in itertools.product(cb_keys, updates):
                    if key == pin:
                        pins.append(pin)
                        try:
                            cb_keys.remove(key)
                        except ValueError:
                            pass

            return pins

        finally:
            for i, f in enumerate(self._update_callbacks):
                if f is update_callback:
                    del self._update_callbacks[i]
                    break
