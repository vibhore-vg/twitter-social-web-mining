# 
# svm_save_model('libsvm.model', m)
# m = svm_load_model('libsvm.model')
import re
from nltk.tokenize import sent_tokenize
import sys
from nltk.corpus import PlaintextCorpusReader
sys.path.append('/Users/oliverfengpet/Program/nlp/python_parser/no_index/libsvm-3.12/python/')
from svmutil import *
from nltk.tokenize import word_tokenize
from progressbar import *
import emoticons
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()
sys.path.append('/Users/oliverfengpet/Dropbox/TwitterAffect/liblinear-1.93/python')
from liblinearutil import *
sys.path.append('/Users/oliverfengpet/Program/nlp/python_parser/no_index/libsvm-3.12/python/')
from svmutil import *

Training_Path = "/Users/oliverfengpet/Dropbox/TwitterAffect/Data/Training"
Testing_Path = "/Users/oliverfengpet/Dropbox/TwitterAffect/Data/Testing"
TFIDF_Path = "/Users/oliverfengpet/Dropbox/TwitterAffect/TFIDF_RAW.txt"


label_map ={'Training_Happy.txt':1,'Training_Angry.txt':0,'Training_Sad.txt':0,'Training_Ashamed.txt':0,'Training_Afraid.txt':0}
test_label_map ={'Test_Happy.txt':1,'Test_Angry.txt':0,'Test_Sad.txt':2,'Test_Ashamed.txt':3,'Test_Afraid.txt':4}


def load_collection_sentence(directory):
	# files_all = PlaintextCorpusReader(directory,'.*')
	# print files_all
	# result = sent_tokenize(files_all.raw().lower())
	# print result
	result = []
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		for line in of.readlines():
			result.append(line.lower())
	#print len(result)
	return result

def create_feature_space(sentences):
	a={}
	#p = re.compile('\w+')
	for i in range(0,len(sentences)):
		#sentences[i] = sentences[i].decode('utf-8')
		#sentences[i] = sentences[i].decode('utf-8','ignore')	
		#k = p.findall(sentences[i])
		k=word_tokenize(sentences[i])
		g = re.finditer(emoticons.Emoticon_RE,sentences[i])
		for ma in g:
			k.append(ma.group())
		for j in range(0, len(k)):
			k[j] = st.stem(k[j])
			if k[j] not in a:
				a[k[j]]=len(a)
	return a


def create_featuer_space_TFIDF(file):
	a={}
	f = open(file)
	for line in f.readlines():
		line = line.replace("'","")
		k=line.split(',')
		for j in range(0, len(k)):
			k[j] = k[j].strip()
			if k[j] not in a:
				a[k[j]]=len(a)
	return a

def vectorize(feature_space, sentence):
	k = word_tokenize(sentence)
	g = re.finditer(emoticons.Emoticon_RE,sentence)
	for ma in g:
		k.append(ma.group())
	for i in range(0,len(k)):
		k[i] = st.stem(k[i])
	
	result = []
	result = [0] * len(feature_space)
	for key in feature_space:
		if key in k:
			result[feature_space[key]]+=1
		else:
			result[feature_space[key]]=0
	return result
	

