import numpy as np
import pandas as pd
import Queue
#import matplotlib.pyplot as plt 
from sklearn.metrics import confusion_matrix 
from sklearn.model_selection import train_test_split 
from sklearn.tree import DecisionTreeClassifier 
from sklearn.metrics import accuracy_score 
from sklearn.metrics import classification_report 
from sklearn.preprocessing import OneHotEncoder
from sklearn import tree
#import graphviz

#import sklearn
def plot(model,class_names,feature_names):
	dot_data = tree.export_graphviz(model, out_file='tree.dot', filled=True, rounded=True,
                                feature_names=feature_names,  
                                class_names=class_names)
	graph = graphviz.Source(dot_data)  
	graph
	# Convert to png
	from subprocess import call
	call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])

	# Display in python
	plt.figure(figsize = (14, 18))
	plt.imshow(plt.imread('tree.png'))
	plt.axis('off');
	plt.show();

def splitdataset(df): 
  	
  	X = df.values[:, 0:4] 
	Y = df.values[:, 4]
	#print(list(X))
	#print(list(Y))
	  
	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size = 0.3, random_state = 100)       
	return X, Y, X_train, X_test, y_train, y_test 

def cal_accuracy(y_test, y_pred):   
	print("Confusion Matrix: ", 
	confusion_matrix(y_test, y_pred))       
	print ("Accuracy : ", 
	accuracy_score(y_test,y_pred)*100)       
	#print("Report : ", 
	#classification_report(y_test, y_pred)) 
	
    
def libdtree(X_train, X_test, y_train):
	model = DecisionTreeClassifier( 
            criterion = "entropy", random_state = 100, 
            max_depth = 5, min_samples_leaf = 1) 
	model.fit(X_train, y_train) 
	y_pred = model.predict(X_test) 	
	return y_pred,model

def entropy(s):
	res = 0
	val, counts = np.unique(s, return_counts=True)
	freqs = counts.astype('float')/len(s)
	for p in freqs:
		if p != 0.0:
			res -= p * np.log2(p)
	return res

def dtree(df,columns,level,resultOf=None):
	print df
	print "Columns :"+str(columns)
	val,count= np.unique(df['Buys'].values,return_counts=True)
	
	if(len(val)==1):
		print "Region_DF is "+str(val[0])
		return decisionnode(name="Decision",value=val[0],leaf=True,level=level,resultOf=resultOf)
		
	if len(columns)==0:
		label=val[count.index(max(count))]
		return decisionnode(name="Decision",value=label,leaf=True,level=level,resultOf=resultOf)
		
	if(len(df)==0):
		print 'Termination Criteria'
		return
		
	baseGain=entropy(df['Buys'].values)
	infodict={}
	#print columns
	for cname in columns:
		#print "For column :"+cname
		e=0
		for region, df_region in df.groupby(cname):
			#print(df_region)
			e+=(float(len(df_region))/len(df))*entropy(df_region['Buys'].values)
		infodict[cname]=e	
	
	print infodict
	for key in infodict:
		infodict[key]=baseGain-infodict[key]
	print infodict	
	target_column = max(infodict,key=infodict.get)
	columns.remove(target_column)
		
	print 'Target :'+target_column
	branches=[]
	for region, df_region in df.groupby(target_column):
		branches.append(dtree(df_region,columns,level+1,{target_column:region}))
	return decisionnode(name=target_column,branches=branches,level=level,resultOf=resultOf)	

class decisionnode:
	L = Queue.Queue(maxsize=0) 
	
	def __init__(self,name,level,value=None,branches=None,leaf=False,resultOf=None):
		self.name=name
		self.branches=branches
		self.leaf=leaf
		self.value=value
		self.level=level
		self.resultOf=resultOf
	
	def parseTree(self):
		decisionnode.L.put(self)
		current=None
		while (not(decisionnode.L.empty())):
			current=decisionnode.L.get()
			
			print 'Name: '+ current.name + "|ResultOf:"+str(current.resultOf)+" |At Level: "+str(current.level)+" |Value: " + str(current.value) 
			
			for b in (current.branches or []):
				#print b
				decisionnode.L.put(b)
				
			
def main():
	print("Decision Tree\n")
	df = pd.read_csv("data.csv",index_col='ID') 		
	columns=list(df)
	#print(df)
	df[:] = df[:].astype('category')
	#df.info()
	#df['Buys'],class_names = pd.factorize(df['Buys'])
	invert=[]
	for column in df:
		df[column],class_names=pd.factorize(df[column])
	
	#print class_names
	
	X, Y, X_train, X_test, y_train, y_test = splitdataset(df) 	
	y_pred,model = libdtree(X_train, X_test, y_train)
	#cal_accuracy(y_test,y_pred)
	feature_names = columns[0:4]
	#plot(model,class_names,feature_names)
	#print df
	#print entropy(df['Buys'].values)
	
	columns.remove('Buys')
	tree=dtree(df,columns,0)
	tree.parseTree()
	
	
if __name__=="__main__": 
    main()
    
