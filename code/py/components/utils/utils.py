import gc
import os

import micropython


def get_heap_usage() -> dict:
    """
    Get the heap usage of the device.

    :return: A dictionary containing the heap usage.
    """
    # collect any outstanding garbage prior to printing heap usage.
    gc.collect()

    return {
        "free_heap": gc.mem_free(),
        "allocated_heap": gc.mem_alloc(),
        "total_heap": gc.mem_free() + gc.mem_alloc(),
    }


def print_heap_usage() -> None:
    """
    Print the heap usage of the device.

    :return: None
    """
    # collect any outstanding garbage prior to printing heap usage.

    gc.collect()
    print(f"Free Heap: {gc.mem_free()}, Allocated Heap: {gc.mem_alloc()}")


def print_heap_usage_raw() -> None:
    """
    Print the heap usage of the device in raw format.

    :return: None
    """
    # collect any outstanding garbage prior to printing heap usage.
    gc.collect()
    micropython.mem_info()


def get_micropython_version() -> str:
    """
    Get the version of MicroPython running on the device.

    :return: The version of MicroPython.
    """
    # uname is a tuple containing the following:
    # (sysname="esp32", nodename="esp32", release="1.15.0", version="v1.15 on 2021-04-18",
    #  machine="ESP32 module with ESP32")
    return os.uname()[3]
