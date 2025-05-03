import tls
import ujson
import uasyncio

try:
    from umqtt.robust import MQTTClient
except ImportError:
    import mip

    # umqtt.robust depends on umqtt.simple, so we need to install both (in that order).
    mip.install("umqtt.simple")
    mip.install("umqtt.robust")
    from umqtt.robust import MQTTClient

from ..simple_queue.simple_queue import SimpleQueue
from ..wifi import wifi


_MQTT_PORT: int = 8883

_client_name: str = ""
_mqtt_client: MQTTClient = None
_mqtt_client_is_connected: bool = False
_initialized: bool = False

# A dictionary of MQTT subscriptions: <"topic_name", on_topic_cb>.
_mqtt_subscriptions_dict: dict = {}

# A queue of telemetry messages waiting to be sent. Each message is
# stored at as a tuple: (topic_name, json_payload_str)
_telemetry_queue: SimpleQueue = None


def __byte_array_to_string(byte_arr: bytearray) -> str:
    return byte_arr.decode("utf-8")


def __top_level_subscription_cb(topic_name: bytearray, json_payload: bytearray) -> None:
    global _mqtt_subscriptions_dict

    topic_name_str: str = __byte_array_to_string(topic_name)
    json_payload_str: str = __byte_array_to_string(json_payload)
    json_payload_dict: dict = ujson.loads(json_payload_str)

    try:
        callback = _mqtt_subscriptions_dict.get(topic_name_str)
        if callback is not None and callback != None:
            callback(topic_name_str, json_payload_dict)
    except Exception as error:
        print(
            f"Topic {topic_name_str}: An error occurred upon receiving subscription payload: {str(error)}"
        )


def __publish(topic_name: str, json_payload_str: str) -> None:
    global _initialized, _mqtt_client_is_connected, _mqtt_client

    assert _initialized
    assert _mqtt_client_is_connected

    print("Publishing to " + topic_name + ": " + json_payload_str)

    try:
        _mqtt_client.publish(topic_name, json_payload_str, qos=1)
    except Exception as error:
        print("Failed to publish telemetry message: " + str(error))
        raise


def __publish_queued_messages() -> None:
    global _telemetry_queue

    telemetry_data = _telemetry_queue.dequeue()
    while telemetry_data is not None:
        topic_name: str = telemetry_data[0]
        json_payload_str: str = telemetry_data[1]
        __publish(topic_name, json_payload_str)
        telemetry_data = _telemetry_queue.dequeue()


def __setup_subscriptions(mqtt_client: MQTTClient) -> None:
    assert mqtt_client is not None and mqtt_client != None

    # See warnings about subscriptions here:
    # https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.robust/example_sub_robust.py
    try:
        mqtt_client.set_callback(__top_level_subscription_cb)
    except Exception as error:
        print("Error registering subsctiption callback: " + str(error))
        raise


def __connect_mqtt_client(
    thing_name: str, host_name: str, cert: bytes, private_key: bytes, ca: bytes
) -> None:
    global _mqtt_client

    try:
        # Configure mTLS.
        context = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
        context.verify_mode = tls.CERT_REQUIRED
        context.load_verify_locations(ca)
        context.load_cert_chain(cert, private_key)
        _mqtt_client = MQTTClient(
            thing_name, host_name, port=_MQTT_PORT, keepalive=10000, ssl=context
        )
        print("MQTT client created successfully!")
        __setup_subscriptions(_mqtt_client)
        _mqtt_client.connect()
        assert _mqtt_client is not None and _mqtt_client != None
        print("MQTT client connected successfully!")
    except Exception as error:
        print("An error occurred when connecting to MQTT broker: " + str(error))
        raise


