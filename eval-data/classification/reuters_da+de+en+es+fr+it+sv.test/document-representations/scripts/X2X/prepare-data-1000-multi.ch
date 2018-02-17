datapath=../../data

L1=$1 #train dir
L2=$2 #test dir
unique_id=$3

if [ ! $L1 ] || [ ! $L2 ]
then
	echo languages not specified
	exit 1
fi
if [ ! $unique_id ]
then
	unique_id=0
fi

echo [Preparing test set for ${L2}]
java -ea -Xmx12000m  -cp ../../bin CollectionPreprocessor --text-dir $datapath/rcv-from-binod/test/${L2} --idf $datapath/idfs/idf.${L2} --word-embeddings ${unique_id}.embs --vector-file ${unique_id}.test-my-embeddings.${L2}-${L1}.${L2}

echo [Preparing train set for ${L1}]
java -ea -Xmx12000m  -cp ../../bin CollectionPreprocessor --text-dir $datapath/rcv-from-binod/train/${L1}1000 --idf $datapath/idfs/idf.${L1} --word-embeddings ${unique_id}.embs  --vector-file ${unique_id}.train-my-embeddings.${L2}-${L1}1000.${L1}

