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
import eval_wordsim
import eval_translate
import eval_qvec
import eval_parse
import eval_classify
import os

def get_vocab(eval_dirs):
  vocab = set()
  for dir_path in eval_dirs:
    if not os.path.isdir(dir_path):
      print 'the following data directory in the tasks_datasets file does not exist: {}'.format(dir_path)
      assert False
    if dir_path.startswith('eval-data/wordsim'):
      vocab |= eval_wordsim.get_relevant_word_types(dir_path + '/annotated_word_pairs')
    elif dir_path.startswith('eval-data/word_translation'):
      vocab |= eval_translate.get_relevant_word_types(dir_path + '/dictionary')[0]
    elif dir_path.startswith('eval-data/qvec'):
      vocab |= eval_qvec.get_relevant_word_types(dir_path + '/semantic_classes')
    elif dir_path.startswith('eval-data/parsing'):
      vocab |= eval_parse.get_relevant_word_types(dir_path + '/train_treebank', dir_path + '/test_treebank')
    elif dir_path.startswith('eval-data/classification'):
      vocab |= eval_classify.get_relevant_word_types(dir_path + '/document-representations/data/idfs/idf.all')
    else:
      assert(False)
  return vocab

def get_eval_dirs(tasks_datasets_filename):
  eval_dirs = []
  for line in open(tasks_datasets_filename):
    if len(line.strip()) == 0 or line.strip().startswith("#"): continue
    splits = line.strip().strip().split()
    assert len(splits) == 4
    eval_dirs.append(splits[1])
  return eval_dirs

def main(argv):
  # parse/validate arguments
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-tasks_datasets", help="(input) a file that describes the available evaluation tasks and their data, e.g., https://github.com/wammar/multilingual-embeddings-eval-portal/blob/master/tasks_datasets")
  argparser.add_argument("-vocab", help="(output) write the evaluation vocabulary to this file.")
  args = argparser.parse_args()

  # read the tasks_datasets file
  eval_dirs = get_eval_dirs(args.tasks_datasets)

  # collect vocabulary from evaluation scripts
  vocab = get_vocab(eval_dirs)

  # write vocabulary to file
  with io.open(args.vocab, encoding='utf8', mode='w') as vocab_file: vocab_file.write('\n'.join(vocab))
  print 'evaluation vocabulary size is {}, written to {}'.format(len(vocab), args.vocab)

if __name__ == '__main__':
  main(sys.argv)
