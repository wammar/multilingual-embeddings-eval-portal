#vars
embeddings_path=~/compare-classification/document-representations/data/embeddings
results_path=~/compare-classification/document-representations/results
rcv_path=~/compare-classification/rcv_scripts
train_path=~/compare-classification/document-representations/data/rcv-from-binod/train
script_path=~/compare-classification/document-representations/scripts/X2X

# USAGE
# ./compare-embeddings.sh train_language test_language run_id
# EXAMPLE
# ./compare-embeddings.sh it es 1 #trains classifier on Italian documents, tests on Spanish documents

L1=$1 #train language
L2=$2 #test language

if [ ! $L1 ] || [ ! $L2 ]
then
	echo languages not specified
	exit 1
fi

if [ ! ${3} ]; then
	echo 'no run id provided, using current date and time'
	run_id=${1}2${2}_$(date +'%m_%d_%k:%M')
	echo $run_id
else
	run_id=${1}2${2}_${3}
fi

mkdir ${results_path}/${run_id}
echo results will be written to ${results_path}/${run_id}

#average over multiple runs
for data_split in 1 2 3 4 5
do
	#create the main train/test sets used to evaluate crosslingual classification
	(cd $rcv_path && python generate_train_test_splits.py ${L1} ${L2})
	#create subsets within each language's train sets to evaluate monolingual classification
	(cd $train_path && python create_monolingual_valid_splits.py ${L1} ${L2} )

	#place embeddings in ${embeddings_path}
	for embs in wiki_embeddings
	do
	    if [ ! -e ${embeddings_path}/${embs} ]; then
			echo embeddings file does not exist. Make sure the file is in ${embeddings_path}/${embs} and edit compare-embeddings.sh if necessary
			exit 1
		fi

		(cd $rcv_path && python filter_embeddings_by_language.py ${embeddings_path}/${embs} ${L1} ${L2} )

		subdir=${results_path}/${run_id}/${embs}

		if [ ! -e ${subdir} ]; then
			mkdir $subdir
		fi

		#split embeddings into language-specific files
		filename=${subdir}/iter_${data_split}_${1}2${2}.result
		cp ${embeddings_path}/${embs}.${L1} ${embeddings_path}/my-embeddings.${L1}
		cp ${embeddings_path}/${embs}.${L2} ${embeddings_path}/my-embeddings.${L2}

		#train and run classifier
		(cd ${script_path} && ./prepare-data-klement-4cat-train-valid-my-embeddings.ch ${L1} )
		(cd ${script_path} && ./prepare-data-klement-4cat-all-sizes-my-embeddings.ch ${L1} ${L2} )
		echo
		echo 'PREPARED DATA'
		echo
		echo MONOLINGUAL > ${filename}
		(cd ${script_path} && ./run-perceptron-train-valid-my-embeddings.ch ${L1} >> ${filename} )
		echo CROSSLINGUAL >> ${filename}
		(cd ${script_path} && ./run-perceptron-all-sizes-my-embeddings.ch ${L1} ${L2} >> ${filename} )

		echo results saved to ${filename}
	done
done

#read results files, get average, and save to summary.result
(cd $rcv_path && python get_average_scores.py ${L1} ${L2} ${results_path}/${run_id})

