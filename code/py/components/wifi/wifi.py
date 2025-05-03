from network import WLAN, STA_IF


def connect(ssid: str, password: str) -> None:
    """
    Connect to a Wi-Fi network.
    
    :param ssid: The SSID of the Wi-Fi network.
    :param password: The password for the Wi-Fi network.
    
    :return: None
    """
    wlan = WLAN(STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("connecting to wifi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass

    print("Wifi connected successfully")
    print("network config:", wlan.ifconfig())


def is_connected() -> bool:
    """
    Whether or not the device is connected to wifi.

    :return: True if connected, False otherwise.
    """
    wlan = WLAN(STA_IF)
    return wlan.isconnected()
