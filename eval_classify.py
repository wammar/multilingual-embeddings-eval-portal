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
import glob
import IPython as ipy

def get_relevant_word_types(idf_filename):
  # find relevant words
  relevant_words = set()
  with io.open(idf_filename, encoding='utf8') as idf_file:
    for line in idf_file:
      relevant_words.add(line.strip().split('\t')[0])
  return relevant_words

def copy_relevant_embeddings_only(raw_embeddings_filename, filtered_embeddings_filename, idf_filename):
  relevant_words = get_relevant_word_types(idf_filename)

  covered_words, all_words = 0.0, len(relevant_words)
  # read and write embeddings of relevant words only
  with io.open(raw_embeddings_filename, encoding='utf8') as raw_embeddings_file, io.open(filtered_embeddings_filename, encoding='utf8', mode='w') as filtered_embeddings_file:
    for line in raw_embeddings_file:
      word = line.split(' ')[0]
      if word not in relevant_words: continue
      filtered_embeddings_file.write(line)
      relevant_words.remove(word)
      covered_words += 1.0

  return covered_words / all_words

def classification_wrapper(eval_data_dirname, embeddings_filename):
  unique_path = os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999)))
  score_filename = unique_path+'.score'
  embeddings_loc = unique_path+'.embs'
  working_dirname = os.path.abspath(os.path.join(eval_data_dirname, 'document-representations/scripts/X2X'))
  idf_filename = os.path.abspath(os.path.join(eval_data_dirname, 'document-representations/data/idfs/idf.all'))
  FNULL = open(os.devnull, 'w')

  # copy the embeddings including prefix
  coverage = copy_relevant_embeddings_only(embeddings_filename, embeddings_loc, idf_filename)

  # prepare data
  command = "cd {} && ./prepare-data-1000-multi.ch all all {}".format(working_dirname, os.path.abspath(unique_path))
  print command
  subprocess.call([command], shell=True)
#                   shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

  # train and test
  command = "cd {} && ./run-perceptron-1000-multi.ch all all {} > {}".format(working_dirname, os.path.abspath(unique_path), os.path.abspath(score_filename))
  print command
  subprocess.call([command], shell=True)
# shell=True, stdout=FNULL, stderr=subprocess.STDOUT)

  score_string = ''
  with open(score_filename) as score_file:
    score_string = score_file.read().split()[-1]
  score = float(score_string)

  # clean the files you created
  for temp_file in glob.glob(unique_path+"*"):
    os.remove(temp_file)
  return (score, coverage)

def evaluate(eval_data_dir, embeddings_filename):
  (score, coverage) = classification_wrapper(eval_data_dir, embeddings_filename)
  return (score, coverage,)

def main(argv):
  # parse/validate arguments
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-eval-data", help="Path to a directory which contains all data files needed to setup the evaluation script.")
  argparser.add_argument("-embeddings-file", help="Path to the embeddings file (lowercased, UTF8-encoded, space-delimited, optional: suffix .gz indicate the file is gzip compressed.)")
  args = argparser.parse_args()
  print "embeddings file:", args.embeddings_file
  print "eval-data:", args.eval_data
  # evaluate
  score, coverage = evaluate(args.eval_data, args.embeddings_file)
  # report
  print 'score={}, coverage={}'.format(score, coverage)

if __name__ == '__main__':
  main(sys.argv)
