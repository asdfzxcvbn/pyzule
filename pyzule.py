#!/usr/bin/env python3
import argparse
import sys
import os
from shutil import rmtree, copyfile, copytree, move
from subprocess import run, DEVNULL
from plistlib import load, dump
from platform import system
from zipfile import ZipFile
from atexit import register
from time import time
from glob import glob
from PIL import Image
WORKING_DIR = os.getcwd()
USER_DIR = os.path.expanduser("~/.zxcvbn")
changed = 0

# check os compatibility
system = system()
if system == "Windows":
    print("windows is not currently supported. install wsl and use pyzule there.")
    sys.exit(1)

# set/get all args
parser = argparse.ArgumentParser(description="an azule \"clone\" written in python3.")
parser.add_argument("-i", metavar="ipa", type=str, required=True,
                    help="the ipa to patch")
parser.add_argument("-o", metavar="output", type=str, required=True,
                    help="the name of the patched ipa that will be created")
parser.add_argument("-n", metavar="name", type=str, required=False,
                    help="modify the app's name")
parser.add_argument("-v", metavar="version", type=str, required=False,
                    help="modify the app's version")
parser.add_argument("-b", metavar="bundle id", type=str, required=False,
                    help="modify the app's bundle id")
parser.add_argument("-c", metavar="level", type=int, default=3,
                    help="the compression level of the output ipa (default is 3)",
                    action="store", choices=range(1, 10),
                    nargs="?", const=1)
parser.add_argument("-k", metavar="icon", type=str, required=False,
                    help="an image file to use as the app icon (may not work due to springboard caching)")
parser.add_argument("-r", metavar="url", type=str, required=False,
                    help="url schemes to add", nargs="+")
parser.add_argument("-f", metavar="files", nargs="+", type=str,
                    help="tweak files to inject into the ipa")
parser.add_argument("-u", action="store_true",
                    help="remove UISupportedDevices")
parser.add_argument("-w", action="store_true",
                    help="remove watch app")
parser.add_argument("-m", action="store_true",
                    help="set MinimumOSVersion to iOS 10.0")
parser.add_argument("-d", action="store_true",
                    help="enable files access")
parser.add_argument("-s", action="store_true",
                    help="fakesigns the ipa (for use with appsync)")
parser.add_argument("-e", action="store_true",
                    help="remove app extensions")
parser.add_argument("-p", action="store_true",
                    help="inject into @executable_path")
args = parser.parse_args()

# checking received args
if not args.i.endswith(".ipa") or not args.o.endswith(".ipa"):
    parser.error("the input and output file must be an ipa")
elif not os.path.exists(args.i):
    parser.error(f"{args.i} does not exist")
elif not any((args.f, args.u, args.w, args.m, args.d, args.n, args.v, args.b, args.s, args.e, args.r, args.k)):
    parser.error("at least one option to modify the ipa must be present")
if os.path.exists(args.o):
    overwrite = input(f"[<] {args.o} already exists. overwrite? [Y/n] ").lower().strip()
    if overwrite in ("y", "yes", ""):
        del overwrite
    else:
        print("[>] quitting.")
        sys.exit()
EXTRACT_DIR = f".pyzule-{time()}"
REAL_EXTRACT_DIR = os.path.join(os.getcwd(), EXTRACT_DIR)
if args.p:
    inject_path = ""  # @executable_path
    inject_path_exec = "@executable_path"
    print("[*] will inject into @executable_path")
else:
    inject_path = "Frameworks"  # @rpath
    inject_path_exec = "@rpath"


def check_cryptid(EXEC_PATH):
    crypt = str(run(f"otool -l {EXEC_PATH}", capture_output=True, check=True, shell=True)).split("\\n")
    if any("cryptid 1" in line for line in crypt):
        print("[!] app is encrypted, injecting and fakesigning not available")
        print("[!] run your pyzule command again without -f or -s")
        sys.exit(1)


