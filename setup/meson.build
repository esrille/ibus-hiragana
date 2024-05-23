pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'setup'
gnome = import('gnome')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('PACKAGE_NAME', meson.project_name())
conf.set('VERSION', meson.project_version())
conf.set('prefix', get_option('prefix'))
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'ibus-setup-hiragana.in',
  output: 'ibus-setup-hiragana',
  configuration: conf,
  install: true,
  install_dir: get_option('libexecdir'),
  install_mode: 'rwxr-xr-x'
)

configure_file(
  input: 'package.py.in',
  output: 'package.py',
  configuration: conf,
  install: true,
  install_dir: moduledir,
  install_mode: 'rw-r--r--'
)

setup_sources = [
  'main.py',
  'setup.glade',
]

install_data(setup_sources, install_dir: moduledir)
