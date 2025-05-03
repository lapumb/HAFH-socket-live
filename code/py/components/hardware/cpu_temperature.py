import machine

_TEMP_SENSOR = machine.ADC(4)

def read_temperature_f() -> float:
    """
    Read the temperature in Fahrenheit from the internal temperature sensor, which
    will return the temperature, in Fahrenheit, of the CPU itself (**NOT** ambient).
    """
    reading = _TEMP_SENSOR.read_u16() * 3.3 / 65535
    temperature_c = 27 - (reading - 0.706) / 0.001721
    temperature_f = (temperature_c * 9 / 5) + 32
    return temperature_f
