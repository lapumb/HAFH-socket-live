#!/bin/bash -e

DEFAULT_VERSION="RPI_PICO_W-20250415-v1.25.0.uf2"
USAGE="""$0

Download the latest MicroPython firmware for the Raspberry Pi Pico W.

Options:
    -h --help     Show this help message
    --version <version> Specify the version to download (default: $DEFAULT_VERSION)

Usage:
    $0
    $0 --version $DEFAULT_VERSION
"""

# Parse command line arguments.
VERSION="$DEFAULT_VERSION"
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "$USAGE"
            exit 0
            ;;
        --version)
            shift
            VERSION="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "$USAGE"
            exit 1
            ;;
    esac
done

# Enter this directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $SCRIPT_DIR

# Remove the binary if it already exists.
rm -f $VERSION

echo "Installing MicroPython: $VERSION"
wget https://micropython.org/resources/firmware/$VERSION

echo "Firmware downloaded: $VERSION"
echo "To install the firmware, press and hold the BOOTSEL button on the Pico W while plugging it into your computer. Then, drag and drop the downloaded firmware file onto the Pico W's storage."
