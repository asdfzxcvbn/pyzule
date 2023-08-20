# pyzule
an [azule](https://github.com/Al4ise/Azule) "clone" written in python3. `pyzule` aims to be faster, have more features, have better support for manually modified dylibs, and overall have less issues than azule. officially supports linux, macos, and wsl. tested on arch linux and macos mojave w/ intel cpu.

## features
~~not many right now, but will probably add some in the future if i need them.~~

open an issue for any feature requests!

- inject deb, dylib, framework, bundle, and appex files and automatically fix dependencies when possible
- automatically fix dependencies on CydiaSubstrate, librocketbootstrap, libmryipc, and Cephei*
- copy any unknown file/folder types to app root
- use a custom compression level
- change app name, version, and bundle id
- add custom url schemes
- change app icon
- enable documents support
- set minimum iOS version to 10.0
- remove UISupportedDevices
- remove watch app
- remove app extensions
- fakesign the output ipa/app
- use custom entitlements for the app
- inject into @executable_path instead of @rpath
- use substitute (open source) instead of CydiaSubstrate
- compress using 7zip instead of `zip`

## usage
you can get usage info with `pyzule -h`.

```
$ pyzule -h
usage: pyzule [-h] -i input -o output [-n name] [-v version] [-b bundle id] [-c [level]] [-k icon] [-x entitlements] [-r url [url ...]] [-f files [files ...]] [-u] [-w] [-m] [-d] [-s] [-e] [-p] [-t] [-z]

an azule "clone" written in python3.

options:
  -h, --help            show this help message and exit
  -i input              the .ipa/.app to patch
  -o output             the name of the patched .ipa/.app that will be created
  -n name               modify the app's name
  -v version            modify the app's version
  -b bundle id          modify the app's bundle id
  -c [level]            the compression level of the output ipa (default is 3)
  -k icon               an image file to use as the app icon
  -x entitlements       a file containing entitlements to sign the app with
  -r url [url ...]      url schemes to add
  -f files [files ...]  tweak files to inject into the ipa
  -u                    remove UISupportedDevices
  -w                    remove watch app
  -m                    set MinimumOSVersion to iOS 10.0
  -d                    enable files access
  -s                    fakesigns the ipa (for use with appsync)
  -e                    remove app extensions
  -p                    inject into @executable_path
  -t                    use substitute instead of substrate
  -z                    use 7zip instead of zip
```

## installation

### requirements

#### cli tools
you need `git`, `gcc`, `zip`, `unzip`, and `tar`. you also need `ar` if you're on linux.

#### insert_dylib
you have to build this yourself.

on macos, run `git clone https://github.com/tyilo/insert_dylib.git && cd insert_dylib/insert_dylib && gcc main.c && chmod +x a.out && sudo mv a.out /usr/local/bin/insert_dylib && cd ../.. && sudo rm -r insert_dylib`

on linux, run `git clone https://github.com/LeanVel/insert_dylib.git && cd insert_dylib && sudo ./Install.sh && cd ../ && sudo rm -rf insert_dylib`

if you're on macos, that should be everything you need to install. skip to the installation script.

#### install_name_tool
installed by default on macos. tested on an amd64 linux machine, it probably won't work on anything else. i don't know where to get the binaries for other architectures.

`sudo wget https://cdn.discordapp.com/attachments/1105232452529700985/1117486649803292837/install_name_tool -O /usr/local/bin/install_name_tool && sudo chmod +x /usr/local/bin/install_name_tool`

#### ldid

with the recent trollstore fix, using procursus's ldid build is now required. get it for your platform here: https://github.com/ProcursusTeam/ldid/releases, then move it to `/usr/local/bin/ldid`

#### otool
ALSO installed by default on macos. (who could've guessed?!)

`sudo wget https://cdn.discordapp.com/attachments/1105232452529700985/1117486650533085275/otool -O /usr/local/bin/otool && sudo chmod +x /usr/local/bin/otool`

### installation script
required. will install pyzule itself.

`curl https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/install-pyzule.py | python3`

> **isn't that unsafe?**
> 
> pretty much. if you're that paranoid, then you should know how to do it manually.

## contributing

### code
if you'd like to improve `pyzule`, then fork this repo and open a PR to the `dev` branch. thank you!

### money
if you want to support [my work](https://github.com/asdfzxcvbn?tab=repositories), you can donate me some monero! any donations are GREATLY appreciated. :)

xmr address: `82m19F4yb15UQbJUrxxmzJ3fvKyjjqJM55gv8qCp2gSTgo3D8avzNJJQ6tREGVKA7VUUJE6hPKg8bKV6tTXKhDDx75p6vGj`

qr code:

![qr](https://user-images.githubusercontent.com/109937991/227786784-28eaf0a1-9d17-4fc5-8c1c-f017fd62cfad.png)

## credits
`pyzule` wouldn't be possible if it wasn't for the work of some marvelous people. HUGE thanks to:

- [Al4ise](https://github.com/Al4ise) for [Azule](https://github.com/Al4ise/Azule)
- [tyilo](https://github.com/tyilo) for [insert_dylib](https://github.com/tyilo/insert_dylib)
- [LeanVel](https://github.com/LeanVel) for [insert_dylib](https://github.com/LeanVel/insert_dylib) for linux
- [binnichtaktiv](https://github.com/binnichtaktiv) for inspiring me to actually start this project
