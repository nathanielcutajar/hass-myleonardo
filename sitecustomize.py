import os


# Keep local lightweight tests isolated from globally installed pytest plugins.
# Home Assistant's pytest plugin tries to import this repository root as an
# installed custom component package, but this checkout is already the component
# directory itself: custom_components/myleonardo.
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
