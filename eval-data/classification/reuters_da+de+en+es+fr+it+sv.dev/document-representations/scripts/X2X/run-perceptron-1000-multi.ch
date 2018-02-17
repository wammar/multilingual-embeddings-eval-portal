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

echo "Training on ${L1}1000"
java  -ea -Xmx2000m -cp ../../bin ApLearn  --train-set  ${unique_id}.train-my-embeddings.${L2}-${L1}1000.${L1}  --model-name ${unique_id}.avperc.${L2}-${L1}.${L2}   --epoch-num 10
java  -ea -Xmx2000m -cp ../../bin   ApClassify  --test-set ${unique_id}.test-my-embeddings.${L2}-${L1}.${L2}  --model-name ${unique_id}.avperc.${L2}-${L1}.${L2}



