#!/bin/bash
OS=$(uname)
ARCH=$(uname -m)
PZ_DIR=${HOME}/.config/pyzule

# check which python we should use
if [ -x "$(command -v python3.12)" ]; then
    PYTHON=python3.12
elif [ -x "$(command -v python3)" ]; then
    PYTHON=python3
elif [ -x "$(command -v python)" ]; then
    PYTHON=python
elif [ ! -x "$(command -v unzip)" ]; then
    echo "[!] unzip is not installed."
    exit 1
else
    echo "[!] couldn't find \"python\" nor \"python3\" installed."
    if [ "$OS" == "Linux" ]; then
        echo "[*] try \"sudo apt install python3 python3-pip python3-venv\" or \"sudo pacman -S python python-pip\" depending on your distro."
    else
        echo "[*] for installation instructions, head over to python.org !"
    fi
    exit 1
fi

mkdir -p ${PZ_DIR}
if [ ! -d ${PZ_DIR}/venv ]; then
    echo "[*] installing required pip libraries.."
    $PYTHON -m venv ${PZ_DIR}/venv > /dev/null
    ${PZ_DIR}/venv/bin/pip install -U Pillow lief &> /dev/null
fi

if [ ! -x "$(command -v ldid)" ]; then
    echo "[*] installing ldid.."
    sudo curl -so /usr/local/bin/ldid https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/ldid_${OS}_$ARCH
    sudo chmod +x /usr/local/bin/ldid
fi

# install_name_tool and otool should only be installed here on linux
if [ ! -x "$(command -v otool)" ]; then
    echo "[*] installing otool.."
    sudo curl -so /usr/local/bin/otool https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/otool_$ARCH
    sudo chmod +x /usr/local/bin/otool
fi

if [ ! -x "$(command -v install_name_tool)" ]; then
    echo "[*] installing install_name_tool.."
    sudo curl -so /usr/local/bin/install_name_tool https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/install_name_tool_$ARCH
    sudo chmod +x /usr/local/bin/install_name_tool
fi

# create (or update) hidden dir
if [ ! -d ${PZ_DIR}/CydiaSubstrate.framework ]; then
    echo "[*] downloading dependencies.."
    curl -so /tmp/zxcvbn_dir.zip https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/zxcvbn_dir.zip
    unzip -o /tmp/zxcvbn_dir.zip -d ${PZ_DIR} > /dev/null
    rm /tmp/zxcvbn_dir.zip
fi

echo "[*] installing pyzule.."
sudo rm /usr/local/bin/pyzule &> /dev/null  # yeah this is totally required leave me alone
sudo curl -so /usr/local/bin/pyzule https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/pyzule.py
sudo sed -i "1s|.*|#\!${PZ_DIR}/venv/bin/python|" /usr/local/bin/pyzule
echo "[*] fixed interpreter path!"
sudo chmod +x /usr/local/bin/pyzule
echo "[*] done!"
