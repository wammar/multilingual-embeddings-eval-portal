import shutil
import io
import os
import glob

# twelve: desired_langs = set('bg,cs,da,de,el,en,es,fi,fr,hu,it,sv'.split(','))
# fifty nine: 
desired_langs = set("bg|cs|da|de|el|en|es|fi|fr|hu|it|sv|zh|af|ca|iw|cy|ar|ga|zu|et|gl|id|ru|nl|pt|la|tr|ne|lv|lt|tg|ro|is|pl|yi|be|hy|hr|jw|ka|ht|fa|mi|bs|ja|mg|tl|ms|uz|kk|sr|mn|ko|mk|so|uk|sl|sw".split('|'))

processed = set()

test_file = io.open('google.fifty_nine.test/dictionary', encoding='utf8', mode='w')
dev_file = io.open('google.fifty_nine.dev/dictionary', encoding='utf8', mode='w')

translations_counter = 0
for filename in glob.glob('google.*-en.dev')+glob.glob('google.*-en.test'):
  print 'processing', filename
  dev_or_test = filename.split('.')[-1]

  lang1, lang2 = filename.split('.')[1].split('-')
  if lang1 not in desired_langs or lang2 not in desired_langs: continue
  processed.add( (lang1,lang2,) )
  if (lang2,lang1,) in processed: continue

  for line in io.open(filename+'/dictionary', encoding='utf8'):
    if dev_or_test == 'dev':
      dev_file.write(line)
    elif dev_or_test == 'test':
      test_file.write(line)
    else:
      assert False

test_file.close()
dev_file.close()
