import shutil
import io
import os
import glob

# twelve: desired_langs = set('bg,cs,da,de,el,en,es,fi,fr,hu,it,sv'.split(','))
# fifty nine: 
desired_langs = set("bg|cs|da|de|el|en|es|fi|fr|hu|it|sv|zh|af|ca|iw|cy|ar|ga|zu|et|gl|id|ru|nl|pt|la|tr|ne|lv|lt|tg|ro|is|pl|yi|be|hy|hr|jw|ka|ht|fa|mi|bs|ja|mg|tl|ms|uz|kk|sr|mn|ko|mk|so|uk|sl|sw".split('|'))

processed = set()

test_file = io.open('wiktionary.fifty_nine.test/dictionary', encoding='utf8', mode='w')
dev_file = io.open('wiktionary.fifty_nine.dev/dictionary', encoding='utf8', mode='w')

translations_counter = 0
for filename in glob.glob('wiktionary.*-*'):
  if filename.endswith('dev') or filename.endswith('test'): continue
  print 'processing', filename

  lang1, lang2 = filename[-5:-3], filename[-2:]
  if lang1 not in desired_langs or lang2 not in desired_langs: continue
  processed.add( (lang1,lang2,) )
  if (lang2,lang1,) in processed: continue
  
  for line in io.open(filename, encoding='utf8'):
    word1, word2 = line.strip().split(' ||| ')
    line = u'{}:{} ||| {}:{}\n'.format(lang1, word1, lang2, word2)
    translations_counter += 1
    if translations_counter % 2 == 0:
      test_file.write(line)
    else:
      dev_file.write(line)

test_file.close()
dev_file.close()
