import os

from typing import List
def try_paths(paths: List[str], file: str):
  if os.path.isabs(file):
    return file if os.path.exists(file) else False

  tried = []
  for path in paths:
    newPath = os.path.join(path, file)
    if os.path.exists(newPath):
      return newPath
    else:
      tried.append(newPath)

  raise FileNotFoundError("Tried paths: \n" + "\n".join(tried))
  # return False

HOME_DIR = os.path.expanduser("~")

ROOT_DIRS = [
  os.path.join(HOME_DIR, "DAZ 3D", "Bridges", "Daz To Maya"),
  os.path.join(HOME_DIR, "Documents", "DAZ 3D", "Bridges", "Daz To Maya"),
]

EXPORT_DIRS = [ os.path.join(dir, "Exports") for dir in ROOT_DIRS ]
