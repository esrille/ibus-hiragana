pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'engine'
test_dir = meson.source_root() / 'tests'

pymod = import('python')
python = pymod.find_installation('python')

# Run tests using the install directory to include generated python source file(s).
test_env = environment()
test_env.set('PYTHONPATH', moduledir)

# To test, execute the following command within a venv:
# $ meson test -C _build
test('tests',
     python,
     args : ['-m', 'unittest', 'discover', '-v', test_dir],
     env : test_env
)
