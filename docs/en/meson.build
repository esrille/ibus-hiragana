pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'docs' / 'en'

static_files = [
  'default.css',
  'ibus-setup-hiragana_1.png',
  'ibus-setup-hiragana_2.png',
  'ibus-setup-hiragana_3.png',
  'keyboard-menu.png',
  'settings-keyboard.png',
]

install_data(static_files, install_dir: moduledir)