def get_icons(icon_type, plist, app_path, icons):
    for icon in plist[icon_type]["CFBundlePrimaryIcon"]["CFBundleIconFiles"]:
        icons.update(i for i in glob(os.path.join(app_path, icon + "*.png")))
    return icons


def cleanup():
    print("[*] deleting temporary directory..")
    rmtree(REAL_EXTRACT_DIR)


register(cleanup)


# extracting ipa
print("[*] extracting ipa..")
with ZipFile(args.i, "r") as ipa:
    ipa.extractall(path=EXTRACT_DIR)
print("[*] extracted ipa successfully")

# checking if everything exists (to see if it's a valid ipa)
try:
    APP_PATH = glob(os.path.join(EXTRACT_DIR, "Payload", "*.app"))[0]
    PLIST_PATH = glob(os.path.join(APP_PATH, "Info.plist"))[0]
except IndexError:
    print("[!] couldn't find Payload folder and/or Info.plist file, invalid ipa specified")
    sys.exit(1)


# injecting stuff
if args.f:
    with open(PLIST_PATH, "rb") as pl:
        BINARY = load(pl)["CFBundleExecutable"]
    BINARY_PATH = os.path.join(APP_PATH, BINARY).replace(" ", r"\ ")
    ENTITLEMENTS_FILE = os.path.join(APP_PATH, "pyzule_entitlements").replace(" ", r"\ ")
    check_cryptid(BINARY_PATH)
    run(f"ldid -S -M {BINARY_PATH}", shell=True, check=True)
    DYLIBS_PATH = os.path.join(REAL_EXTRACT_DIR, "pyzule-inject")
    os.makedirs(DYLIBS_PATH, exist_ok=True)  # we'll copy everything we modify (dylibs) here to not mess with the original files

    if any(i.endswith(".appex") for i in args.f):
        os.makedirs(os.path.join(APP_PATH, "PlugIns"), exist_ok=True)

    if any(i.endswith(known) for i in args.f for known in (".deb", ".dylib", ".framework")):
        if inject_path:
            os.makedirs(os.path.join(APP_PATH, "Frameworks"), exist_ok=True)
            run(f"install_name_tool -add_rpath @executable_path/Frameworks {BINARY_PATH}", shell=True, stdout=DEVNULL, stderr=DEVNULL)   # skipcq: PYL-W1510
        deb_counter = 0

    dylibs = [d for d in args.f if d.endswith(".dylib")]
    id_injected = dylibs + [f for f in args.f if ".framework" in f and "CydiaSubstrate.framework" not in f]
    substrate_injected = 0
    rocketbootstrap_injected = 0
    mryipc_injected = 0

    # extracting all debs
    for deb in args.f:
        if not deb.endswith(".deb"):
            continue
        bn = os.path.basename(deb)
        output = os.path.join(EXTRACT_DIR, str(deb_counter))
        os.makedirs(output)
        os.makedirs(os.path.join(output, "e"))
        if system == "Linux":
            run(["ar", "-x", deb, f"--output={output}"], check=True)
        else:
            run(["tar", "-xf", deb, "-C", output], check=True)
        data_tar = glob(os.path.join(output, "data.*"))[0]
        run(["tar", "-xf", data_tar, "-C", os.path.join(output, "e")], check=True)
        for dirpath, dirnames, filenames in os.walk(os.path.join(output, "e")):
            for filename in filenames:
                if filename.endswith(".dylib"):
                    src_path = os.path.join(dirpath, filename)
                    dest_path = os.path.join(DYLIBS_PATH, filename)
                    if not os.path.exists(dest_path):
                        move(src_path, dest_path)
                    dylibs.append(filename)
                    id_injected.append(filename)
            for dirname in dirnames:
                if dirname.endswith(".bundle") or dirname.endswith(".framework"):
                    src_path = os.path.join(dirpath, dirname)
                    dest_path = os.path.join(DYLIBS_PATH, dirname)
                    if not os.path.exists(dest_path):
                        move(src_path, dest_path)
                    args.f.append(dirname)
                    if ".framework" in dirname:
                        id_injected.append(dirname)
                if "preferenceloader" in dirname.lower():
                    print("[!] found dependency on PreferenceLoader, ipa will not work jailed")
        print(f"[*] extracted {bn} successfully")
        deb_counter += 1

    # remove codesign + fix all dependencies
    for dylib in dylibs:
        dylib_bn = os.path.basename(dylib)
        actual_path = os.path.join(DYLIBS_PATH, dylib_bn)
        try:
            copyfile(dylib, actual_path)
        except FileNotFoundError:
            pass
        run(f"ldid -S -M '{actual_path}'", shell=True, check=True)
        run(f"install_name_tool -id {inject_path_exec}/{dylib_bn} '{actual_path}'", shell=True, check=True)
        deps_temp = run(f"otool -L '{actual_path}'", shell=True, capture_output=True, text=True, check=True).stdout.strip().split("\n")[2:]
        for ind, dep in enumerate(deps_temp):
            if "(architecture " in dep:
                deps_temp = deps_temp[:ind]
                break

        deps = []
        for dep in deps_temp:
            if any(dep.startswith(s) for s in ("\t/Library/", "\t/usr/lib/", "\t@rpath", "\t@executable_path")):
                deps.append(dep.split()[0])

        for dep in deps_temp:
            dep = dep.split()[0]

            if "substrate" in dep.lower():
                run(f"install_name_tool -change {dep} {inject_path_exec}/CydiaSubstrate.framework/CydiaSubstrate '{actual_path}'", shell=True, check=True)

                if not substrate_injected:
                    if not os.path.exists(os.path.join(APP_PATH, inject_path, "CydiaSubstrate.framework")):
                        copytree(os.path.join(USER_DIR, "CydiaSubstrate.framework"), os.path.join(APP_PATH, inject_path, "CydiaSubstrate.framework"))
                    print("[*] injected CydiaSubstrate.framework")
                    substrate_injected = 1

                if dep != f"{inject_path_exec}/CydiaSubstrate.framework/CydiaSubstrate":
                    print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/CydiaSubstrate.framework/CydiaSubstrate")

            if "librocketbootstrap" in dep.lower():
                run(f"install_name_tool -change {dep} {inject_path_exec}/librocketbootstrap.dylib '{actual_path}'", shell=True, check=True)

                if not rocketbootstrap_injected:
                    if not os.path.exists(os.path.join(APP_PATH, inject_path, "librocketbootstrap.dylib")):
                        copyfile(os.path.join(USER_DIR, "librocketbootstrap.dylib"), os.path.join(APP_PATH, inject_path, "librocketbootstrap.dylib"))
                    print("[*] injected librocketbootstrap.dylib")
                    rocketbootstrap_injected = 1

                if dep != f"{inject_path_exec}/librocketbootstrap.dylib":
                    print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/librocketbootstrap.dylib")

            if "libmryipc" in dep.lower():
                run(f"install_name_tool -change {dep} {inject_path_exec}/libmryipc.dylib '{actual_path}'", shell=True, check=True)

                if not mryipc_injected:
                    if not os.path.exists(os.path.join(APP_PATH, inject_path, "libmryipc.dylib")):
                        copyfile(os.path.join(USER_DIR, "libmryipc.dylib"), os.path.join(APP_PATH, inject_path, "libmryipc.dylib"))
                    print("[*] injected libmryipc.dylib")
                    mryipc_injected = 1

                if dep != f"{inject_path_exec}/libmryipc.dylib":
                    print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/libmryipc.dylib")

        for dep in deps:
            for known in id_injected:
                if os.path.basename(known) in dep:
                    bn = os.path.basename(dep)

                    if f"{inject_path_exec}/{bn}" in dep:
                        continue

                    if dep.endswith(".dylib"):
                        run(f"install_name_tool -change {dep} {inject_path_exec}/{bn} '{actual_path}'", shell=True, check=True)
                        print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/{bn}")
                    elif ".framework" in dep:
                        run(f"install_name_tool -change {dep} {inject_path_exec}/{bn}.framework/{bn} '{actual_path}'", shell=True, check=True)
                        print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/{bn}.framework/{bn}")

    for d in dylibs:
        actual_path = os.path.join(DYLIBS_PATH, os.path.basename(d))
        bn = os.path.basename(d)
        run(f"insert_dylib --inplace --no-strip-codesig --all-yes '{inject_path_exec}/{bn}' {BINARY_PATH}", shell=True, stdout=DEVNULL, check=True)
        try:
            copyfile(actual_path, os.path.join(APP_PATH, inject_path, bn))
        except FileExistsError:
            pass
        print(f"[*] successfully injected {bn}")
    for tweak in args.f:
        bn = os.path.basename(tweak)
        actual_path = os.path.join(DYLIBS_PATH, os.path.basename(tweak))
        try:
            if tweak.endswith(".framework") and "CydiaSubstrate" not in tweak:
                try:
                    copytree(tweak, os.path.join(APP_PATH, inject_path, bn))
                except FileNotFoundError:
                    copytree(actual_path, os.path.join(APP_PATH, inject_path, bn))
                run(f"insert_dylib --inplace --no-strip-codesig --all-yes {inject_path_exec}/{bn}/{bn[:-10]} {BINARY_PATH}", shell=True, stdout=DEVNULL, check=True)
                print(f"[*] successfully injected {bn}")
            elif tweak.endswith(".appex"):
                copytree(tweak, os.path.join(APP_PATH, "PlugIns", bn))
                print(f"[*] successfully copied {bn} to PlugIns")
            elif tweak not in dylibs and not tweak.endswith(".deb") and "CydiaSubstrate" not in tweak:
                try:
                    if os.path.isdir(tweak):
                        copytree(tweak, os.path.join(APP_PATH, bn))
                    else:
                        copyfile(tweak, os.path.join(APP_PATH, bn))
                except FileNotFoundError:
                    if os.path.isdir(actual_path):
                        copytree(actual_path, os.path.join(APP_PATH, bn))
                    else:
                        copyfile(actual_path, os.path.join(APP_PATH, bn))
                print(f"[*] successfully copied {bn} to app root")
        except FileExistsError:
            continue
    changed = 1

