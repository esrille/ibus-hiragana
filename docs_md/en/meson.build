pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'docs' / 'en'

python_prog = find_program('python3')

toc = custom_target(
  'generate_toc.txt',
  input: [files(
    'toc.py',
    'index.md',
    'install.md',
    'usage.md',
    'key_assign.md',
    'settings.md',
    'layouts.md',
    'roomazi.md',
    'altgr.md'
  )],
  output: 'toc.txt',
  command: [python_prog, '@INPUT@'],
  capture: true,
)

contents = [
  ['index.md', 'altgr.md', 'install.md', 'index.html'],
  ['install.md', 'index.md', 'usage.md', 'install.html'],
  ['usage.md', 'install.md', 'key_assign.md', 'usage.html'],
  ['key_assign.md', 'usage.md', 'settings.md', 'key_assign.html'],
  ['settings.md', 'key_assign.md', 'layouts.md', 'settings.html'],
  ['layouts.md', 'settings.md', 'roomazi.md', 'layouts.html'],
  ['roomazi.md', 'layouts.md', 'altgr.md', 'roomazi.html'],
  ['altgr.md', 'roomazi.md', 'index.md', 'altgr.html'],
]

foreach content : contents
  html = custom_target(
    'generate_' + content[3],
    input: [files('md2html.py', content[0], content[1], content[2], 'template.html'), toc],
    output: content[3],
    command: [python_prog, '@INPUT@', '@OUTPUT@'],
    install: true,
    install_dir: moduledir,
    depends: toc,
  )
endforeach