def Training(directory):
	# -s svm_type : set type of SVM (default 0)
	# 	0 -- C-SVC
	# 	1 -- nu-SVC
	# 	2 -- one-class SVM
	# 	3 -- epsilon-SVR
	# 	4 -- nu-SVR
	# -t kernel_type : set type of kernel function (default 2)
	# 	0 -- linear: u'*v
	# 	1 -- polynomial: (gamma*u'*v + coef0)^degree
	# 	2 -- radial basis function: exp(-gamma*|u-v|^2)
	# 	3 -- sigmoid: tanh(gamma*u'*v + coef0)
	# -d degree : set degree in kernel function (default 3)
	# -g gamma : set gamma in kernel function (default 1/num_features)
	# -r coef0 : set coef0 in kernel function (default 0)
	# -c cost : set the parameter C of C-SVC, epsilon-SVR, and nu-SVR (default 1)
	# -n nu : set the parameter nu of nu-SVC, one-class SVM, and nu-SVR (default 0.5)
	# -p epsilon : set the epsilon in loss function of epsilon-SVR (default 0.1)
	# -m cachesize : set cache memory size in MB (default 100)
	# -e epsilon : set tolerance of termination criterion (default 0.001)
	# -h shrinking: whether to use the shrinking heuristics, 0 or 1 (default 1)
	# -b probability_estimates: whether to train a SVC or SVR model for probability estimates, 0 or 1 (default 0)
	# -wi weight: set the parameter C of class i to weight*C, for C-SVC (default 1)

	#The k in the -g option means the number of attributes in the input data.
	vectors = []
	labels = []
	sentences = load_collection_sentence(directory)
	feature_space = create_feature_space(sentences)
	print len(feature_space)
	# try:
	#    with open('libsvm_SVC_Present.model'): 
	# 		m = svm_load_model('libsvm_SVC_Present.model')
	# 		return [m,feature_space]
	# except IOError:
	#    print 'Start Training Over.'
	
	count = 0
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		count+=len(of.readlines())
	widgets = ['Train_Vectorize: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
		        ' ', ETA(), ' ', FileTransferSpeed()]
	pbar = ProgressBar(widgets=widgets, maxval=count)
	pbar.start()
	curCount = 0
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		for line_num, line in enumerate(of.readlines()):
			vector = vectorize(feature_space,line)
			vectors.append(vector)
			labels.append(label_map[f])
			pbar.update(curCount)
			curCount+=1
			#print label_map[f]
			#print line
	
	pbar.finish()
	#prob  = problem(labels, vectors)
	#print 'get here'
	#param = parameter('-s 0 -b 1')
	#print 'get here'
	m1 = svm_train(labels,vectors, '-s 0 -b 1 -t 0')
	#print 'get here'
	svm_save_model('libsvm_SVC_stem_emoticons_Happy.model', m1)
	return [m1,feature_space]

def Testing(directory,m1,feature_space):
	vectors = []
	labels = []
	count = 0
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		count+=len(of.readlines())
	widgets = ['Test_Vectorize: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
			        ' ', ETA(), ' ', FileTransferSpeed()]
	pbar = ProgressBar(widgets=widgets, maxval=count)
	pbar.start()
	
	curCount=0
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		for line_num, line in enumerate(of.readlines()):
			vector = vectorize(feature_space,line)
			#print vector
			vectors.append(vector)
			#print test_label_map[f]
			labels.append(test_label_map[f])
			pbar.update(curCount)
			curCount+=1
	
	pbar.finish()
	m, p_acc, p_vals = svm_predict(labels, vectors, m1, '-b 1')
	
	print m
	return [m,p_acc,p_vals]