with open(PLIST_PATH, "rb") as p:
    plist = load(p)

# removing UISupportedDevices (if specified)
if args.u:
    try:
        del plist["UISupportedDevices"]
        print("[*] removed UISupportedDevices")
        changed = 1
    except KeyError:
        print("[?] UISupportedDevices not present")

# removing watch app (if specified)
if args.w:
    try:
        rmtree(os.path.join(APP_PATH, "Watch"))
        print("[*] removed watch app")
        changed = 1
    except FileNotFoundError:
        print("[?] watch app not present")

# set minimum os version (if specified)
if args.m:
    plist["MinimumOSVersion"] = "10.0"
    print("[*] set MinimumOSVersion to iOS 10.0")
    changed = 1

# enable documents support
if args.d:
    plist["UISupportsDocumentBrowser"] = True
    plist["UIFileSharingEnabled"] = True
    print("[*] enabled documents support")
    changed = 1

# change app name
if args.n:
    plist["CFBundleDisplayName"] = args.n
    print(f"[*] changed app name to {args.n}")
    changed = 1

# change app version
if args.v:
    plist["CFBundleShortVersionString"] = args.v
    plist["CFBundleVersion"] = args.v
    print(f"[*] changed app version to {args.v}")
    changed = 1

# change app bundle id
if args.b:
    orig_bundle = plist["CFBundleIdentifier"]
    print(f"[*] original bundle id is {orig_bundle}")
    plist["CFBundleIdentifier"] = args.b
    for ext in glob(os.path.join(APP_PATH, "PlugIns", "*.appex")):
        ext_plist = os.path.join(ext, "Info.plist")
        with open(ext_plist, "rb") as ap:
            appex_plist = load(ap)
        appex_plist["CFBundleIdentifier"] = appex_plist["CFBundleIdentifier"].replace(orig_bundle, args.b)
        with open(ext_plist, "wb") as done:
            dump(appex_plist, done)
        print(f"[*] changed {os.path.basename(ext)} bundle id to {appex_plist['CFBundleIdentifier']}")
    print(f"[*] changed app bundle id to {args.b}")
    changed = 1

