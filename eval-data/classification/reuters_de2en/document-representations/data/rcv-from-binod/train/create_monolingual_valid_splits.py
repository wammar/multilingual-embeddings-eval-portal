import os
import random
import shutil
import sys

train_frac = 0.8
random.seed(1234)

languages  = sys.argv[1:]

for lang in languages:
    name1 = lang+'1000'
    name2 = lang+'1000_train_valid'

    if os.path.isdir(name2):
        shutil.rmtree(name2)
    if os.path.isdir('../test/'+name2):
        shutil.rmtree('../test/'+name2)
    os.mkdir(name2)
    os.mkdir('../test/'+name2)

    for dir in ['C','E','G','M']:
        l = os.listdir(name1+'/'+dir)
        os.mkdir(name2+'/'+dir)
        os.mkdir('../test/'+name2+'/'+dir)
        random.shuffle(l)
        train_size = int(train_frac*len(l))
        train = l[:train_size]
        valid = l[train_size:]
        for f in train:
            shutil.copy(name1+'/'+dir+'/'+f,name2+'/'+dir+'/'+f)
        for f in valid:
            shutil.copy(name1+'/'+dir+'/'+f,'../test/'+name2+'/'+dir+'/'+f)

    print "created monolingual train/validation splits for", lang
    print name2
        