def Testing_multi(directory,fs):
	happy_model = svm_load_model('libsvm_SVC_stem_emoticons_Happy.model')
	sad_model = svm_load_model('libsvm_SVC_stem_emoticons_Sad.model')
	ashamed_model = svm_load_model('libsvm_SVC_stem_emoticons_Ashamed.model')
	angry_model = svm_load_model('libsvm_SVC_stem_emoticons_Angry.model')
	afraid_model = svm_load_model('libsvm_SVC_stem_emoticons_Afraid.model')
	
	
	
	
	
	vectors = []
	labels_happy = []
	labels_sad = []
	labels_ashamed = []
	labels_angry = []
	labels_afraid = []
	
	lines = []
	err_lines=[]
	
	labels = []
	count = 0
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		count+=len(of.readlines())
	widgets = ['Test_Vectorize: ', Percentage(), ' ', Bar(marker='0',left='[',right=']'),
			        ' ', ETA(), ' ', FileTransferSpeed()]
	pbar = ProgressBar(widgets=widgets, maxval=count)
	pbar.start()
	
	curCount=0
	for f in os.listdir(directory):
		of = open(directory+'/'+f,'r')
		for line_num, line in enumerate(of.readlines()):
			lines.append(line)
			vector = vectorize(feature_space,line)
			#print vector
			vectors.append(vector)
			
			if f == 'Test_Happy.txt':
				labels_happy.append(1)
				labels_sad.append(0)
				labels_ashamed.append(0)
				labels_angry.append(0)
				labels_afraid.append(0)
			elif f== 'Test_Angry.txt':
				labels_happy.append(0)
				labels_sad.append(0)
				labels_ashamed.append(0)
				labels_angry.append(1)
				labels_afraid.append(0)
			elif f== 'Test_Sad.txt':
				labels_happy.append(0)
				labels_sad.append(1)
				labels_ashamed.append(0)
				labels_angry.append(0)
				labels_afraid.append(0)	
			elif f== 'Test_Ashamed.txt':
				labels_happy.append(0)
				labels_sad.append(0)
				labels_ashamed.append(1)
				labels_angry.append(0)
				labels_afraid.append(0)
			elif f== 'Test_Afraid.txt':
				labels_happy.append(0)
				labels_sad.append(0)
				labels_ashamed.append(0)
				labels_angry.append(0)
				labels_afraid.append(1)
			else:
				print 'error'
				print f
				break
			labels.append(test_label_map[f])
		#print test_label_map[f]
			
			#labels.append(test_label_map[f])
			pbar.update(curCount)
			curCount+=1
	
	pbar.finish()
	
	m_happy, p_acc, p_happy = svm_predict(labels_happy, vectors, happy_model, '-b 1')
	m_sad, p_acc, p_sad = svm_predict(labels_sad, vectors, sad_model, '-b 1')
	m_angry, p_acc, p_angry = svm_predict(labels_angry, vectors, angry_model, '-b 1')
	m_ashamed, p_acc, p_ashamed = svm_predict(labels_ashamed, vectors, ashamed_model, '-b 1')
	m_afraid, p_acc, p_afraid = svm_predict(labels_afraid, vectors, afraid_model, '-b 1')
		
		
	correctCount = 0.0
	resultLabel = []
		
	err_f = open('err_file.txt','w+')
	print len(p_happy)
		
	for i in range(0,len(p_happy)):
		tempZ = []
		tempZ.append(p_angry[i][1])
		tempZ.append(p_happy[i][1])
		tempZ.append(p_sad[i][1])	
		tempZ.append(p_ashamed[i][1])
		tempZ.append(p_afraid[i][0])
			
		mZ = max(tempZ)
		c = [m for m, j in enumerate(tempZ) if j == mZ]
		resultLabel.append(c[0])
		if c[0] == labels[i]:
			correctCount+=1
		else:
			err_f.write(lines[i]+'	')
			err_f.write(str(labels[i])+'	')
			err_f.write(str(c[0])+'		')
			err_f.write(str(p_angry[i][1])+'	')
			err_f.write(str(tempZ[1])+'		')
			err_f.write(str(tempZ[2])+'		')
			err_f.write(str(tempZ[3])+'		')
			err_f.write(str(tempZ[4])+'		')
			err_f.write('\n')
		
		
		
	err_f.close()	
	print correctCount
	print 'Accuracy ', correctCount/len(labels)
	
	


sentences = load_collection_sentence(Training_Path)
feature_space = create_feature_space(sentences)
Testing_multi(Testing_Path,feature_space)


#[m, fs] = Training(Training_Path)
#[m,p_acc,p_vals]=Testing(Testing_Path,m,fs)

#print p_vals
#print p_vals

# vector = vectorize(fs," I hate when people have candy in their mouth and they are moving it around and you can hear that nasty spit noise. #[someTAG] #[someTAG]")
# label = [0]
# vectors = []
# vectors.append(vector)	
# svm_predict(label, vectors, m)	
	
	
