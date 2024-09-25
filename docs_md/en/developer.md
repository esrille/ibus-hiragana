# Development

## Build and Install

To build and install Hiragana IME from the source code, enter the following commands into a terminal:

```
git clone https://github.com/esrille/ibus-hiragana.git
cd ibus-hiragana
meson setup --prefix /usr _build [-Denable-dic=false] [-Denable-html=false] [-Dpython=python3]
ninja -C _build
ninja -C _build install
```

With <code>meson setup</code>, you can specify the following options:

- Specify <code>-Denable-dic=true</code> to build Kanji and Katakana dictionaries.
- Specify <code>-Denable-html=true</code> to generate HTML documents from the markdown files.
- Use <code>-Dpython</code> to specify the Python command. For instance, to use Python 3.12, set <code>-Dpython=python3.12</code>.

Refer to Build-Depends in debian/control or BuildRequires in ibus-hiragana.spec for the packages required for building the Hiragana IME.

If you are using Fedora, you can use the following command to install the required packages:

```
sudo yum-builddep ibus-hiragana.spec
```

If you are using Ubuntu, you can use the following command to install the required packages:

```
sudo apt build-dep .
```

## Unit Testing {: #tests}

Hiragana IME runs within a local Python virtual environment (venv).
You need to run tests within this venv.
You also need to [install](install.html#llm) additional components to use LLM for testing some tests.

To run tests, enter the following commands into a terminal:

```
source ~/.local/share/ibus-hiragana/venv/bin/activate
meson test -C _build --verbose
```

## Uninstall {: #uninstall}

To uninstall Hiragana IME that is built from the source code, enter the following command into a terminal:

```
sudo ninja -C _build uninstall
```

<code>ninja</code> does not remove the directory <code>/usr/share/ibus-hiragana</code> with the <code>uninstall</code> command.
To remove this directory, enter the following command into a terminal:

```
sudo rm -rf /usr/share/ibus-hiragana
```
