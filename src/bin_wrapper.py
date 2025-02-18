#!/usr/bin/env python3
"""
@file bin_wrapper.py
@brief Frontend to execute a program within time and memory limits
@date 2025-01-13
"""


from argparse import ArgumentParser

import resource

import subprocess

from urllib.parse import unquote


def process_arguments() -> dict:
  """
  Basic command line argument process.
  """
  parser = ArgumentParser(description="Process input")

  # Arguments passed to the underlying solver via a program or function.
  parser.add_argument(
      '-c', '--command', action='store', nargs='?', type=str,
      required=True, help='command to run (Path cannot have spaces; replace space characters by %20 in the path)')

  # Resource limit parameters
  parser.add_argument(
      '-hm', '--hardmemlimit', action='store', nargs='?', type=int, required=False,
      help='Enforce memory limit (in MB) in a solver independent way, from the python script')
  parser.add_argument(
      '-ht', '--hardtimelimit', action='store', nargs='?', type=int, required=False,
      help='Enforce time limit (in seconds) in a solver independent way, from the python script')

  args = parser.parse_args()

  return args


def set_rlimit(res, sl, hl):
  resource.setrlimit(res, (sl, hl))


if __name__ == "__main__":
  """
  """
  args = process_arguments()
  _, hard_mem_limit = resource.getrlimit(resource.RLIMIT_AS)

  command = [unquote(i) for i in args.command.split(" ")]
  print(command)

  def prepare_call(args):

    if args.hardtimelimit:
      print("Setting hard time limit: {} seconds".format(args.hardtimelimit))
      set_rlimit(resource.RLIMIT_CPU, args.hardtimelimit, args.hardtimelimit + 5)

    if args.hardmemlimit:
      print("Setting hard memory limit: {} MB".format(args.hardmemlimit))
      _, sys_mem_limit = resource.getrlimit(resource.RLIMIT_AS)
      # 1 MB  = 1024 * 1024 Bytes
      set_rlimit(resource.RLIMIT_AS, args.hardmemlimit * 1024 * 1024,
                 sys_mem_limit)

  subprocess.call(command, preexec_fn=prepare_call(args))