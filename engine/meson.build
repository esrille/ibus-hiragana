pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'engine'
componentdir = get_option('prefix') / get_option('datadir') / 'ibus' / 'component'
gnome = import('gnome')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('PACKAGE_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('prefix', get_option('prefix'))
conf.set('libexecdir', get_option('prefix') / get_option('libexecdir'))
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'hiragana.xml.in',
  output: 'hiragana.xml',
  configuration: conf,
  install: true,
  install_dir: componentdir,
  install_mode: 'rw-r--r--',
)

configure_file(
  input: 'ibus-engine-hiragana.in',
  output: 'ibus-engine-hiragana',
  configuration: conf,
  install: true,
  install_dir: get_option('libexecdir'),
  install_mode: 'rwxr-xr-x',
)

configure_file(
  input: 'package.py.in',
  output: 'package.py',
  configuration: conf,
  install: true,
  install_dir: moduledir,
  install_mode: 'rw-r--r--',
)

ibus_hiragana_sources = [
  'dictionary.py',
  'engine.py',
  'event.py',
  'factory.py',
  'main.py',
]

install_data(ibus_hiragana_sources, install_dir: moduledir)
