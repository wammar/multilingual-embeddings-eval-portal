#!/usr/bin/env python

import gzip
import argparse
import random
import io
import os
import sys
from read_write import read_word_vectors
from read_write import gzopen
from wordsim_scripts.ranking import *

def gzopen(f):
  return gzip.open(f) if f.endswith('.gz') else open(f)

def get_relevant_word_types(eval_data_filename):
  relevant_word_types = set()
  with io.open(eval_data_filename, encoding='utf8') as eval_data_file:
    for line in eval_data_file:
      word1, word2, similarity = line.strip().split('\t')
      relevant_word_types.add(word1)
      relevant_word_types.add(word2)
  return relevant_word_types

def get_relevant_embeddings_filename(eval_data_filename, embeddings_filename):
  # We only need embeddings for a subset of word types. Copy the relevant embeddings in a new plain file.
  relevant_embeddings_filename = os.path.join(os.path.dirname(__file__), 'relevant_embeddings', str(random.randint(100000, 999999)))
  relevant_word_types = set(get_relevant_word_types(eval_data_filename))
  with gzopen(embeddings_filename) as all_embeddings_file:
    with open(relevant_embeddings_filename, mode='w') as relevant_embeddings_file:
      for line in all_embeddings_file:
        line = line.decode('utf8')
        if line.split(' ')[0] not in relevant_word_types: continue
        line = line.encode('utf8')
        relevant_embeddings_file.write(line)
  return relevant_embeddings_filename

def compute_similarities_and_coverage(word_sim_file, word_vecs):
  manual_dict, auto_dict = ({}, {})
  not_found, total_size = (0, 0)
  for line in io.open(word_sim_file, encoding='utf8'):
    line = line.strip().lower()
    word1, word2, val = line.strip().split('\t')
    if word1 in word_vecs and word2 in word_vecs:
      manual_dict[(word1, word2)] = float(val)
      auto_dict[(word1, word2)] = cosine_sim(word_vecs[word1], word_vecs[word2])
    else:
      not_found += 1
      print 'not found:', word1, word2
    total_size += 1    
  return (manual_dict, auto_dict, 1.0 - (not_found * 1.0 / total_size))

def get_wordsim_gold_filename():
  return 'annotated_word_pairs'

def evaluate(eval_data_dir, embeddings_filename):
  eval_data_filename = '{}/{}'.format(eval_data_dir, get_wordsim_gold_filename()) 
  word_vecs = read_word_vectors(get_relevant_embeddings_filename(eval_data_filename, embeddings_filename))
  manual_dict, auto_dict, coverage = compute_similarities_and_coverage(eval_data_filename, word_vecs)
  ranked_manual_dict, ranked_auto_dict = assign_ranks(manual_dict), assign_ranks(auto_dict)
  score = spearmans_rho(ranked_manual_dict, ranked_auto_dict)
  return (score, coverage,)

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
