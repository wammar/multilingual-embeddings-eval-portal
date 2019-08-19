#!/usr/bin/env python

import argparse
import random
import io
import sys
from read_write import read_word_vectors
from read_write import gzopen
from qvec_scripts.qvec import OracleMatrix, VectorMatrix, AlignColumns 
#from .qvec_scripts.ranking import *

def get_qvec_gold_filename():
  return 'semantic_classes'

def get_relevant_word_types(eval_data_filename):
  relevant_word_types = set()
  with open(eval_data_filename) as eval_data_file:
    for line in eval_data_file:
      splits = line.strip().split('\t')
      assert len(splits) > 0
      word = splits[0]
      relevant_word_types.add(word)
  return relevant_word_types

def get_relevant_embeddings_filename(eval_data_filename, embeddings_filename):
  # We only need embeddings for a subset of word types. Copy the relevant embeddings in a new plain file.
  if not os.path.isdir('temp'): os.mkdir('temp') 
  relevant_embeddings_filename = os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999)))
  relevant_word_types = set(get_relevant_word_types(eval_data_filename))
  with gzopen(embeddings_filename) as all_embeddings_file:
    with open(relevant_embeddings_filename, mode='w') as relevant_embeddings_file:
      for line in all_embeddings_file:
        if line.split(' ')[0] not in relevant_word_types: continue
        relevant_embeddings_file.write(line)
  return relevant_embeddings_filename

def compute_coverage(semantic_classes_file, word_vecs):
  not_found, total_size = (0, 0)
  for line in open(semantic_classes_file):
    splits = line.strip().lower().split('\t')
    assert len(splits) > 0
    word = splits[0]
    total_size += 1
    if word not in word_vecs:
      not_found += 1
  assert total_size > 0
  return 1.0 - (not_found * 1.0 / total_size)

def qvec_wrapper(in_oracle, in_vectors):
  oracle_matrix = OracleMatrix()
  oracle_matrix.AddMatrix(in_oracle)
  vsm_matrix = VectorMatrix()
  top_k = 0
  vsm_matrix.AddMatrix(in_vectors, top_k)
  alignments, score = AlignColumns(vsm_matrix, oracle_matrix, 'correlation')
  return score

def evaluate(eval_data_dir, embeddings_filename):
  eval_data_filename = '{}/{}'.format(eval_data_dir, get_qvec_gold_filename())
  relevant_embeddings_filename = get_relevant_embeddings_filename(eval_data_filename, embeddings_filename)
  word_vecs = read_word_vectors(relevant_embeddings_filename)
  coverage = compute_coverage(eval_data_filename, word_vecs)
  score = qvec_wrapper(eval_data_filename, relevant_embeddings_filename)
  os.remove(relevant_embeddings_filename)
  embedding_size = len(word_vecs[next(iter(word_vecs))])
  return (score / embedding_size, coverage,)

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
