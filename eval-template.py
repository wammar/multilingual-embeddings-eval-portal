#!/usr/bin/env python

import gzip
import argparse
import random
#import math
#import os
#import shutil
#import subprocess
#import sys
#import tempfile

# parse/validate arguments
argparser = argparse.ArgumentParser()
argparser.add_argument("-eval-data", help="Path to a directory which contains all data files needed to setup the evaluation script.")
argparser.add_argument("-embeddings-file", help="Path to the embeddings file (lowercased, UTF8-encoded, space-delimited, optional: suffix .gz indicate the file is gzip compressed.)")
args = argparser.parse_args()

def gzopen(f):
  return gzip.open(f) if f.endswith('.gz') else open(f)

def get_relevant_word_types(eval_data_dir):
  pass

def evaluate(eval_data_dir, embeddings_filename):
  # We only need embeddings for a subset of word types. Copy the relevant embeddings in a new plain file.
  relevant_word_types = set(get_relevant_word_types(eval_data_dir))
  relevant_embeddings_filename = "relevant_embeddings/" + random.randint(100000, 999999)
  with gzopen(embeddings_filename) as all_embeddings_file:
    with open(relevant_embeddings_filename, mode='w') as relevant_embeddings_file:
      for line in all_embeddings_file:
        line = line.decode('utf8')
        if line.split(' ')[0] not in relevant_word_types: continue
        line = line.encode('utf8')
        relevant_embeddings_file.write(line)
  
  # do the actual evaluation
  pass

def main(argv):
  score = evaluate(args.eval_data, args.embeddings_file)
  print score

if __name__ == '__main__':
  main(sys.argv)
