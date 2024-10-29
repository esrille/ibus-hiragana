project('ibus-hiragana',
          version: '1.0~rc1',
    meson_version: '>= 0.53.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

i18n = import('i18n')
gnome = import('gnome')

subdir('data')
subdir('docs')
subdir('engine')
subdir('layouts')
subdir('man')
subdir('setup')
subdir('po')

if get_option('enable-dic')
  subdir('dic_tools')
else
  subdir('dic')
endif

if get_option('enable-html')
  subdir('docs_md')
endif

if get_option('tests')
  subdir('tests')
endif

install_data([
    'requirements.txt'
  ],
  install_dir: pkgdatadir,
)

meson.add_dist_script('meson/update-changelog.sh', meson.project_version())

meson.add_install_script('meson/postinstall.py')
