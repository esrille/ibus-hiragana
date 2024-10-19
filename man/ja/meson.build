conf = configuration_data()
conf.set('VERSION', meson.project_version())

configure_file(
  input: 'ibus-hiragana-tool.1.in',
  output: 'ibus-hiragana-tool.1',
  configuration: conf,
  install: true,
  install_dir: join_paths(get_option('mandir'), 'ja', 'man1')
)
