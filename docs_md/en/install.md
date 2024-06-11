# Installation

To set up the Hiragana IME, follow the steps below:

1. [Install the Hiragana IME software package](#install)
2. [Add the Hiragana IME to the input sources](#input-source)
3. [Enable the Hiragana IME](#enable)
4. [Change the Configuration for Wayland](#wayland)

## Install the Hiragana IME software package {: #install}

If you use Fedora or Ubuntu, the Hiragana IME package will be automatically downloaded during installation using the **dnf** or **apt** command.

### Instructions for Fedora

The RPM packages are available in the Copr project at [@esrille/releases](https://copr.fedorainfracloud.org/coprs/g/esrille/releases/).
To enable this Copr project, enter the following command into a terminal:

```
sudo dnf copr enable @esrille/releases
```

To install Hiragana IME, use the following **dnf** command as usual:

```
sudo dnf update
sudo dnf install ibus-hiragana
```

### Instructions for Ubuntu

The Debian packages are available in the PPA repository at [esrille/releases](https://launchpad.net/~esrille/+archive/ubuntu/releases).
To enable this repository, enter the following command into a terminal:

```
sudo add-apt-repository ppa:esrille/releases
```

To install the Hiragana IME, use the following **apt** command as usual:

```
sudo apt update
sudo apt install ibus-hiragana
```

### Install from source

To install the Hiragana IME from the source code, enter the following commands into a terminal:

```
git clone https://github.com/esrille/ibus-hiragana.git
cd ibus-hiragana
meson setup --prefix /usr _build [-Denable-dic=true] [-Denable-html=true]
ninja -C _build
ninja -C _build  install
```

- Specify -Denable-dic=true to build Kanji and Katakana dictionaries.
- Specify -Denable-html=true to generate HTML documents from the markdown files.

Refer to Build-Depends in debian/control or BuildRequires in ibus-hiragana.spec for the packages required for building the Hiragana IME.

If you are using Fedora, you can use the following command to install the required packages:

```
sudo yum-builddep ibus-hiragana.spec
```

If you are using Ubuntu, you can use the following command to install the required packages:

```
sudo apt build-dep .
```

## Add the Hiragana IME to the input sources {: #input-source}

**Note**: Keyboard layouts and input methods are collectively referred to as [input sources](https://wiki.gnome.org/Design/OS/LanguageInput).

After installing the Hiragana IME software package, restart your computer.
Then, follow the steps below to add the Hiragana IME to the input sources.
The steps for setting up the input sources differ depending on your desktop environment.

### Instructions for GNOME

On Fedora and Ubuntu, GNOME is the default desktop environment.
The Hiragana IME currently works best in GNOME.
If you're using GNOME, open **Settings** and add **Japanese (Hiragana IME)** to **Input Sources** in the **Keyboard** pane.

![Settings—Keyboard](settings-keyboard.png)

### Instructions for other desktops

Open **IBus Preferences**, and select the **Input Method** tab.
Add **Hiragana IME** to the list of **Input Method** by selecting the following item:
<br><br>
  ![icon](../icon.png) ￹Hiragana IME
<br><br>

## Enable the Hiragana IME {: #enable}

In IBus, you can switch between multiple input methods and use them.

To enable Hiragana IME, open the keyboard menu of the desktop shell by clicking the current input method logo like <nobr>**ja**</nobr>，<nobr>**あ**</nobr> inside the top bar.
Then select **Japanese (Hiragana IME)**.

![Keyboard menu](keyboard-menu.png)

As for the keyboard layout, Hiragana IME uses the previously selected keyboard layout.

- To use the Japanese keyboard layout, select **Japanese** from the keyboard menu first, then select **Japanese (Hiragana IME)**.
- To use the US keyboard layout, select **English (US)** from the keyboard menu first, then select **Japanese (Hiragana IME)**.

When you can't find the keyboard layout you want to use, add your preferred layout to the **Input Sources**.
Currently, Hiragana IME supports three keyboard layouts: **Japanese**, **English (US)**, and **English (Dvorak)**.

**Note**: Often, different keyboard designs are used from country to country for each language. In Japan, both Japanese and US keyboards are used. The US keyboard is designed in the United States. Nevertheless, it is also utilized in many other countries by modifying the letters printed on the keycaps.

## Change the Configuration for Wayland {: #wayland}

From Ubuntu 21.04 and Fedora 25 onwards, Wayland is used by default for screen rendering. Wayland is being developed to replace the classic X server.

GNOME is also developing a new input method module for Wayland. Since it is still in its early stage of development, we recommend using the IBus input method module even on Wayland. To do so, define the GTK_IM_MODULE environment variable in your ~/.bash_profile (in Fedora) or ~/.profile (in Ubuntu) as below.

```
export GTK_IM_MODULE=ibus
```

With the Wayland IM module, the surrounding text information sent to input methods is broken in GNOME 45 or earlier. In the latest GNOME 46, many applications still cannot send the surrounding text at the right time to the input methods with the Wayland IM module. You can check the version of GNOME by opening the GNOME **Settings** window, then going to **About This System**-**System Details**.

<br>
The Hiragana IME setup is now complete.
You can use the [Hiragana IME Setup](settings.html) window for additional settings.
