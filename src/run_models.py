#! /usr/bin/env python3

import sys
import subprocess
import os
import datetime

script, tlim, model, batch = sys.argv

if __name__ == "__main__":

    folderpath = os.getcwd()
    script = model + ".py"
    script_path = os.path.join(folderpath,script)


    subprocess.run(["python3", script_path, tlim, batch]) 