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

def get_vocab(eval_dirs):
  vocab = set()
  for dir_path in eval_dirs[0]:
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

def main(argv):
  # parse/validate arguments
  argparser = argparse.ArgumentParser()
  argparser.add_argument("-eval-dirs", nargs='+', action='append', 
                         help="(input) paths to all directories which contain all data files needed to setup the evaluation script.")
  argparser.add_argument("-vocab-file", help="(output) write the evaluation vocabulary to this file.")
  args = argparser.parse_args()

  # collect vocabulary from evaluation scripts
  vocab = get_vocab(args.eval_dirs)

  # write vocabulary to file
  with io.open(args.vocab_file, encoding='utf8', mode='w') as vocab_file: vocab_file.write('\n'.join(vocab))
  print 'evaluation vocabulary size is {}, written to {}'.format(len(vocab), args.vocab_file)

if __name__ == '__main__':
  main(sys.argv)
