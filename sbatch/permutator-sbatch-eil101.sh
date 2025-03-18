#!/bin/bash

## Lines beginning with "#SBATCH" specify an sbatch configurations.
## We use "##" for commentary. 

## Sbatch configuration are used by Slurm to allocate resources. It throws an
## error if it cannot satisfy them.


## Each individual command given to the gnu `parallel` is a "task".

## For sbatch parameter list, https://slurm.schedmd.com/sbatch.html

## As of November-2024, each niagara node has 40 CPUs each with 2 threads, and
## when a node is reserved the total number of CPUs shows as 80 (threads).

## Slurm allocates CPU-threads to a task, not CPUs.

## Number of nodes requested
#SBATCH --nodes=1

## TIDEL account name.
#SBATCH --account=def-beck

## The "--time" argument specifies the requested time period of node allocation.
## It is specified in the HH:MM:SS format.
## As of November-2024, 
##  - the max value is 24:00:00
##  - the min value is 00:15:00
## It is advisable to request 30 minutes more than the expected run time.
#SBATCH --time=01:00:00

## "--ntasks-per-node" parameter tells Slurm the number of parallel task runs.
## Typical value: minimum of 40 and (175 GB / memory-limit-per-task)
## For comparative evaluation, this value should be same across all scripts to
##   ensure that the same number of processes are run in parallel on all nodes.
## This value is used at two places:
## 1. To set the number of CPUs in the resource allocation request. 
## 2. Assigned to SLURM_TASKS_PER_NODE environment variable.
#SBATCH --ntasks=40
#SBATCH --ntasks-per-node=40
#SBATCH --ntasks-per-core=1

## "--cpus-per-task" tells the expected count of CPU "threads" per task
##
## Each CPU core on Niagara node allows two threads to share it. However, that
##  results in slower execution as the two threads contend for shared resources
##  like the CPU cache, execution units and registers.
## To make sure a single-threaded process gets a full CPU core allocated to it,
##  we set cpus-per-task=2, so the request requires slurm to allocate twice the
##  number of threads (or same number CPU cores as tasks per node).
##
## Typical value: 2, which is equal to the threads per CPU core on Niagara.
#SBATCH --cpus-per-task=2

## "--ntasks-per-node" and "--cpus-per-task" are used by slurm to formulate the 
##  allocation request, requested CPU Threads: ntasks-per-node * cpus-per-task.

## Get sbatch job status on your email
##
## !!!--USER ACTION--!!! Update your email below.
#SBATCH --mail-user=daniel.pekar@mail.utoronto.ca
#SBATCH --mail-type=ALL

module load CCEnv
module load StdEnv/2023
module load gcc/12.3
module load boost/1.85.0
## module load python/3.12.4
##module load boost/1.85.0
## module load rust/1.76.0

## module use /scinet/niagara/software/commercial/modules
## module load gurobi/12.0.0

## Load the python virtual environment containing the installation of DIDP
# source ~/env_didp/bin/activate

## Gnu-parallel is responsible to run tasks in parallel.
##
## Comments on the below command:
## 1. The symbol {1} and {2} refers to items in the first and second lists: 
##      {1..3} and 10 20 30.
## 2. Any number of lists can be given as input to gnu-parallel.
## 3. Gnu-parallel will run the test_didp.py script in parallel for all 
##      combinations of '{1}' and '{2}'. 
## 4. -j specifies the number of tasks run in parallel on a node.
## 5. `tee` directs a copy of stdout to the log file. 
##
## !!!--USER ACTION--!!! Create `results` directory in the working directory.

parallel -j 40 "/gpfs/fs0/scratch/b/beck/pekardan/permutator/permutator/cmake-build-release/TSPSD_meta -i /gpfs/fs1/home/b/beck/pekardan/permutator/permutator/data_demo/results/TSPSD/init/{1}_init.json -d /gpfs/fs1/home/b/beck/pekardan/permutator/permutator/data_demo/datasets/TSPSD/{1}.json -o ./data_demo/results/TSPSD/run_{1}_{2}_{3}.json -c /gpfs/fs1/home/b/beck/pekardan/permutator/permutator/configs/TSPSD_opt.json -t {2} | tee /gpfs/fs0/scratch/b/beck/pekardan/results/perm/run_{1}_{2}_{3}.txt" ::: eil101-27.5 :::+ 1010 ::: {0..49}