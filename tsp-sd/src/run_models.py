import sys
import subprocess
import os

script, tlim, model, batch = sys.argv

print("time limit is:", int(tlim))
print("model used is:", model)
print("batch num is:", batch)


if __name__ == "__main__":

    folderpath = os.getcwd()
    script = model + ".py"
    script_path = os.path.join(folderpath,script)
    print(folderpath)
    print(script_path)
    subprocess.run(["python3", script_path, tlim, batch]) 