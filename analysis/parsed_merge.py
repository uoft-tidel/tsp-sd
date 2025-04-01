import os
import json

folderpath = os.getcwd()
results_folder = os.path.join(folderpath,"results","no_first_last")

files=[f for f in os.listdir(results_folder)]

def combine_jsons(files, resname):
    all_data_dict = {}
    for json_file in files:
       json_f_name = os.path.join(folderpath,"results","no_first_last",json_file)
       print(json_file)
       with open(json_f_name,'r+') as file:
           # First we load existing data into a dict.
           file_data = json.load(file)
       all_data_dict.update(file_data)
    with open(resname, "w") as outfile:# save to json file
        json.dump(all_data_dict, outfile)


results_fname = os.path.join(folderpath,"results","no_first_last","merged-original-nofirst_last-results.json")
combine_jsons(files, results_fname)