# add url schemes to the app
if args.r:
    SCHEMES = [scheme.replace("://", "") for scheme in args.r]
    if "CFBundleURLTypes" not in plist:
        plist["CFBundleURLTypes"] = []
    plist["CFBundleURLTypes"].append({
        "CFBundleURLName": "fyi.zxcvbn.pyzule",
        "CFBundleURLSchemes": SCHEMES
    })
    print("[*] added url schemes:", ", ".join(SCHEMES))
    changed = 1

if args.k:
    IMG_PATH = os.path.join(EXTRACT_DIR, "pyzule_img.png")

    # convert to png
    if not args.k.endswith(".png"):
        with Image.open(args.k) as img:
            img.save(IMG_PATH, "PNG")
    else:
        copyfile(args.k, IMG_PATH)

    icons = set()  # set of paths to every icon file

    if "CFBundleIcons" in plist:
        icons = get_icons("CFBundleIcons", plist, APP_PATH, icons)
    if "CFBundleIcons~ipad" in plist:
        icons = get_icons("CFBundleIcons~ipad", plist, APP_PATH, icons)

    for icon in icons:
        with Image.open(icon) as img:
            width, height = img.size
        os.remove(icon)
        with Image.open(IMG_PATH) as img:
            img.resize((width, height)).save(icon)

    print("[*] updated app icon")
    changed = 1 

