from requests import get
from os import path as osp
from subprocess import run
from zipfile import ZipFile
from os import makedirs, remove
DEP_DIR = osp.expanduser("~/.zxcvbn")
DEPS = {
    "CydiaSubstrate.framework": "https://cdn.discordapp.com/attachments/1118672500126138550/1123059377264414901/TS-CydiaSubstrate.zip",
    "Cephei.framework": "https://cdn.discordapp.com/attachments/1130557037361770526/1130557602951069816/Cephei.framework.zip",
    "CepheiUI.framework": "https://cdn.discordapp.com/attachments/1130557037361770526/1130557964185501778/CepheiUI.framework.zip",
    "CepheiPrefs.framework":"https://cdn.discordapp.com/attachments/1130557037361770526/1130558249532407968/CepheiPrefs.framework.zip",
    "librocketbootstrap.dylib": "https://cdn.discordapp.com/attachments/1105635370885992458/1125588473466851328/librocketbootstrap.dylib",
    "libmryipc.dylib": "https://cdn.discordapp.com/attachments/1105635370885992458/1120562207458070568/libmryipc.dylib"
}
makedirs(DEP_DIR, exist_ok=True)


def download(dep, link, ftype="z"):
    dl = get(link).content

    if ftype == "z":
        with open((fp := osp.join(DEP_DIR, dep) + ".zip"), "wb") as f:
            f.write(dl)
        with ZipFile(fp) as zf:
            zf.extractall(DEP_DIR)
        remove(fp)
    else:
        with open(osp.join(DEP_DIR, dep), "wb") as f:
            f.write(dl)

    del dl


# `tuple()` avoids a RuntimeError: dictionary changed size during iteration
for dep in tuple(DEPS.keys()):
    if osp.exists(osp.join(DEP_DIR, dep)):
        del DEPS[dep]

if DEPS:
    print(f"[*] downloading missing dependencies ({', '.join(d for d in DEPS)})..")

for dependency, link in DEPS.items():
    if dependency.endswith("k"):
        download(dependency, link)
    else:
        download(dependency, link, "d")

print("\n[*] installing pyzule..")
with open((pz_path := osp.join(DEP_DIR, "pyzule.py")), "wb") as f:
    f.write(get("https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/pyzule.py").content)
print("[?] if prompted, enter your sudo password to finish installation")

run(["sudo", "-p", "'[<] '", "mv", pz_path, "/usr/local/bin/pyzule"])
run(["sudo", "-p", "'[<] '", "chmod", "+x", "/usr/local/bin/pyzule"])
