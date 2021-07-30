import sys

import d2m

python_version = sys.version_info[0]
if python_version > 3:
    import importlib
    importlib.reload(d2m)
else:
    reload(d2m)

def run():
    print("Daz to Maya, run() method")
    d2m.initialize()