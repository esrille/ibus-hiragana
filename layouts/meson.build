pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'layouts'

layouts_files = [
  'altgr.us.json',
  'altgr.us+dvorak.json',
  'altgr.jp.json',
  'jis.us.json',
  'jis.us+dvorak.json',
  'jis.jp.json',
  'new_stickney.us.json',
  'new_stickney.us+dvorak.json',
  'new_stickney.jp.json',
  'roomazi.us.json',
  'roomazi.jp.json',
]

install_data(layouts_files, install_dir: moduledir)