with open(PLIST_PATH, "wb") as p:
    dump(plist, p)

if args.s:
    with open(PLIST_PATH, "rb") as pl:
        BINARY = load(pl)["CFBundleExecutable"]
    BINARY_PATH = os.path.join(APP_PATH, BINARY).replace(" ", r"\ ")
    check_cryptid(BINARY_PATH)
    run(f"ldid -S -M {BINARY_PATH}", shell=True, check=True)
    print(f"[*] fakesigned {BINARY}")

    PATTERNS = (
        "*.dylib", "*.framework",
        os.path.join("PlugIns", "*.appex"),
        os.path.join("Frameworks", "*.dylib"),
        os.path.join("Frameworks", "*.framework")
    )
    tfs = sum((glob(os.path.join(APP_PATH, p)) for p in PATTERNS), [])

    for fs in tfs:
        bn = os.path.basename(fs)
        if ".framework" in fs:
            run(f"ldid -S -M '{os.path.join(fs, bn[:-10])}'", shell=True, check=True)
        elif ".appex" in fs:
            run(f"ldid -S -M '{os.path.join(fs, bn[:-6])}'", shell=True, check=True)
        else:
            run(f"ldid -S -M '{fs}'", shell=True, check=True)
        print(f"[*] fakesigned {bn}")
    changed = 1

if args.e:
    try:
        rmtree(os.path.join(APP_PATH, "PlugIns"))
        print("[*] removed app extensions")
        changed = 1
    except FileNotFoundError:
        print("[?] no app extensions to remove")

# checking if anything was actually changed
if not changed:
    print("[!] nothing was changed, output file will not be created")
    sys.exit()

# zipping everything back into an ipa
os.chdir(EXTRACT_DIR)
print(f"[*] generating ipa using compression level {args.c}..")
run(f"zip -{args.c} -r '{os.path.basename(args.o)}' Payload", shell=True, stdout=DEVNULL, check=True)

# cleanup when everything is done
os.chdir(WORKING_DIR)
if "/" in args.o:
    os.makedirs(args.o.replace(os.path.basename(args.o), ""), exist_ok=True)
move(os.path.join(EXTRACT_DIR, os.path.basename(args.o)), args.o)
print(f"[*] generated ipa at {args.o}")
