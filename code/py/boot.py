# This file is executed on every boot (including wake-boot from deep-sleep)

import ntptime

import components.wifi.wifi as wifi
import components.utils.utils as utils


def __start_wifi() -> None:
    wifi.connect("@@WIFI_SSID@@", "@@WIFI_PASSWORD@@")


def __sync_time_with_ntp() -> None:
    try:
        # Fetch time from NTP
        ntptime.settime()
        print("Time synchronized with NTP.")
    except Exception as e:
        print(f"Error fetching time from NTP: {e}")


def __boot() -> None:
    utils.print_heap_usage_raw()
    __start_wifi()
    __sync_time_with_ntp()


if __name__ == "__main__":
    print("Running boot.py..")

    try:
        __boot()
    except KeyboardInterrupt:
        print("Killing boot.py..")
        import sys
        sys.exit(0)
