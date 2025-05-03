# This file is executed on every boot (including wake-boot from deep-sleep) AFTER boot.py (if applicable)

import uasyncio

import components.utils.utils as utils
import components.mqtt.mqtt_client as mqtt_client


async def __print_heap_usage_task() -> None:
    while True:
        utils.print_heap_usage()
        await uasyncio.sleep_ms(5000)


def __main() -> None:
    main_loop = uasyncio.get_event_loop()

    mqtt_client.init(
        "@@CLIENT_NAME@@",
        "@@MQTT_BROKER_HOSTNAME@@",
        "/certs/client.der",
        "/certs/client.key.der",
        "/certs/ca.der",
    )

    uasyncio.create_task(mqtt_client.loop())
    uasyncio.create_task(__print_heap_usage_task())

    try:
        main_loop.run_forever()
    finally:
        mqtt_client.disconnect()
        main_loop.close()


if __name__ == "__main__":
    print("Running main.py..")
    __main()
