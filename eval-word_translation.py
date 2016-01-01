#!/usr/bin/env python

import gzip
import argparse
import random
import io
import os
import sys
import numpy
from numpy.linalg import norm
from read_write import read_word_vectors
from read_write import gzopen

EPSILON = 1e-6

def euclidean(vec1, vec2):
  diff = vec1 - vec2
  return math.sqrt(diff.dot(diff))

def cosine_sim(vec1, vec2):
  vec1 += EPSILON * numpy.ones(len(vec1))
  vec2 += EPSILON * numpy.ones(len(vec1))
  return vec1.dot(vec2)/(norm(vec1)*norm(vec2))

def get_word_translation_gold_filename():
  return 'dictionary'

def get_relevant_word_types(eval_data_filename):
  relevant_word_types = set()
  relevant_word_pairs = set()
  with io.open(eval_data_filename, encoding='utf8') as eval_data_file:
    for line in eval_data_file:
      splits = line.strip().lower().split(' ||| ')
      assert len(splits) == 2
      relevant_word_types |= set(splits)
      relevant_word_pairs.add( (splits[0], splits[1],) )
  return relevant_word_types, relevant_word_pairs

def get_relevant_embeddings_filename(relevant_word_types, embeddings_filename):
  # We only need embeddings for a subset of word types. Copy the relevant embeddings in a new plain file.
  relevant_embeddings_filename = os.path.join(os.path.dirname(__file__), 'relevant_embeddings', str(random.randint(100000, 999999)))
  with gzopen(embeddings_filename) as all_embeddings_file:
    with open(relevant_embeddings_filename, mode='w') as relevant_embeddings_file:
      for line in all_embeddings_file:
        line = line.decode('utf8')
        if line.split(' ')[0] not in relevant_word_types: 
          continue
        line = line.encode('utf8')
        relevant_embeddings_file.write(line)
  return relevant_embeddings_filename

def compute_coverage(dictionary_file, word_vecs):
  not_found, total_size = (0, 0)
  for line in io.open(dictionary_file, encoding='utf8'):
    splits = line.strip().lower().split(' ||| ')
    assert len(splits) == 2
    word1, word2 = splits
    total_size += 1    
    if word1 not in word_vecs or word2 not in word_vecs:
      not_found += 1
  assert total_size > 0
  return 1.0 - (not_found * 1.0 / total_size)

def compute_precision_at_k(relevant_word_pairs, word_vecs, precision_at_k):
  assert precision_at_k >= 1
  total, correct = 0.0, 0.0
  # for each pair in the evaluation dictionary
  for gold_pair in relevant_word_pairs:
    if gold_pair[0] not in word_vecs or gold_pair[1] not in word_vecs: 
      continue
    gold_src, gold_tgt = gold_pair
    # compute cosine similarity
    gold_similarity = cosine_sim(word_vecs[gold_src], word_vecs[gold_tgt])
    # then count the number of tgt words which are more similar than the correct translation.
    count_of_more_similar_tgts = 0
    for candidate_pair in relevant_word_pairs:
      if candidate_pair[0] not in word_vecs or candidate_pair[1] not in word_vecs: continue
      candidate_tgt = candidate_pair[1]
      if candidate_tgt == gold_tgt: continue
      similarity = cosine_sim(word_vecs[gold_src], word_vecs[candidate_tgt])      
      if similarity > gold_similarity: count_of_more_similar_tgts += 1
    # if the number of more similar tgt words is > precision_at_k - 1, there's a problem 
    total += 1
    if count_of_more_similar_tgts < precision_at_k: correct += 1

  assert total > 0
  score = correct / total
  return score
    
def evaluate(eval_data_dir, embeddings_filename):
  eval_data_filename = '{}/{}'.format(eval_data_dir, get_word_translation_gold_filename())
  relevant_word_types, relevant_word_pairs = get_relevant_word_types(eval_data_filename)
  relevant_embeddings_filename = get_relevant_embeddings_filename(relevant_word_types, embeddings_filename)
  word_vecs = read_word_vectors(relevant_embeddings_filename)
  coverage = compute_coverage(eval_data_filename, word_vecs)
  score = compute_precision_at_k(relevant_word_pairs, word_vecs, 1)
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
