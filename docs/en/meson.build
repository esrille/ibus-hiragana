pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'docs' / 'en'

static_files = [
  'about.png',
  'default.css',
  'ibus-setup-hiragana_1.png',
  'ibus-setup-hiragana_2.png',
  'ibus-setup-hiragana_3.png',
  'ibus-setup-hiragana_4.png',
  'ibus-setup-hiragana_5.png',
  'keyboard-menu.png',
  'notification.png',
  'postinst_1.png',
  'postinst_2.png',
  'settings-keyboard.png',
]

install_data(static_files, install_dir: moduledir)

if get_option('enable-html') == false

  html_files = [
    'altgr.html',
    'developer.html',
    'dictionary.html',
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
