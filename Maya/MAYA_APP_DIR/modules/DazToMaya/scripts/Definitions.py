import os

HOME_DIR = os.path.expanduser("~")

ROOT_DIRS = [
  os.path.join(HOME_DIR, "DAZ 3D", "Bridges", "Daz To Maya"),
  os.path.join(HOME_DIR, "Documents", "DAZ 3D", "Bridges", "Daz To Maya"),
]

EXPORT_DIRS = [ os.path.join(dir, "Exports") for dir in ROOT_DIRS ]
