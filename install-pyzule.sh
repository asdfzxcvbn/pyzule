#!/bin/bash
ARCH=$(uname -m)

if [[ $ARCH == *"iPhone"* ]]; then
    OS="iPhone"
    PATHPREFIX="/var/jb"
    PYZULEURL="https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/pyzule-ios.py"
else
    OS=$(uname)
    PYZULEURL="https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/pyzule.py"
fi

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
    elif [ "$OS" == "iPhone" ]; then
        echo "[*] try looking for python in your package manager!"
    else
        echo "[*] for installation instructions, head over to python.org !"
    fi
    exit 1
fi

mkdir -p ${PZ_DIR}
if [ ! -d ${PZ_DIR}/venv ]; then
    echo "[*] installing required pip libraries.."
    $PYTHON -m venv ${PZ_DIR}/venv > /dev/null

    if [ ! "$OS" == "iPhone" ]; then
        ${PZ_DIR}/venv/bin/pip install -U Pillow orjson requests lief &> /dev/null
    fi
elif [ ! "$OS" == "iPhone" ] && [ ! -f ${PZ_DIR}/requests_upd ]; then
    touch ${PZ_DIR}/requests_upd
    echo "[*] installing new dependencies.."
    ${PZ_DIR}/venv/bin/pip install -U orjson requests &> /dev/null
fi

if [ ! -x "$(command -v ldid)" ]; then
    echo "[*] installing ldid.."
    sudo curl -so ${PATHPREFIX}/usr/local/bin/ldid https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/ldid_${OS}_$ARCH
    sudo chmod +x ${PATHPREFIX}/usr/local/bin/ldid
fi

# ldid error doesnt seem to happen on iOS
if [ ! -x "$(command -v ipsw)" ] && [ "$OS" != "iPhone" ]; then
    echo "[*] installing ipsw.."
    sudo curl -so ${PATHPREFIX}/usr/local/bin/ipsw https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/ipsw_${OS}_$ARCH
    sudo chmod +x ${PATHPREFIX}/usr/local/bin/ipsw
fi

# install_name_tool and otool should only be installed here on linux
if [ ! -x "$(command -v otool)" ]; then
    echo "[*] installing otool.."
    sudo curl -so ${PATHPREFIX}/usr/local/bin/otool https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/otool_$ARCH
    sudo chmod +x ${PATHPREFIX}/usr/local/bin/otool
fi

if [ ! -x "$(command -v install_name_tool)" ]; then
    echo "[*] installing install_name_tool.."
    sudo curl -so ${PATHPREFIX}/usr/local/bin/install_name_tool https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/install_name_tool_$ARCH
    sudo chmod +x ${PATHPREFIX}/usr/local/bin/install_name_tool
fi

# lief is used on desktop, insert_dylib on iOS, so fetch that
if [ "$OS" == "iPhone" ] && [ ! -x "$(command -v insert_dylib)" ]; then
    # this *might* work? should test on both rootful/rootless
    echo "[*] installing insert_dylib.."
    sudo curl -so ${PATHPREFIX}/usr/local/bin/insert_dylib https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/deps/insert_dylib
    sudo chmod +x ${PATHPREFIX}/usr/local/bin/insert_dylib
fi

# create (or update) hidden dir
if [ ! -d ${PZ_DIR}/CydiaSubstrate.framework ]; then
    echo "[*] downloading dependencies.."
    curl -so /tmp/zxcvbn_dir.zip https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/zxcvbn_dir.zip
    unzip -o /tmp/zxcvbn_dir.zip -d ${PZ_DIR} > /dev/null
    rm /tmp/zxcvbn_dir.zip
fi

echo "[*] installing pyzule.."
curl -so ~/.config/pyzule/version.json https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/version.json
sudo rm ${PATHPREFIX}/usr/local/bin/pyzule &> /dev/null  # yeah this is totally required leave me alone
sudo curl -so ${PATHPREFIX}/usr/local/bin/pyzule ${PYZULEURL}
if [ "$OS" == "Linux" ]; then
    sudo sed -i "1s|.*|#\!${PZ_DIR}/venv/bin/python|" ${PATHPREFIX}/usr/local/bin/pyzule
else
    sudo sed -e "1s|.*|#\!${PZ_DIR}/venv/bin/python|" -i "" ${PATHPREFIX}/usr/local/bin/pyzule &> /dev/null  # bsd sed is broken asf
fi
echo "[*] fixed interpreter path!"
sudo chmod +x ${PATHPREFIX}/usr/local/bin/pyzule
echo "[*] done!"
