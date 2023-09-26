# pyzule
an [azule](https://github.com/Al4ise/Azule) "clone" written in python3. `pyzule` aims to be faster, have more features, have better support for manually modified dylibs, and overall have less issues than azule. officially supports linux, macos, and wsl. tested on arch linux and macos mojave w/ intel cpu.

## features
~~not many right now, but will probably add some in the future if i need them.~~

open an issue for any feature requests!

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
- inject into @executable_path instead of @rpath
- use substitute (open source) instead of CydiaSubstrate
- compress using 7zip instead of `zip`

## usage
you can get usage info with `pyzule -h`.

```
$ pyzule -h
usage: pyzule [-h] -i input -o output [-n name] [-v version] [-b bundle id] [-m minimum] [-c [level]] [-k icon] [-x entitlements] [-r url [url ...]] [-f files [files ...]] [-u] [-w] [-d] [-s] [-e] [-p] [-t] [-z]

an azule "clone" written in python3.

options:
  -h, --help            show this help message and exit
  -i input              the .ipa/.app to patch
  -o output             the name of the patched .ipa/.app that will be created
  -n name               modify the app's name
  -v version            modify the app's version
  -b bundle id          modify the app's bundle id
  -m minimum            change MinimumOSVersion
  -c [level]            the compression level of the output ipa (default is 6)
  -k icon               an image file to use as the app icon
  -x entitlements       a file containing entitlements to sign the app with
  -r url [url ...]      url schemes to add
  -f files [files ...]  tweak files to inject into the ipa
  -u                    remove UISupportedDevices
  -w                    remove watch app
  -d                    enable files access
  -s                    fakesigns the ipa (for use with appsync)
  -e                    remove app extensions
  -p                    inject into @executable_path
  -t                    use substitute instead of substrate
  -z                    use 7zip instead of zip
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
  install <code>insert_dylib</code>:

  <pre lang="bash"><code>git clone https://github.com/tyilo/insert_dylib.git && cd insert_dylib/insert_dylib && gcc main.c && chmod +x a.out && sudo mv a.out /usr/local/bin/insert_dylib && cd ../.. && sudo rm -r insert_dylib</code></pre>
  </li>
  <li>
  run <code>uname -m</code>. if the output says <code>x86_64</code>, run the following:
  
  <pre lang="bash"><code>sudo curl https://github.com/ProcursusTeam/ldid/releases/download/v2.1.5-procursus7/ldid_macosx_x86_64 --output /usr/local/bin/ldid && sudo chmod +x /usr/local/bin/ldid</code></pre>

  if it says something else, run:

  <pre lang="bash"><code>sudo curl https://github.com/ProcursusTeam/ldid/releases/download/v2.1.5-procursus7/ldid_macosx_arm64 --output /usr/local/bin/ldid && sudo chmod +x /usr/local/bin/ldid</code></pre>
  </li>
  <li>
  install <code>pyzule</code>:

  <pre lang="bash"><code>python3 -m pip install -U requests Pillow && curl https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/install-pyzule.py | python3</code></pre>
  </li>
</ol>
</details>

<details>
<summary><b>linux instructions (64-bit only)</b></summary>
<br/>
<ol>
  <li>make sure you have <code>git</code>, <code>gcc</code>, <code>zip</code>, <code>unzip</code>, <code>tar</code> and <code>ar</code> installed.</li>
  <li>
  install <code>insert_dylib</code>:

  <pre lang="bash"><code>git clone https://github.com/LeanVel/insert_dylib.git && cd insert_dylib && sudo ./Install.sh && cd ../ && sudo rm -rf insert_dylib</code></pre>
  </li>
  <li>
  install <code>ldid</code>:

  <pre lang="bash"><code>sudo curl https://github.com/ProcursusTeam/ldid/releases/download/v2.1.5-procursus7/ldid_linux_x86_64 --output /usr/local/bin/ldid && sudo chmod +x /usr/local/bin/ldid</code></pre>
  </li>
  <li>
  install <code>install_name_tool</code>:

  <pre lang="bash"><code>sudo curl https://cdn.discordapp.com/attachments/1105232452529700985/1117486649803292837/install_name_tool --output /usr/local/bin/install_name_tool && sudo chmod +x /usr/local/bin/install_name_tool</code></pre>
  </li>
  <li>
  install <code>otool</code>:

  <pre lang="bash"><code>sudo curl https://cdn.discordapp.com/attachments/1105232452529700985/1117486650533085275/otool --output /usr/local/bin/otool && sudo chmod +x /usr/local/bin/otool</code></pre>
  </li>
  <li>
  install <code>pyzule</code>:

  <pre lang="bash"><code>python3 -m pip install -U requests Pillow && curl https://raw.githubusercontent.com/asdfzxcvbn/pyzule/main/install-pyzule.py | python3</code></pre>
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
- [tyilo](https://github.com/tyilo) for [insert_dylib](https://github.com/tyilo/insert_dylib)
- [LeanVel](https://github.com/LeanVel) for [insert_dylib](https://github.com/LeanVel/insert_dylib) for linux
- [binnichtaktiv](https://github.com/binnichtaktiv) for inspiring me to actually start this project
