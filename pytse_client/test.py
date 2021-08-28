import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import download

download.download("همراه", adj_by_split=True, write_to_csv=True, base_path="temp_data")