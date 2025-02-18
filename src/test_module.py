#!/usr/bin/env python3

import time

import sys

from math import ceil

from argparse import ArgumentParser


def consume_cpucycle_seconds(cputime: int):
  """
  wait for wait_time seconds
  """
  t0 = time.perf_counter()
  while time.perf_counter() - t0 < cputime:
    x = 1
    x = x + 1


def create_list(size_in_bytes: int):
  """
  Create a list consuming at least size_in_bytes bytes
  """
  base_list_size = sys.getsizeof(1*[])
  diff = sys.getsizeof(2*[0]) - sys.getsizeof(1*[0])
  size = ceil((size_in_bytes - base_list_size) / diff)

  assert size > 0

  x = size * [0]


def test_limits(ml: int, tl: int):
  """
  Test memory limit, given in bytes, and time limit, given in seconds.
  """
  create_list(ml)
  consume_cpucycle_seconds(tl)


def process_arguments() -> dict:
  """
  Basic command line argument process.
  """
  parser = ArgumentParser(description="Process input")

  # Resource limit parameters
  parser.add_argument(
      '-m', '--memlimit', action='store', nargs='?', type=int, required=True)
  parser.add_argument(
      '-t', '--timelimit', action='store', nargs='?', type=int, required=True)

  return parser.parse_args()


if __name__ == "__main__":
  """
  """
  args = process_arguments()

  test_limits(args.memlimit * 1024 * 1024, args.timelimit)

  print("Success")