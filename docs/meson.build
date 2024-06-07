pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'docs'

static_files = [
  'default.css',
  'screenshot.webm',
  'undo.webm',
  'ibus-setup-hiragana_1.png',
  'ibus-setup-hiragana_2.png',
  'ibus-setup-hiragana_3.png',
  'icon.png',
  'input-modes.gif',
  'keyboard-menu.png',
  'screenshot.png',
  'settings-keyboard.png',
]

install_data(static_files, install_dir: moduledir)

if get_option('enable-html') == false

  html_files = [
    'altgr.html',
    'index.html',
    'install.html',
    'key_assign.html',
    'layouts.html',
    'roomazi.html',
    'settings.html',
    'usage.html',
  ]

install_data(html_files, install_dir: moduledir)

endif

subdir('en')
