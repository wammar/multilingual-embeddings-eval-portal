#!/usr/bin/env python

import gzip
import argparse
import random
import io
import os
import sys
from read_write import read_word_vectors
from read_write import gzopen
from qvec_scripts.qvec import OracleMatrix, VectorMatrix, AlignColumns
from qvec_scripts.qvec_cca import GetVocab, ReadOracleMatrix, ReadVectorMatrix, WriteMatrix
import subprocess

def get_qvec_gold_filename():
  return 'semantic_classes'

def get_relevant_word_types(eval_data_filename):
  relevant_word_types = set()
  with io.open(eval_data_filename, encoding='utf8') as eval_data_file:
    for line in eval_data_file:
      splits = line.strip().split('\t')
      assert len(splits) > 0
      word = splits[0]
      relevant_word_types.add(word)
  return relevant_word_types

def get_relevant_embeddings_filename(eval_data_filename, embeddings_filename):
  # We only need embeddings for a subset of word types. Copy the relevant embeddings in a new plain file.
  relevant_embeddings_filename = os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999)))
  relevant_word_types = set(get_relevant_word_types(eval_data_filename))
  with gzopen(embeddings_filename) as all_embeddings_file:
    with open(relevant_embeddings_filename, mode='w') as relevant_embeddings_file:
      for line in all_embeddings_file:
        line = line.decode('utf8')
        if line.split(' ')[0] not in relevant_word_types: continue
        line = line.encode('utf8')
        relevant_embeddings_file.write(line)
  return relevant_embeddings_filename

def compute_coverage(semantic_classes_file, word_vecs):
  not_found, total_size = (0, 0)
  for line in io.open(semantic_classes_file, encoding='utf8'):
    splits = line.strip().lower().split('\t')
    assert len(splits) > 0
    word = splits[0]
    total_size += 1    
    if word not in word_vecs:
      not_found += 1
  assert total_size > 0
  return 1.0 - (not_found * 1.0 / total_size)

def qvec_cca_wrapper(in_oracle, in_vectors):
  oracle_files = [in_oracle]
  vocab_oracle = GetVocab(oracle_files, vocab_union=True)
  vocab_vectors = GetVocab([in_vectors])
  vocab = sorted(set(vocab_vectors) & set(vocab_oracle))
  
  column_names, tmp_matrix = None, None
  for filename in oracle_files:
    oracle_matrix, column_names, tmp_matrix = ReadOracleMatrix(
         filename, vocab, column_names, tmp_matrix)

  vsm_matrix = ReadVectorMatrix(in_vectors, vocab)

  vsm_filename = os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999)))
  print 'temporary vsm_filename={}'.format(vsm_filename)
  WriteMatrix(vsm_matrix, vsm_filename)
  oracle_filename = os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999)))
  print 'temporary oracle_filename={}'.format(oracle_filename)
  WriteMatrix(oracle_matrix, oracle_filename)

  FNULL = open(os.devnull, 'w')
  qvec_scripts_dir = os.path.join(os.path.dirname(__file__), 'qvec_scripts')
  score_filename = os.path.join(os.path.dirname(__file__), 'temp', str(random.randint(100000, 999999)))
  print 'temporary score_filename={}'.format(score_filename)
  subprocess.call(["cd {} && matlab -nosplash -nodisplay -r \"cca(\'{}\',\'{}\',\'{}\')\"".format(qvec_scripts_dir, os.path.abspath(vsm_filename), os.path.abspath(oracle_filename), os.path.abspath(score_filename))], shell=True, 
                  #stdout=FNULL, 
                  stderr=subprocess.STDOUT)
  score_string = ''
  with open(score_filename, 'r') as score_file:
    score_string = score_file.read()
  score = float(score_string)
  os.remove(vsm_filename)
  os.remove(oracle_filename)
  os.remove(score_filename)
  return score

def evaluate(eval_data_dir, embeddings_filename):
  eval_data_filename = '{}/{}'.format(eval_data_dir, get_qvec_gold_filename())
  relevant_embeddings_filename = get_relevant_embeddings_filename(eval_data_filename, embeddings_filename)
  word_vecs = read_word_vectors(relevant_embeddings_filename)
  coverage = compute_coverage(eval_data_filename, word_vecs)
  score = qvec_cca_wrapper(eval_data_filename, relevant_embeddings_filename)
  os.remove(relevant_embeddings_filename)
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
