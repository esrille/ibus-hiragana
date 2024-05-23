pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'docs'

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
  ['index.md', 'altgr.md', 'install.md'],
  ['install.md', 'index.md', 'usage.md'],
  ['usage.md', 'install.md', 'key_assign.md'],
  ['key_assign.md', 'usage.md', 'settings.md'],
  ['settings.md', 'key_assign.md', 'layouts.md'],
  ['layouts.md', 'settings.md', 'roomazi.md'],
  ['roomazi.md', 'layouts.md', 'altgr.md'],
  ['altgr.md', 'roomazi.md', 'index.md'],
]

foreach content : contents
  html = custom_target(
    'generate_' + content[0].replace('.md', '.html'),
    input: [files('md2html.py', content[0], content[1], content[2], 'template.html'), toc],
    output: content[0].replace('.md', '.html'),
    command: [python_prog, '@INPUT@', '@OUTPUT@'],
    install: true,
    install_dir: moduledir,
    depends: toc,
  )
endforeach
