# pyzule
an [azule](https://github.com/Al4ise/Azule) "clone" written in python3. `pyzule` aims to be faster, have more features, have better support for manually modified dylibs, and overall have less issues than azule. officially supports linux, macos, and wsl. tested on arch linux and macos mojave w/ intel cpu.

## features
~~not many right now, but will probably add some in the future if i need them.~~

open an issue for any feature requests!

- **generate and use [shareable `.pyzule` files](https://github.com/asdfzxcvbn/pyzule-gen) to configure IPAs!**
- inject deb, dylib, framework, bundle, and appex files and automatically fix dependencies when possible
- automatically fix dependencies on CydiaSubstrate, librocketbootstrap, libmryipc, libhdev, and Cephei*
- copy any unknown file/folder types to app root
- use a custom compression level
- change app name, version, and bundle id
- add custom url schemes
- change app icon
- enable documents support
- customize MinimumOSVersion
- remove UISupportedDevices
- remove watch app
- remove app extensions
- fakesign the output ipa/app
- use custom entitlements for the app
- merge a plist into the app's existing Info.plist
- inject into @executable_path instead of @rpath
- use substitute (open source) instead of CydiaSubstrate

## usage
you can get usage info with `pyzule -h`.

```
$ pyzule -h
usage: pyzule [-h] -i input -o output [-z .pyzule] [-n name] [-v version] [-b bundle id] [-m minimum] [-c [level]] [-k icon] [-x entitlements] [-l plist] [-r url [url ...]] [-f files [files ...]] [-u] [-w] [-d] [-s] [-e] [-p] [-t]

an azule "clone" written in python3.

options:
  -h, --help            show this help message and exit
  -i input              the .ipa/.app to patch
  -o output             the name of the patched .ipa/.app that will be created
  -z .pyzule            the .pyzule file to get info from
  -n name               modify the app's name
  -v version            modify the app's version
  -b bundle id          modify the app's bundle id
  -m minimum            change MinimumOSVersion
  -c [level]            the compression level of the output ipa (default is 6, 0-9)
  -k icon               an image file to use as the app icon
  -x entitlements       a file containing entitlements to sign the app with
  -l plist              a plist to merge with the existing Info.plist
  -r url [url ...]      url schemes to add
  -f files [files ...]  tweak files to inject into the ipa
  -u                    remove UISupportedDevices
  -w                    remove watch app
  -d                    enable files access
  -s                    fakesigns the ipa (for use with appsync)
  -e                    remove app extensions
  -p                    inject into @executable_path
  -t                    use substitute instead of substrate
```

## installation

<details>
<summary><b>macOS instructions</b></summary>
<br/>
<ol>
  <li>open Terminal. this is where you'll be running every command.</li>
  <li>install <a href="https://apps.apple.com/us/app/xcode/id497799835">Xcode</a> from the app store (if not already installed)</li>
  <li>Install the Xcode cli tools (if not already installed <strong>or if <code>pyzule</code> suddenly stopped working</strong>) by running:
  <ul>
    <li><code>xcode-select --install</code></li>
    <li><code>sudo xcodebuild -license</code></li>
  </ul>
  </li>
  <li>
  install <code>pyzule</code>:

  <pre lang="bash"><code>bash -c "$(curl https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/install-pyzule.sh)"</code></pre>
  </li>
</ol>
</details>

<details>
<summary><b>linux/wsl instructions</b></summary>
<br/>
<ol>
  <li>
    on debian-based systems (like ubuntu), run the following:
    <pre lang="bash"><code>sudo apt update ; sudo apt install unzip curl python3 python3-venv</code></pre>
    on arch based systems, use:
    <pre lang="bash"><code>sudo pacman -Syu unzip curl python</code></pre>
  </li>
  <li>
  install <code>pyzule</code>:

  <pre lang="bash"><code>bash -c "$(curl https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/install-pyzule.sh)"</code></pre>
  </li>
</ol>
</details>

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
- [lief-project](https://github.com/lief-project) for [LIEF](https://github.com/lief-project/LIEF)
- [binnichtaktiv](https://github.com/binnichtaktiv) for inspiring me to actually start this project

formerly used:
- [tyilo](https://github.com/tyilo)'s [insert_dylib](https://github.com/tyilo/insert_dylib)
- [LeanVel](https://github.com/LeanVel)'s [insert_dylib](https://github.com/LeanVel/insert_dylib) for linux
