pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
dicdir = pkgdatadir / 'dic'

python_prog = find_program('python3')

grades = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

foreach grade : grades
  target = custom_target(
    'generate_' + grade,
    input: [files('restrain.py', 'third_party/skk/SKK-JISYO.ML')],
    output: 'restrained.' + grade + '.dic',
    command: [python_prog, '@INPUT@', grade],
    capture: true,
    install: true,
    install_dir: dicdir,
    depend_files: [files(
      'zyouyou-kanji.csv',
      'add_6.dic',
      'add_7.dic',
      'add_8.dic',
      'add_9.dic',
      'drop.dic',
      'drop_6.dic',
      'huhyou.dic',
      'permissible_9.dic',
      'reigai.dic',
      'tc2.compat.dic',
      'zyosuusi.dic',
      'dic.py'
    )],
  )
endforeach

katakana = custom_target(
  'generate_katakana.dic',
  input: [files('katakana.py', 'third_party/edrdg/edict2', 'drop.katakana.dic')],
  output: 'katakana.dic',
  command: [python_prog, '@INPUT@'],
  capture: true,
  install: true,
  install_dir: dicdir,
  depend_files: [files('drop.katakana.dic')],
)

permissible = custom_target(
  'generate_permissible.dic',
  input: [files('permissible.py', 'zyouyou-kanji.csv')],
  output: 'permissible.dic',
  command: [python_prog, '@INPUT@'],
  capture: true,
  install: true,
  install_dir: dicdir,
)
