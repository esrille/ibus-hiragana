test_dir = meson.source_root() / 'tests'

pymod = import('python')
python = pymod.find_installation('python3')

# Include generated python source file(s).
python_paths = [
  meson.current_build_dir() / '..' / 'engine',
  meson.source_root() / 'engine'
]
test_env = environment()
test_env.set('PYTHONPATH', python_paths)

# To test, execute the following command within a venv:
# $ meson test -C _build
test('tests',
     python,
     args : ['-m', 'unittest', 'discover', '-v', test_dir],
     env : test_env
)
