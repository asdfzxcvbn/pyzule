#!/usr/bin/env python3
import os
import sys
import argparse
from PIL import Image
from glob import glob
from time import time
from atexit import register
from zipfile import ZipFile
from platform import system
from plistlib import load, dump
from subprocess import run, DEVNULL
from shutil import rmtree, copyfile, copytree, move
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
                    help="the .ipa/.app to patch")
parser.add_argument("-o", metavar="output", type=str, required=True,
                    help="the name of the patched .ipa/.app that will be created")
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
parser.add_argument("-x", metavar="entitlements", type=str, required=False,
                    help="a file containing entitlements to sign the app with")
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

# sanitize paths
args.i = os.path.normpath(args.i)
args.o = os.path.normpath(args.o)

# checking received args
if not (args.i.endswith(".ipa") or os.path.basename(args.i).endswith(".app")) or not (args.o.endswith(".ipa") or os.path.basename(args.o).endswith(".app")):
    parser.error("the input and output file must be a .ipa (file) or .app (folder)")
elif not os.path.exists(args.i):
    parser.error(f"{args.i} does not exist")
elif not any((args.f, args.u, args.w, args.m, args.d, args.n, args.v, args.b, args.s, args.e, args.r, args.k, args.x)):
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


def get_plist(path, entry=None):
    with open(path, "rb") as f:
        if entry is None:
            return load(f)
        else:
            try:
                return load(f)[entry]
            except (IndexError, KeyError):
                return None


def dump_plist(path, new):
    with open(path, "wb") as f:
        dump(new, f)


def change_plist(success, error, plist, condition, *keys):
    try:
        if all(plist[key] == condition for key in keys):
            print(f"[?] {error}")
        else:
            raise KeyError
    except KeyError:
        for key in keys:
            plist[key] = condition
        print(f"[*] {success}")
        global changed
        changed = 1


def cleanup():
    print("[*] deleting temporary directory..")
    rmtree(REAL_EXTRACT_DIR)


register(cleanup)


# extracting ipa
INPUT_IS_IPA = 1 if args.i.endswith(".ipa") else 0
OUTPUT_IS_IPA = 1 if args.o.endswith(".ipa") else 0
if INPUT_IS_IPA:
    print("[*] extracting ipa..")
    with ZipFile(args.i, "r") as ipa:
        ipa.extractall(path=EXTRACT_DIR)
    print("[*] extracted ipa successfully")

# checking if everything exists (to see if it's a valid ipa)
try:
    INPUT_BASENAME = os.path.basename(args.i)
    if INPUT_IS_IPA:
        APP_PATH = glob(os.path.join(EXTRACT_DIR, "Payload", "*.app"))[0]
    else:
        print("[*] copying app to temporary directory..")
        copytree(args.i, os.path.join(EXTRACT_DIR, INPUT_BASENAME))
        print("[*] copied app")
        APP_PATH = glob(os.path.join(EXTRACT_DIR, INPUT_BASENAME))[0]
    PLIST_PATH = glob(os.path.join(APP_PATH, "Info.plist"))[0]
except IndexError:
    print("[!] couldn't find Payload folder and/or Info.plist file, invalid ipa/app specified")
    sys.exit(1)

# remove app extensions
if args.e:
    try:
        rmtree(os.path.join(APP_PATH, "PlugIns"))
        print("[*] removed app extensions")
        changed = 1
    except FileNotFoundError:
        print("[?] no app extensions to remove")

