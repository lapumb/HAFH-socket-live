#!/bin/bash -e

# Enter this directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $SCRIPT_DIR

wget https://raw.githubusercontent.com/dwelch67/raspberrypi-pico/main/flash_nuke.uf2
