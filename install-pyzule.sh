#!/bin/bash
OS=$(uname)
ARCH=$(uname -m)

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
    if [ "$OS" == "Linux" ]; then
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

echo "[*] installing required pip libraries.."
mkdir -p ~/.zxcvbn
if [ ! -d ~/.zxcvbn/venv ]; then
    $PYTHON -m venv ~/.zxcvbn/venv > /dev/null
fi
~/.zxcvbn/venv/bin/pip install -U requests Pillow &> /dev/null
~/.zxcvbn/venv/bin/pip install --index-url https://lief.s3-website.fr-par.scw.cloud/latest lief &> /dev/null

if [ ! -x "$(command -v ldid)" ]; then
    echo "[*] installing ldid.."

    # im not even going to try to improve this, cry about it
    if [ "$OS" == "Linux" ]; then
        sudo curl -so /usr/local/bin/ldid https://github.com/ProcursusTeam/ldid/releases/download/v2.1.5-procursus7/ldid_linux_$ARCH
    else
        sudo curl -so /usr/local/bin/ldid https://github.com/ProcursusTeam/ldid/releases/download/v2.1.5-procursus7/ldid_macosx_$ARCH
    fi

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
if [ ! -d ~/.zxcvbn ] || [ $(ls -1 ~/.zxcvbn | wc -l) -ne 8 ]; then
    echo "[*] downloading dependencies.."
    curl -so /tmp/zxcvbn_dir.zip https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/zxcvbn_dir.zip
    unzip -o /tmp/zxcvbn_dir.zip -d ~/.zxcvbn > /dev/null
fi

echo "[*] installing pyzule.."
sudo rm /usr/local/bin/pyzule &> /dev/null  # yeah this is totally required leave me alone
sudo curl -so /usr/local/bin/pyzule https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/pyzule.py
sudo sed -i "1s/.*/#!\\$HOME\/.zxcvbn\/venv\/bin\/python/" /usr/local/bin/pyzule
echo "[*] fixed interpreter path!"
sudo chmod +x /usr/local/bin/pyzule
echo "[*] done!"
