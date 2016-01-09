import glob
import io

desired_langs = 'bg,cs,da,de,el,en,es,fi,fr,hu,it,sv'.split(',')

for filename in glob.glob('ud1.1-dev/*')+glob.glob('ud1.1-test/*'):
  print 'processing {}'.format(filename)
  dev_or_test = filename.split('/')[0].split('-')[1]
  print 'its a {} directory'.format(dev_or_test)
  destination_dir = 'ud1.1-' + '+'.join(desired_langs) + '-' + dev_or_test + '/'
  basename = filename.split('/')[1]
  arcstd = basename.endswith('arcstd')
  if arcstd:
    with io.open(destination_dir+basename, encoding='utf8', mode='w') as output_file:
      output_file.write(u'\n')
      current_lang = ''
      for line in io.open(filename, encoding='utf8'):
        # the first line in a new sentence.
        # lets see if its language is desired 
        if line.startswith('[]['):
          current_lang = line[3:5]

        # skip undesirable sentences
        if current_lang not in desired_langs:
          continue

        # and print the rest
        output_file.write(line)

  else:
    with io.open(destination_dir+basename, encoding='utf8', mode='w') as output_file:
      current_lang = ''
      for line in io.open(filename, encoding='utf8'):
        if line.startswith('1\t'): 
            if current_lang != line[2:4]: 
                current_lang = line[2:4]
                print current_lang
        if current_lang not in desired_langs: continue 
        output_file.write(line)
      output_file.write(u'\n')
