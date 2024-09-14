conf = configuration_data()
conf.set('PACKAGE', meson.project_name())

configure_file(
  input: 'org.freedesktop.ibus.engine.hiragana.gschema.xml.in',
  output: 'org.freedesktop.ibus.engine.hiragana.gschema.xml',
  configuration: conf,
  install: true,
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas',
  install_mode: 'rw-r--r--',
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
dicdir = pkgdatadir / 'dic'
install_data([
    'yougen_token.dic',
    'katuyou_token.dic'
  ],
  install_dir: dicdir,
)

subdir('icons')