def init(
    client_name: str,
    host_name: str,
    cert_file_path: str,
    private_key_file_path: str,
    ca_file_path: str,
    telemetry_queue_size: int = 5,
) -> None:
    """Configure and connect to the MQTT broker.

    Parameters
    ----------
    `client_name` : str
        The device's client name, typically the device serial number

        Note: this CANNOT be None

    `host_name` : str
        The host name used to connect to the MQTT server

        Note: this CANNOT be None

    `cert_file_path` : str
        The relative path to the client certificate (.der) file (i.e., /certs/client.der)

        Note: this CANNOT be None

    `private_key_file_path` : str
        The relative path to the client private-key (.der) file (i.e., /certs/client.key.der)

        Note: this CANNOT be None

    `ca_file_path` : str
        The relative path to the CA (.der) file (i.e., /certs/ca.der)

        Note: this CANNOT be None

    `telemetry_queue_size` : int
        The size of the telemetry queue. The telemetry queue is appended to whenever `publish`
        is called. The queued telemetry (MQTT) messages are published as soon as possible.

        Note: this must be at least 2

    Exceptions
    ----------
    An exception will be raised if:

    1. The cert file cannot be read

    2. The key file cannot be read

    3. An MQTT connection cannot be established
    """
    assert client_name is not None
    assert host_name is not None
    assert cert_file_path is not None and cert_file_path.endswith(".der")
    assert private_key_file_path is not None and private_key_file_path.endswith(".der")
    assert ca_file_path is not None and ca_file_path.endswith(".der")
    assert telemetry_queue_size is not None and telemetry_queue_size >= 2

    if not wifi.is_connected():
        print("Cannot initialize an MQTT client if wifi is not connected!")
        return

    print("---------------------------------------")
    print("client_name: " + client_name)
    print("host_name: " + host_name)
    print("cert_file_path: " + cert_file_path)
    print("private_key_file_path: " + private_key_file_path)
    print("telemetry_queue_size: " + str(telemetry_queue_size))
    print("---------------------------------------")

    global _telemetry_queue, _client_name, _mqtt_client_is_connected, _initialized

    _telemetry_queue = SimpleQueue(telemetry_queue_size)

    try:
        with open(cert_file_path, "rb") as cert_file:
            certificate: bytes = cert_file.read()

        with open(private_key_file_path, "rb") as private_key_file:
            private_key: bytes = private_key_file.read()

        with open(ca_file_path, "rb") as ca_file:
            ca: bytes = ca_file.read()
    except Exception as error:
        print("An error occurred when reading mTLS credentials: " + str(error))
        raise

    __connect_mqtt_client(client_name, host_name, certificate, private_key, ca)

    _client_name = client_name
    _mqtt_client_is_connected = True
    _initialized = True


def disconnect() -> None:
    """Disconnect the MQTT client from the broker."""
    global _mqtt_client_is_connected, _initialized
    assert _initialized
    _mqtt_client_is_connected = False
    _mqtt_client.disconnect()


def get_client_name() -> str:
    """Get the devices MQTT client name"""
    global _initialized, _client_name
    assert _initialized
    return _client_name


def subscribe(topic_name: str, callback: function) -> None:
    """Subscribe to an MQTT topic.

    Parameters
    ----------
    `topic_name` : str
        The topic name to subscribe to

        Note: this CANNOT be None

    `callback` : function
        Called when a payload is received at the subscribed topic_name, where the topic name (string) and json payload (dict) are passed into the function

        Signature: `on_subscription_cb(topic_name: str, json_payload: dict) -> None`

        Note: this CANNOT be None
    """
    global _initialized, _mqtt_client_is_connected, _mqtt_client, _mqtt_subscriptions_dict
    
    assert topic_name is not None
    assert callback is not None
    assert _initialized
    assert _mqtt_client_is_connected

    try:
        _mqtt_client.subscribe(topic_name)
        _mqtt_subscriptions_dict[topic_name] = callback
        print("Subscribed to topic: " + topic_name)
    except Exception as error:
        print("Failed to subscribe to topic (" + topic_name + "): " + str(error))
        raise


def publish(topic_name: str, json_payload_str: str) -> None:
    """Append a telemetry message to the telemetry queue to be published as soon 
    as possible in `loop`.

    Parameters
    ----------
    `topic_name` : str
        The topic name to publish the json_payload_str to

        Note: this CANNOT be None

    `json_payload_str` : str
        The JSON payload, as a string, to publlish to topic_name

        Note: this CANNOT be None
    """
    global _initialized, _telemetry_queue

    assert _initialized
    assert topic_name is not None
    assert json_payload_str is not None
    _telemetry_queue.enqueue((topic_name, json_payload_str))


async def loop() -> None:
    """The task to asynchronously publish queued messages and check for incoming messages.

    Usage
    -----
    ```python
    import uasyncio
    main_loop = uasyncio.get_event_loop()
    mqtt_client.init(client_name, host_name, cert_file_path, private_key_file_path, ca_file_path)
    uasyncio.create_task(mqtt_client.loop())
    main_loop.run_forever()
    ```
    """
    global _initialized, _mqtt_client_is_connected, _mqtt_client

    assert wifi.is_connected()
    assert _initialized
    assert _mqtt_client_is_connected

    while _mqtt_client_is_connected:
        __publish_queued_messages()

        # Check for any incoming messages.
        _mqtt_client.check_msg()

        await uasyncio.sleep_ms(100)
