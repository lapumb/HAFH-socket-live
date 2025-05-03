import machine

_LED = machine.Pin("LED", machine.Pin.OUT)

def toggle_led(on: bool = None) -> None:
    """
    Toggle the LED on the Pico W. If `on` is True/False, sets state explicitly;
    otherwise toggles the current state.
    """
    _ = _LED.value(on) if on is not None else _LED.toggle()
