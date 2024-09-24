# Development

## Install from source

To install Hiragana IME from the source code, enter the following commands into a terminal:

```
git clone https://github.com/esrille/ibus-hiragana.git
cd ibus-hiragana
meson setup --prefix /usr _build [-Denable-dic=true] [-Denable-html=true]
ninja -C _build
ninja -C _build install
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
