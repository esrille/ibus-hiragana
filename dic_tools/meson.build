pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
bindir = get_option('prefix') / get_option('bindir')
moduledir = pkgdatadir / 'dic_tools'
dicdir = pkgdatadir / 'dic'

python_prog = find_program('python3')

conf = configuration_data()
conf.set('PYTHON', python.path())
conf.set('VERSION', meson.project_version())
conf.set('prefix', get_option('prefix'))
conf.set('localedir', get_option('prefix') / get_option('localedir'))

configure_file(
  input: 'ibus-hiragana-tool.in',
  output: 'ibus-hiragana-tool',
  configuration: conf,
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x',
)

install_data([
    'dictools.py',
    'diclib.py',
    'toolpath.py',
    'zyouyou-kanji.csv'
  ],
  install_dir: moduledir,
  install_mode: 'rw-r--r--'
)

grades = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

foreach grade : grades
  target = custom_target(
    'generate_' + grade,
    input: ['restrain.py', 'third_party/skk/SKK-JISYO.ML'],
    output: 'restrained.' + grade + '.dic',
    command: [python_prog, '@INPUT@', grade],
    capture: true,
    install: true,
    install_dir: dicdir,
    depend_files: [
      'zyouyou-kanji.csv',
      'add_6.dic',
      'add_7.dic',
      'add_8.dic',
      'add_9.dic',
      'drop.dic',
      'drop_6.dic',
      'huhyou.dic',
      'reigai.dic',
      'tc2.compat.dic',
      'zyosuusi.dic',
      'diclib.py'
    ],
  )
endforeach

katakana = custom_target(
  'generate_katakana.dic',
  input: ['katakana.py', 'third_party/edrdg/edict2', 'drop.katakana.dic'],
  output: 'katakana.dic',
  command: [python_prog, '@INPUT@'],
  capture: true,
  install: true,
  install_dir: dicdir,
  depend_files: ['drop.katakana.dic'],
)

permissible = custom_target(
  'generate_permissible.dic',
  input: ['permissible.py', 'permissible_9.dic'],
  output: 'permissible.dic',
  command: [python_prog, '@INPUT@'],
  capture: true,
  install: true,
  install_dir: dicdir,
  depend_files: ['zyouyou-kanji.csv'],
)
