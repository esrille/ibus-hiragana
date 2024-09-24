# Installation

To set up the Hiragana IME, follow the steps below:

1. [Install the Hiragana IME software package](#install)
2. [Add the Hiragana IME to the input sources](#input-source)
3. [Enable the Hiragana IME](#enable)
4. [Install additional components for using LLM](#llm)

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

### Change the input method module for Wayland {: #wayland}

From Ubuntu 21.04 and Fedora 25 onwards, Wayland is used by default for screen rendering.
Wayland is being developed to replace the classic X server.

GNOME is also developing a new input method module for Wayland. However, it is still in the early stages of development.
In GNOME 45 or earlier, the surrounding text information sent to input methods is broken.
In GNOME 46, the surrounding text information is not sent to input methods at the right time with many applications.

So, we recommend using the IBus input method module even on Wayland.
To do so, define GTK_IM_MODULE environment variable in your ~/.bash_profile (in Fedora) or ~/.profile (in Ubuntu) as below.

```
export GTK_IM_MODULE=ibus
```

You can check the version of GNOME by opening the GNOME **Settings** window, then going to **About This System**-**System Details**.

### Restart your computer

Please restart your computer to apply the changes before proceeding to the next section.

## Add the Hiragana IME to the input sources {: #input-source}

Next, we will add the Hiragana IME to the input sources.
We call keyboard layouts and input methods collectively as **Input Sources** on GNOME.
The setup process varies depending on your desktop environment.

### Instructions for GNOME

On Fedora and Ubuntu, GNOME is the default desktop environment.
The Hiragana IME currently works best in GNOME.
If you're using GNOME, open **Settings** and add **Japanese (Hiragana IME)** to **Input Sources** in the **Keyboard** pane.

![Settings—Keyboard](settings-keyboard.png)

### Instructions for other desktops

Open **IBus Preferences**, and select the **Input Method** tab.
Add **Hiragana IME** to the list of **Input Method** by selecting the following item:
<br><br>
  ![icon](../icon.png) Hiragana IME
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

## Install additional components for using LLM {: #llm}

Hiragana IME has a feature that pre-selects the most probable conversion candidate using a Large Language Model.
To use this, the following packages need to be installed:

- [Huggingface Transformers](https://huggingface.co/docs/transformers/)
- [tohoku-nlp/bert-base-japanese-v3](https://huggingface.co/tohoku-nlp/bert-base-japanese-v3)

Hiragana IME runs within a local Python virtual environment (venv).
To install the above packages in this venv, follow these steps:

1. In **[Hiragana IME Setup](settings.html#ibus-setup-hiragana)** window, open the **Option** tab:

![Hiragana IME Setup Window](ibus-setup-hiragana_3.png)

2. Click **Install**, and the following window will open.

![Post Installation Window](postinst_1.png)

3. Click **Install** to start the installation. The installation log will be displayed within the window.

![Post Installation Window](postinst_2.png)

4. Once the installation is finished, the **Install** button will change to a **Close** button. Click it to close the window.

The installation of the required packages for using LLM is now complete.
When you log in again, you can use the candidate pre-selection feature using LLM.

<br>**Hint**: If your PC has an NVIDIA GPU, the Hiragana IME can use CUDA to accelerate the LLM calculation.
For more details, please see "[Use CUDA for LLM calculation](settings.html#cuda)".

## Updates {: #update}

When a new release of the Hiragana IME is available, we will announce it on the [Releases](https://github.com/esrille/ibus-hiragana/releases) page on GitHub.
The steps for updating the Hiragana IME depend on how you install it.
Follow the update steps that correspond to your installation method.

### Instructions for Fedora

The Hiragana IME can be updated just like other Fedora packages.
To do so from the command line, use the following <code>dnf</code> command:

```
sudo dnf update
```

### Instructions for Ubuntu

The Hiragana IME can be updated just like other Ubuntu packages.
To do so from the command line, use the following <code>apt</code> commands:

```
sudo apt update
sudo apt upgrade
```

## Uninstall {: #uninstall}

The steps for uninstalling the Hiragana IME depend on how you install it.
Follow the uninstall steps that correspond to your installation method.

### Instructions for Fedora

To uninstall the Hiragana IME, use the following <code>dnf</code> command:

```
sudo dnf remove ibus-hiragana
```

### Instructions for Ubuntu

To uninstall the Hiragana IME, use the following <code>apt</code> command:

```
sudo apt remove ibus-hiragana
```

## User data stored in your home directory {: #user-files}

The Hiragana IME stores user data in the directory <code>~/.local/share/ibus-hiragana/</code>.
Under this directory, the Hiragana IME stores your input histories, user dictionary file(s), and also its Python venv:

```
~/.local/share/ibus-hiragana/
├── dic/        # Your input histories
├── my.dic      # User dictionary file
└── venv/       # Python venv for the Hiragana IME
```

If you want to install the Hiragana IME on other PCs, you can use the copy of the directory <code>dic/</code> and the file <code>my.dic</code>.

### Clean uninstall

If you want to remove all user data after uninstalling the Hiragana IME, you can remove the directory <code>~/.local/share/ibus-hiragana/</code>:

```
rm -rf ~/.local/share/ibus-hiragana
```

If you used the Hiragana IME with the LLM packages, the [tohoku-nlp/bert-base-japanese-v3](https://huggingface.co/tohoku-nlp/bert-base-japanese-v3) files are stored in the directory <code>~/.cache/huggingface/hub/models--cl-tohoku--bert-base-japanese-v3/</code>.
Please note that these files might be used by other applications that use [Transformers](https://huggingface.co/docs/transformers/index).
If you are sure that you want to delete these files, enter the following command into a terminal:

```
rm -rf ~/.cache/huggingface/hub/models--cl-tohoku--bert-base-japanese-v3
```
