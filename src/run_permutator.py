#! /usr/bin/env python3

import sys
import subprocess
import os

script, instance, output, init, config, tlim = sys.argv

print("instance: ", instance)
print("output: ", output)
print("init: ", init)
print("time limit is:", int(tlim))
print("config: ",config)

run_string = script + " -d " + instance + " -i " + init + " -o " + output + " -c " + config + " -t " + tlim

if __name__ == "__main__":

    folderpath = os.getcwd()
    # script = model + ".py"
    # script_path = os.path.join(folderpath,script)
    print(folderpath)
    # print(script_path)
    print(run_string)
    subprocess.run([run_string]) 


#./cmake-build-release/TSPSD_meta -d ./data_demo/datasets/TSPSD/berlin52-13.2.json -i ./data_demo/results/TSPSD/berlin52-13.2_init.json -o ./data_demo/results/wTSPSD/berlin52-13.2.json -c ./configs/TSPSD_config_opt.json -t 60

# -d . . . path to a problem instance
# -o . . . path to an output file (optional)
# -i . . . initial solution (optional)
# -t . . . timeout in seconds (optional)
# -c . . . solver configuration file (optional)
