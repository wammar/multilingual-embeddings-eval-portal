# I/O patch to multilingual-embeddings-eval-portal
This repo is a fork of [multilingual-embeddings-eval-portal](https://github.com/wammar/multilingual-embeddings-eval-portal) and contains a fix for the character encoding related issue which caused certain words to be treated as OOV even when they were included in the embeddings file.
(The reason behind this was an inconsistent use of `io.open` which got fixed (actually removed) in this repo.)

The sample embedding file (da_en_fa.vec) contains the first 500 embeddings from the [fasttext embeddings](https://fasttext.cc/docs/en/pretrained-vectors.html) trained over the Wikipedia for Danish (da), English (en) and Farsi (fa).

Using this repo, the evaluation script  
`python2 eval_translate.py -embeddings-file da_en_fa.vec -eval-data eval-data/word_translation/google.fa-en.dev/`
gives us the below output:  
`score=0.2, coverage=0.00446030330062`  
whereas the code from the original repo would yield:  
`score=0.0, coverage=0.0`

As an additional example, invoking the below command  
`python2 eval_cvec.py -embeddings-file da_en_fa.vec -eval-data eval-data/qvec/dev-da`  
with this version of the evaluation framework results in the output  
`score=1.0, coverage=0.0337188786512`  
as opposed to  
`score=1.0, coverage=0.0301901587924`  
provided by the original code base.
