export lang1="PT"
export lang1_lower="pt"
export lang2="FA"
export lang2_lower="fa"

# download the corpus
wget http://lcl.uniroma1.it/similarity-datasets/datasets/rg65_$lang1-$lang2.txt

# add language prefixes
python ~/wammar-utils/add-prefix-to-conll-column.py -i rg65_$lang1-$lang2.txt -o rg65_$lang1-$lang2.txt.$lang1_lower -j 1 -p $lang1_lower:
python ~/wammar-utils/add-prefix-to-conll-column.py -i rg65_$lang1-$lang2.txt.$lang1_lower -o rg65_$lang1-$lang2.txt.$lang1_lower-$lang2_lower -j 2 -p $lang2_lower:
rm rg65_$lang1-$lang2.txt.$lang1_lower
mv rg65_$lang1-$lang2.txt.$lang1_lower-$lang2_lower rg65_$lang1-$lang2.txt

# create subdirectories
mkdir $lang1_lower+$lang2_lower.rg65.dev
mkdir $lang1_lower+$lang2_lower.rg65.test

# split the corpus in test and dev
python ~/wammar-utils/vertical-split-corpus.py -r 0:1:1 --corpusFilename rg65_$lang1-$lang2.txt -t ~/dummy.rm --devFilename ./$lang1_lower+$lang2_lower.rg65.dev/annotated_word_pairs --testFilename ./$lang1_lower+$lang2_lower.rg65.test/annotated_word_pairs
rm rg65_$lang1-$lang2.txt
