# This file is executed on every boot (including wake-boot from deep-sleep) AFTER boot.py (if applicable)

import uasyncio
import ujson

import components.mqtt.mqtt_client as mqtt_client
import components.utils.utils as utils
import components.hardware.cpu_temperature as cpu_temperature
import components.hardware.led as led


_CLIENT_NAME = "@@CLIENT_NAME@@"


async def __print_heap_usage_task() -> None:
    while True:
        utils.print_heap_usage()
        await uasyncio.sleep_ms(5000)


def __build_payload_json() -> str:
    """
    Build the payload JSON string to be sent to the MQTT broker.
    """
    payload = {
        "serial_number": _CLIENT_NAME,
        "data": {
            "micropython_version": utils.get_micropython_version(),
            "cpu_temperature": cpu_temperature.read_temperature_f(),
            "heap_usage": utils.get_heap_usage(),
        }
    }

    return ujson.dumps(payload)


async def __publish_task() -> None:
    while True:
        led.toggle_led(on = True)
        await uasyncio.sleep(30)

        mqtt_client.publish(f"/peripherals/readings/{_CLIENT_NAME}", __build_payload_json())

        led.toggle_led(on = False)
        await uasyncio.sleep(30)


def __main() -> None:
    main_loop = uasyncio.get_event_loop()

    mqtt_client.init(
        _CLIENT_NAME,
        "@@MQTT_BROKER_HOSTNAME@@",
        "/certs/client.der",
        "/certs/client.key.der",
        "/certs/ca.der",
    )

    uasyncio.create_task(mqtt_client.loop())
    uasyncio.create_task(__publish_task())
    uasyncio.create_task(__print_heap_usage_task())

    try:
        main_loop.run_forever()
    finally:
        mqtt_client.disconnect()
        main_loop.close()


if __name__ == "__main__":
    print("Running main.py..")
    __main()