# injecting stuff
if args.f:
    BINARY = get_plist(PLIST_PATH, "CFBundleExecutable")
    BINARY_PATH = os.path.join(APP_PATH, BINARY).replace(" ", r"\ ")
    check_cryptid(BINARY_PATH)
    run(f"ldid -S -M {BINARY_PATH}", shell=True, check=True)
    DYLIBS_PATH = os.path.join(REAL_EXTRACT_DIR, "pyzule-inject")
    os.makedirs(DYLIBS_PATH, exist_ok=True)  # we'll copy everything we modify (dylibs) here to not mess with the original files

    args.f = [os.path.normpath(np) for np in args.f]

    if any(i.endswith(".appex") for i in args.f):
        os.makedirs(os.path.join(APP_PATH, "PlugIns"), exist_ok=True)

    if any(i.endswith(known) for i in args.f for known in (".deb", ".dylib", ".framework")):
        if inject_path:
            os.makedirs(os.path.join(APP_PATH, "Frameworks"), exist_ok=True)
            run(f"install_name_tool -add_rpath @executable_path/Frameworks {BINARY_PATH}", shell=True, stdout=DEVNULL, stderr=DEVNULL)   # skipcq: PYL-W1510
        deb_counter = 0

    dylibs = {d for d in args.f if d.endswith(".dylib")}
    id_injected = {f for f in args.f if ".framework" in f and "CydiaSubstrate.framework" not in f}
    id_injected.update(dylibs)
    substrate_injected = 0
    rocketbootstrap_injected = 0
    mryipc_injected = 0

    # extracting all debs
    for deb in set(args.f):
        if not deb.endswith(".deb"):
            continue
        bn = os.path.basename(deb)
        output = os.path.join(EXTRACT_DIR, str(deb_counter))
        os.makedirs(output)
        os.makedirs(os.path.join(output, "e"))
        if system == "Linux":
            run(f"ar -x {deb} --output={output}", shell=True, check=True)
        else:
            run(f"tar -xf {deb} -C {output}", shell=True, check=True)
        data_tar = glob(os.path.join(output, "data.*"))[0]
        run(["tar", "-xf", data_tar, "-C", os.path.join(output, "e")], check=True)
        for dirpath, dirnames, filenames in os.walk(os.path.join(output, "e")):
            for filename in filenames:
                if filename.endswith(".dylib"):
                    src_path = os.path.join(dirpath, filename)
                    dest_path = os.path.join(DYLIBS_PATH, filename)
                    if not os.path.exists(dest_path):
                        move(src_path, dest_path)
                    dylibs.add(filename)
                    id_injected.add(filename)
            for dirname in dirnames:
                if dirname.endswith(".bundle") or dirname.endswith(".framework"):
                    src_path = os.path.join(dirpath, dirname)
                    dest_path = os.path.join(DYLIBS_PATH, dirname)
                    if not os.path.exists(dest_path):
                        move(src_path, dest_path)
                    args.f.append(dirname)
                    if ".framework" in dirname:
                        id_injected.add(dirname)
                if "preferenceloader" in dirname.lower():
                    print(f"[!] found dependency on PreferenceLoader in {deb}, ipa might not work jailed")
        print(f"[*] extracted {bn} successfully")
        deb_counter += 1

    args.f = set(args.f)

    # remove codesign + fix all dependencies
    for dylib in dylibs:
        dylib_bn = os.path.basename(dylib)
        actual_path = os.path.join(DYLIBS_PATH, dylib_bn)
        try:
            copyfile(dylib, actual_path)
        except FileNotFoundError:
            pass
        run(f"ldid -S -M '{actual_path}'", shell=True, check=True)
        run(f"install_name_tool -id {inject_path_exec}/{dylib_bn} '{actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
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
            dep_actual_path = os.path.join(APP_PATH, inject_path, os.path.basename(dep))

            if "substrate" in dep.lower():
                run(f"install_name_tool -change {dep} {inject_path_exec}/CydiaSubstrate.framework/CydiaSubstrate '{actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)

                if not substrate_injected:
                    if not os.path.exists(os.path.join(APP_PATH, inject_path, "CydiaSubstrate.framework")):
                        copytree(os.path.join(USER_DIR, "CydiaSubstrate.framework"), os.path.join(APP_PATH, inject_path, "CydiaSubstrate.framework"))
                        print("[*] injected CydiaSubstrate.framework")
                    else:
                        print("[*] existing CydiaSubstrate.framework found")
                    substrate_injected = 1

                if dep != f"{inject_path_exec}/CydiaSubstrate.framework/CydiaSubstrate":
                    print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/CydiaSubstrate.framework/CydiaSubstrate")

            if "librocketbootstrap" in dep.lower():
                run(f"install_name_tool -change {dep} {inject_path_exec}/librocketbootstrap.dylib '{actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)

                if not rocketbootstrap_injected:
                    if not os.path.exists(os.path.join(APP_PATH, inject_path, "librocketbootstrap.dylib")):
                        copyfile(os.path.join(USER_DIR, "librocketbootstrap.dylib"), os.path.join(APP_PATH, inject_path, "librocketbootstrap.dylib"))
                        if not os.path.exists(os.path.join(APP_PATH, inject_path, "CydiaSubstrate.framework")):
                            copytree(os.path.join(USER_DIR, "CydiaSubstrate.framework"), os.path.join(APP_PATH, inject_path, "CydiaSubstrate.framework"))
                            print("[*] injected CydiaSubstrate.framework")
                        substrate_injected = 1
                        print("[*] injected librocketbootstrap.dylib")
                    if not inject_path:
                        run(f"install_name_tool -change @rpath/CydiaSubstrate.framework/CydiaSubstrate @executable_path/CydiaSubstrate.framework/CydiaSubstrate '{dep_actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
                    rocketbootstrap_injected = 1

                if dep != f"{inject_path_exec}/librocketbootstrap.dylib":
                    print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/librocketbootstrap.dylib")

            if "libmryipc" in dep.lower():
                run(f"install_name_tool -change {dep} {inject_path_exec}/libmryipc.dylib '{actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)

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
                        run(f"install_name_tool -change {dep} {inject_path_exec}/{bn} '{actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
                        print(f"[*] fixed dependency in {os.path.basename(dylib)}: {dep} -> {inject_path_exec}/{bn}")
                    elif ".framework" in dep:
                        run(f"install_name_tool -change {dep} {inject_path_exec}/{bn}.framework/{bn} '{actual_path}'", shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
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
            if bn.endswith(".framework") and "cydiasubstrate" not in bn.lower():
                try:
                    copytree(tweak, os.path.join(APP_PATH, inject_path, bn))
                    framework_exec = get_plist(os.path.join(tweak, "Info.plist"), "CFBundleExecutable")
                except FileNotFoundError:
                    copytree(actual_path, os.path.join(APP_PATH, inject_path, bn))
                    framework_exec = get_plist(os.path.join(actual_path, "Info.plist"), "CFBundleExecutable")
                run(f"insert_dylib --inplace --no-strip-codesig --all-yes {inject_path_exec}/{bn}/{framework_exec} {BINARY_PATH}", shell=True, stdout=DEVNULL, check=True)
                print(f"[*] successfully injected {bn}")
            elif bn.endswith(".appex"):
                copytree(tweak, os.path.join(APP_PATH, "PlugIns", bn))
                print(f"[*] successfully copied {bn} to PlugIns")
            elif tweak not in dylibs and not bn.endswith(".deb") and "cydiasubstrate" not in tweak.lower():
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

plist = get_plist(PLIST_PATH)

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
    WATCH_APPS = tuple(os.path.join(APP_PATH, watchapp) for watchapp in ("Watch", "WatchKit", "com.apple.WatchPlaceholder"))
    removed_watch = 0

    for watch in WATCH_APPS:
        try:
            rmtree(watch)
            removed_watch = 1
        except FileNotFoundError:
            continue
    
    if removed_watch:
        print("[*] removed watch app")
        changed = 1
    else:
        print("[?] watch app not present")

# set minimum os version (if specified)
if args.m:
    change_plist("set MinimumOSVersion to iOS 10.0", "MinimumOSVersion was already 10.0",
                plist, "10.0", "MinimumOSVersion")

# enable documents support
if args.d:
    change_plist("enabled documents support", "documents support was already enabled",
                plist, True, "UISupportsDocumentBrowser", "UIFileSharingEnabled")

# change app name
if args.n:
    change_plist(f"changed app name to {args.n}", f"app name was already {args.n}",
                plist, args.n, "CFBundleDisplayName")

# change app version
if args.v:
    change_plist(f"changed app version to {args.v}", f"app version was already {args.v}",
                plist, args.v, "CFBundleShortVersionString", "CFBundleVersion")

# change app bundle id
if args.b:
    orig_bundle = plist["CFBundleIdentifier"]
    print(f"[*] original bundle id is {orig_bundle}")
    plist["CFBundleIdentifier"] = args.b
    for ext in glob(os.path.join(APP_PATH, "PlugIns", "*.appex")):
        ext_plist = os.path.join(ext, "Info.plist")
        appex_plist = get_plist(ext_plist)
        appex_plist["CFBundleIdentifier"] = appex_plist["CFBundleIdentifier"].replace(orig_bundle, args.b)
        dump_plist(ext_plist, appex_plist)
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
    args.k = os.path.normpath(args.k)
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

dump_plist(PLIST_PATH, plist)

if args.s:
    BINARY = get_plist(PLIST_PATH, "CFBundleExecutable")
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
        if any(s in fs for s in (".framework", ".appex")):
            FS_EXEC = get_plist(os.path.join(fs, "Info.plist"), "CFBundleExecutable")
            run(f"ldid -S -M '{os.path.join(fs, FS_EXEC)}'", shell=True, check=True)
        else:
            run(f"ldid -S -M '{fs}'", shell=True, check=True)
        print(f"[*] fakesigned {os.path.basename(fs)}")
    changed = 1

# sign app executable with entitlements provided
if args.x:
    args.x = os.path.normpath(args.x)
    BINARY = get_plist(PLIST_PATH, "CFBundleExecutable")
    BINARY_PATH = os.path.join(APP_PATH, BINARY).replace(" ", r"\ ")
    check_cryptid(BINARY_PATH)
    run(f"ldid -S{args.x} {BINARY_PATH}", shell=True, check=True)
    print("[*] signed binary with entitlements file")
    changed = 1

# checking if anything was actually changed
if not changed:
    print("[!] nothing was changed, output will not be created")
    sys.exit()

# zipping everything back into an ipa/app
os.chdir(EXTRACT_DIR)
if OUTPUT_IS_IPA:
    print(f"[*] generating ipa using compression level {args.c}..")
    if not INPUT_IS_IPA:
        os.makedirs("Payload")
        run(f"mv '{INPUT_BASENAME}' 'Payload/{INPUT_BASENAME}'", shell=True, check=True)
    run(f"zip -{args.c} -r '{os.path.basename(args.o)}' Payload", shell=True, stdout=DEVNULL, check=True)
else:
    print("[*] moving app to output..")

# cleanup when everything is done
os.chdir(WORKING_DIR)
if "/" in args.o:
    os.makedirs(args.o.replace(os.path.basename(args.o), ""), exist_ok=True)
if OUTPUT_IS_IPA:
    move(os.path.join(EXTRACT_DIR, os.path.basename(args.o)), args.o)
    print(f"[*] generated ipa at {args.o}")
else:
    run(f"mv '{APP_PATH}' '{os.path.join(EXTRACT_DIR, os.path.basename(args.o))}'", shell=True, check=True)
    run(f"mv '{os.path.join(EXTRACT_DIR, os.path.basename(args.o))}' '{args.o}'", shell=True, check=True)
    print(f"[*] generated app at {args.o}")
