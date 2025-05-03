#!/bin/bash -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

function cleanup {
    cd $SCRIPT_DIR
    rm -rf tmp
}

USAGE="""$0

Upload all Python modules to the board attached to the specified port.

Options:
    --port <port>  Specify the port to use (default: $PI_PORT)
    --py-only      Only upload Python files (default: upload all files, certs included)
    -h --help      Show this help message

Usage:
    $0
    $0 --port /dev/cu.usbmodem11101
    $0 --py-only
    $0 --py-only --port /dev/cu.usbmodem11101
"""

# Enter this directory.
cd $SCRIPT_DIR

# Parse the required environment variables.
source ../.userenv
if [[ -z "$WIFI_SSID" ]]; then
    echo "WIFI_SSID is not set. Please set it in .userenv."
    exit 1
elif [[ -z "$WIFI_PASSWORD" ]]; then
    echo "WIFI_PASSWORD is not set. Please set it in .userenv."
    exit 1
elif [[ -z "$CLIENT_NAME" ]]; then
    echo "CLIENT_NAME is not set. Please set it in .userenv."
    exit 1
elif [[ -z "$MQTT_BROKER_HOSTNAME" ]]; then
    echo "MQTT_BROKER_HOSTNAME is not set. Please set it in .userenv."
    exit 1
fi

PORT="$PI_PORT"
UPLOAD_CERTS=true

# Parse command line arguments.
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            echo "$USAGE"
            exit 0
            ;;
        --port)
            shift
            PORT="$1"
            ;;
        --py-only)
            UPLOAD_CERTS=false
            ;;
        *)
            echo "Unknown option: $1"
            echo "$USAGE"
            exit 1
            ;;
    esac
    shift
done

# Verify a port was specified.
if [[ -z "$PORT" ]]; then
    echo "No port specified. Please specify a port using --port <port> or set the PI_PORT environment variable."
    exit 1
fi

# Check if mpremote is installed.
if ! command -v mpremote &> /dev/null; then
    echo "mpremote is not installed. Please setup your virtual environment and 'pip install -r requirements.txt'"
    exit 1
fi

# Upload the certificates to the board, if required.
if [[ "$UPLOAD_CERTS" == true ]]; then
    echo "Uploading certificates..."
    mpremote connect "$PORT" fs cp -r certs :
fi

# Create a tmp/ directory to store the files since we are modifying them.
rm -rf tmp
mkdir -p tmp
trap cleanup EXIT
cp -r py tmp/py
cd tmp/py

# Determine if we're on macOS or Linux.
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE=(sed -i '')
else
    SED_INPLACE=(sed -i)
fi

# Replace the placeholders in the boot.py and main.py files with the environment variables.
"${SED_INPLACE[@]}" "s|@@WIFI_SSID@@|$WIFI_SSID|g" boot.py
"${SED_INPLACE[@]}" "s|@@WIFI_PASSWORD@@|$WIFI_PASSWORD|g" boot.py
"${SED_INPLACE[@]}" "s|@@CLIENT_NAME@@|$CLIENT_NAME|g" main.py
"${SED_INPLACE[@]}" "s|@@MQTT_BROKER_HOSTNAME@@|$MQTT_BROKER_HOSTNAME|g" main.py

# Upload the files to the board.
echo "Uploading files $(ls -R)."
mpremote connect "$PORT" fs cp -r * :
echo "Uploaded file structure $(mpremote connect "$PORT" fs ls) to $PORT"
