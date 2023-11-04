#!/bin/bash

# check if python is `python` or `python3`
if [ -x "$(command -v python3)" ]; then
    PYTHON=python3
elif [ -x "$(command -v python)" ]; then
    PYTHON=python
elif [ ! -x "$(command -v unzip)" ]; then
    echo "[!] unzip is not installed."
    exit 1
else
    echo "[!] couldn't find \"python\" nor \"python3\" installed."
    if [ "$(uname)" == "Linux" ]; then
        echo "[*] try \"sudo apt install python3 python3-pip\" or \"sudo pacman -S python python-pip\" depending on your distro."
    else
        echo "[*] for installation instructions, head over to python.org !"
    fi
    exit 1
fi

# check for pip
$PYTHON -m pip &> /dev/null
if [ $? -ne 0 ]; then
    echo "[!] pip check failed! are you sure you have pip installed?"
    exit 1
fi

echo "[*] installing required libraries.."
$PYTHON -m pip install requests Pillow > /dev/null

# create (or update) hidden dir
if [ ! -d ~/.zxcvbn ] || [ $(ls -1 ~/.zxcvbn | wc -l) -ne 8 ]; then
    echo "[*] downloading dependencies.."
    wget -qO /tmp/zxcvbn_dir.zip https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/zxcvbn_dir.zip > /dev/null
    unzip -o /tmp/zxcvbn_dir.zip -d ~/.zxcvbn > /dev/null
fi

echo "[*] installing pyzule.."
sudo rm /usr/local/bin/pyzule &> /dev/null  # yeah this is totally required leave me alone
sudo wget -qO /usr/local/bin/pyzule https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/pyzule.py
sudo sed -i "1s/.*/#!\/usr\/bin\/env $PYTHON/" /usr/local/bin/pyzule
echo "[*] fixed interpreter path!"
sudo chmod +x /usr/local/bin/pyzule
echo "[*] done!"
