#!/usr/bin/env python

import gzip
import argparse
import random
import io
import os
import sys
from read_write import read_word_vectors
from read_write import gzopen
import subprocess

def copy_relevant_embeddings_only(raw_embeddings_filename, filtered_embeddings_filename, idf_filenames):
  # find relevant words
  relevant_words = set()
  for idf_filename in idf_filenames:
    with open(idf_filename) as idf_file:
      for line in idf_file:
        relevant_words.add(line.strip().split('\t')[0])

  # read and write embeddings of relevant words only
  with io.open(raw_embeddings_filename, encoding='utf8') as raw_embeddings_file, io.open(filtered_embeddings_filename, encoding='utf8', mode='w') as filtered_embeddings_file:
    for line in raw_embeddings_file:
      if line.split(' ')[0][3:] not in relevant_words: continue
      filtered_embeddings_file.write(line[3:])

def classification_wrapper(eval_data_dirname, embeddings_filename):
  score_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999))))
  no_prefix_embeddings_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999))))
  working_dirname = os.path.abspath(os.path.join(eval_data_dirname, 'document-representations/scripts/X2X'))
  idf_filenames = [ os.path.abspath(os.path.join(eval_data_dirname, 'document-representations/data/idfs/idf.de')),
                    os.path.abspath(os.path.join(eval_data_dirname, 'document-representations/data/idfs/idf.en')) ]                    
  FNULL = open(os.devnull, 'w')

  # copy the embeddings while removing the language prefix
  copy_relevant_embeddings_only(embeddings_filename, no_prefix_embeddings_filename, idf_filenames)

  # prepare data
  command = "cd {} && ./prepare-data-klement-4cat-train-valid-my-embeddings.ch {}".format(working_dirname, no_prefix_embeddings_filename)
  print command
  subprocess.call([command], shell=True)
#                   shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

  # train and test
  command = "cd {} && ./run-perceptron-train-valid-my-embeddings.ch > {}".format(working_dirname, score_filename)
  print command
  subprocess.call([command], shell=True)
# shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

  score_string = ''
  with open(score_filename) as score_file:
    score_string = score_file.read().split()[-1]
  score = float(score_string)
  return score

def evaluate(eval_data_dir, embeddings_filename):
  score = classification_wrapper(eval_data_dir, embeddings_filename)
  return (score, 0.0,)

def main(argv):
  # parse/validate arguments
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-eval-data", help="Path to a directory which contains all data files needed to setup the evaluation script.")
  argparser.add_argument("-embeddings-file", help="Path to the embeddings file (lowercased, UTF8-encoded, space-delimited, optional: suffix .gz indicate the file is gzip compressed.)")
  args = argparser.parse_args()
  # evaluate
  score, coverage = evaluate(args.eval_data, args.embeddings_file)
  # report
  print 'score={}, coverage={}'.format(score, coverage)

if __name__ == '__main__':
  main(sys.argv)
