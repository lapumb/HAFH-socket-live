# HAFH SocketLive

This repository contains the [MicroPython](https://micropython.org/) source code for the `SocketLive` project. `SocketLive` was born because the [GFCI](https://www.unitedrentals.com/project-uptime/safety/what-does-gfci-mean-and-what-do-they-do) my [sump pump](https://www.freshwatersystems.com/blogs/blog/what-is-a-sump-pump-and-how-does-it-work) was plugged into tripped without giving any indication, causing my basement to flood. I do not want this to happen again to myself, nor anyone else.

To gut shot my problem, I decided to create `SocketLive` to passively monitor whether or not a GFCI outlet is actively being powered. The passive monitoring occurs through the [HAFH-server](https://github.com/lapumb/HAFH-server), which will receive an (mTLS) MQTT message from the `SocketLive` device once a minute. The idea is that, if _X_ number of readings (MQTT publishes) are missed by the server, the socket is no longer online.

>**Note**: the `HAFH` system is still under development. Eventually, there will be a mobile application where specific notifications can be configured for a given HAFH peripheral (mTLS MQTT-driven device).

**Although this project _is_ something I actively utilize, it is a minimal, quick-and-dirty example of how to integrate a sensor into your HAFH network.**

>Note: the majority of this repository is a massaged version of [ESP32-MicroPython-Starter](https://github.com/lapumb/ESP32-MicroPython-Starter).

## Dependencies

### Hardware

- [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/?variant=raspberry-pi-pico-w)
- [Micro USB cable **with data line**](https://a.co/d/60GPOF1)
- [5V Power block](https://a.co/d/gO7BRaF)

    >Note: the Pico W is a low power device. It is recommended to use a 5V power block with a micro USB cable to power the device. The power block should be able to provide at least 1A of current.

### Software

- Python 3.10 or higher
- [`venv`](https://docs.python.org/3/library/venv.html)
- `bash`

## Setting up the Environment

1. Clone the repository:

```bash
git clone git@github.com:lapumb/HAFH-socket-live.git
```

1. Set up your virtual environment:

```bash
cd HAFH-socket-live
python3 -m venv .venv
source .venv/bin/activate
```

>You can deactivate the virtual environment by running `deactivate` in the terminal. To reactivate it, run `source .venv/bin/activate` again.

1. Install the required packages:

```bash
pip install -r requirements.txt
```

1. Setup your `.userenv` file to export the required environment variables that are used at "flashing" time. You can copy the `.userenv.example` file to `.userenv` and edit it to match your configuration:

```bash
cp .userenv.example .userenv
```

1. Source the `.userenv` file to export the environment variables:

```bash
source .userenv
```

## Certificates & Keys

TODO: Fill in!

## "Flashing" the Pico W

1. Put the Pico W into bootloader mode by holding down the `BOOTSEL` button while plugging it into your computer with the uUSB cable. This will mount the Pico W as a USB drive named `RPI-RP2`.
1. Run `./MicroPython/download_picow_micropython.sh` to download the latest supported version of MicroPython for the project. Alternatively, navigate to [MicroPython's download page](https://micropython.org/download/RPI_PICO_W/) if you prefer to download the firmware manually.
1. Drag and drop the downloaded `.uf2` file onto the Pico W drive. This will flash the MicroPython firmware onto the Pico W. Once the flashing is complete, the Pico W will reboot and will not appear as a mass storage device until you put it back into bootloader mode.
1. Open a terminal and find the serial port for the Pico W (e.g., `ls /dev/ttyACM*` on Linux or `ls /dev/cu.usbmodem*` on macOS). The port will be something like `/dev/ttyACM0` or `/dev/cu.usbmodem14201`.

    >At this point, you can use a serial terminal program (e.g., `screen`, `picocom`, or `PuTTY`) to connect to the Pico W to interact with the Read-Eval-Print-Loop (REPL) using a baud rate of 115200. For example, you can use the following command to connect to the Pico W using `screen`:
    >
    >```bash
    >picocom -b 115200 /dev/ttyACM0
    >```
    >
    >To exit `picocom`, press `Ctrl+A` followed by `Ctrl+X`.

1. Install the `SocketLive` scripts and certs on the Pico W by running the following command in the terminal:

```bash
# Pass in the -h flag to see the help message.
./code/flash_modules.sh
```

It is worth validating your installation by monitoring the Pico W's serial output (described above) and checking the `HAFH-server` logs. The Pico W should be able to connect to the `HAFH-server` and publish messages every minute. If you see any errors, please check the configuration files and ensure that the certificates are correctly installed. Once the Pico W is connected to the `HAFH-server` and actively sending messages, you should be good to install the device on your critical GFCI outlet!

## Nuking the Flash

There are some cases where you may want to nuke the flash on the Pico W. For example, if you want to start fresh or if you are experiencing issues with the installation. To do this, install `flash_nuke.uf2` by running:

```bash
./MicroPython/download_picow_nuke.sh
```

This will download the `.uf2` file that wipes everything on the board. To install it, put the Pico W into bootloader mode again and drag and drop the `flash_nuke.uf2` file onto the Pico W drive. This will wipe everything on the board, including the MicroPython firmware. You will need to reflash the MicroPython firmware after this step.

## Resources

- [MicroPython Documentation](https://docs.micropython.org/en/latest/)
- [HAFH-server](https://github.com/lapumb/HAFH-server)
- [HAFH-os](https://github.com/lapumb/HAFH-os)
- [HAFH-client](https://github.com/lapumb/HAFH-client) (TODO: NEED TO UPDATE UPON CREATION OF CLIENT/FRONTEND)
