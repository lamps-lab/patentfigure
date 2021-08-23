# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 01:14:10 2021

@author: weixi
"""


#For 2019design dataset, a small pilot dataset
#use flair (BiLSTM-CRF) NER to extract aspect and object
 

#!/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
import mysql.connector
import re
#import stanza
import os

from flair.data import Sentence
from flair.training_utils import EvaluationMetric
from flair.data import Corpus
from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings, FlairEmbeddings, TransformerWordEmbeddings
from typing import List
from flair.models import SequenceTagger


# load the model you trained
model = SequenceTagger.load('resources/taggers/example-ner/final-model.pt')



#nlp = stanza.Pipeline('en')


mydb=mysql.connector.connect(
	host='hawking.cs.odu.edu',
	user='xwei',
	passwd='ThuMay74:57',
	database='uspto_2001_2020_figs',
	auth_plugin='mysql_native_password'
)

mycursor=mydb.cursor()




mycursor.execute("CREATE TABLE usptofigs2019design_xwei (id INT PRIMARY KEY AUTO_INCREMENT, patentID VARCHAR(255), pid VARCHAR(255), is_multiple ENUM('0', '1'), origreftext VARCHAR(255), figid VARCHAR(255), subfig VARCHAR(32), is_caption ENUM('0', '1'), description VARCHAR(10000), aspect VARCHAR(1000), object VARCHAR(1000))")

 
alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|me|edu)"
digits = "([0-9])"

def split_into_sentences(text):
	text = " " + text + "  "
	text = text.replace("\n"," ")
	text = re.sub(prefixes,"\\1<prd>",text)
	text = re.sub(websites,"<prd>\\1",text)
	if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
	text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
	text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
	text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
	text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
	text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
	text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
	text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
	if "”" in text: text = text.replace(".”","”.")
	if "\"" in text: text = text.replace(".\"","\".")
	if "!" in text: text = text.replace("!\"","\"!")
	if "?" in text: text = text.replace("?\"","\"?")
	if "e.g." in text: text = text.replace("e.g.","e<prd>g<prd>")
	if "i.e." in text: text = text.replace("i.e.","i<prd>e<prd>")
	if "..." in text: text = text.replace("...","<prd><prd><prd>")
	if "FIG." in text: text = text.replace("FIG.","FIG<prd>") 
	if "FIGS." in text: text = text.replace("FIGS.","FIGS<prd>")    
	text = text.replace(".",".<stop>")
	text = text.replace("?","?<stop>")
	text = text.replace("!","!<stop>")
	text = text.replace("<prd>",".")
	text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
	sentences = text.split("<stop>")
	sentences = sentences[:-1]
	sentences = [s.strip() for s in sentences]
	return sentences








def insertrow1(doc1, id1, multiple1, fig1, figid1, subfig1, text1, aspect, objectt) :
	sql = "INSERT INTO usptofigs14_xwei (patentID, pid, is_multiple, origreftext, figid, subfig, is_caption, description, aspect, object) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	val = (doc1, id1, multiple1, fig1, figid1, subfig1, "1", text1, aspect, objectt)
	mycursor.execute(sql, val)
	mydb.commit()
	print(mycursor.rowcount, "record inserted.")
    
def insertrow0(doc1, id1, multiple1, fig1, figid1, subfig1, text1, aspect, objectt) :
	sql = "INSERT INTO usptofigs14_xwei (patentID, pid, is_multiple, origreftext, figid, subfig, is_caption, description, aspect, object) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	val = (doc1, id1, multiple1, fig1, figid1, subfig1, "0", text1, aspect, objectt)
	mycursor.execute(sql, val)
	mydb.commit()
	print(mycursor.rowcount, "record inserted.")


def insertand(figvalue) :   #local5 version modified this
	
	print(fig)
	prfig = re.sub(r'[and]{1}',' ',fig) #remove and 
	prfig = re.sub(r'[,]{1}',' ',prfig)   #remove comma
	prefig = prfig.split()
	del prefig[0]
	print(prefig)
	#figids = re.findall(r'\d+',prfig)   #find numbers  ['14', '14']
	#print(figids) 
	#subfigs = re.findall(r'\D+',prfig)  #find other things ['FIGS. ', 'A     ', 'B']
	#del subfigs[0] #['A     ', 'B']
	#print(subfigs)
	multi = "1"  
	for i in range(0, len(prefig)):
		figid = re.findall(r'\d+',prefig[i])
		subfig = re.findall(r'[A-Za-z]+',prefig[i])
		figid = "".join(figid)  #convert list to string
		subfig = "".join(subfig)   #convert list to string
		print(figid)
		print(subfig)
		insertrow1(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=text, aspect=aspect, objectt=objectt)
		#print("c:", c)

def insertdash(figvalue):
	 
	prfig = re.sub(r'[-|to]{1}',' ',fig)   #FIGS. 1 6
	print(prfig)
	prfig = prfig.split( )   #['FIGS.', '1', '6']
	del prfig[0]  #['1', '6']
	print(prfig)
	a = prfig[0]
	a = int(a)
	b = prfig[len(prfig)-1]
	b = int(b)
	figid = a
	subfig = None
	multi = "1"
	for i in range(0, b-a+1):
		insertrow1(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=text, aspect=aspect, objectt=objectt)
		figid +=1
            
def insertand0(figvalue, textfinalvalue) :
	 
	print(fig)
	prfig = re.sub(r'[and]{1}',' ',fig) #remove and 
	prfig = re.sub(r'[,]{1}',' ',prfig)   #remove comma
	prefig = prfig.split()
		
	del prefig[0]
	print(prefig)
	multi = "1"
	for i in range(0, len(prefig)):
		figid = re.findall(r'\d+',prefig[i])    #list
		subfig = re.findall(r'[A-Za-z]+',prefig[i])  # list
		figid = "".join(figid)  #convert list to string
		subfig = "".join(subfig)   #convert list to string
		print(figid)
		print(subfig)
		insertrow0(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=textfinal, aspect=aspect, objectt=objectt)

def insertdash0(figvalue, textfinalvalue):
	
	prfig = re.sub(r'[-|to]{1}',' ',fig)   #FIGS. 1 6
	#prfig = re.sub(r'[to]{1}',' ',fig)
	print(prfig)
	prfig = prfig.split( )   #['FIGS.', '1', '6']
	del prfig[0]  #['1', '6']
	print(prfig)
	a = prfig[0]
	a = int(a)
	b = prfig[len(prfig)-1]
	b = int(b)
	figid = a
	subfig = None
	multi = "1"
	for i in range(0, b-a+1):
		insertrow0(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=textfinal, aspect=aspect, objectt=objectt)
		figid +=1

def insertmix1(figvalue):
	prfig = re.sub(r'[-|to]{1}',' ',fig)   #FIGS. 1 6    #FIGS. 1A 1D
	print(prfig)
	prfig = prfig.split( )   #['FIGS.', '1', '6']
	del prfig[0]  #['1', '6']
	print("/", prfig)    
    
	figid1 = re.findall(r'\d+',prfig[0])    #list
	figid1 = int("".join(figid1)) #list---string----integer
	print(figid1)
	figid2 = re.findall(r'\d+',prfig[1])    #list
	figid2 = int("".join(figid2))
	print(figid2)    
	subfig1 = re.findall(r'[A-Za-z]+',prfig[0])  # list
	subfig1 = "".join(subfig1)
	print(subfig1)
	subfig2 = re.findall(r'[A-Za-z]+',prfig[1])  # list
	subfig2 = "".join(subfig2)
	print(subfig2)
	if figid1 ==figid2:
		figid = figid1
		multi = "1"     
		a = ord(subfig1)
		b = ord(subfig2)
		print(a)
		print(b)
		#a = relate(subfig[0])
		#b = relate(subfig[1])
		for i in range(0, b-a+1):
			subfig = chr(a)
			print(subfig)
			insertrow1(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=text, aspect=aspect, objectt=objectt)
			a +=1
	else:    
		insertrow1(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=text, aspect=aspect, objectt=objectt)   
    
def insertmix0(figvalue, textfinalvalue):
	prfig = re.sub(r'[-|to]{1}',' ',fig)   #FIGS. 1 6
	print(prfig)
	prfig = prfig.split( )   #['FIGS.', '1', '6']
	del prfig[0]  #['1', '6']
	print("/", prfig)    
    
	figid1 = re.findall(r'\d+',prfig[0])    #list
	figid1 = int("".join(figid1)) #list---string----integer
	print(figid1)
	figid2 = re.findall(r'\d+',prfig[1])    #list
	figid2 = int("".join(figid2))
	print(figid2)    
	subfig1 = re.findall(r'[A-Za-z]+',prfig[0])  # list
	subfig1 = "".join(subfig1)
	print(subfig1)
	subfig2 = re.findall(r'[A-Za-z]+',prfig[1])  # list
	subfig2 = "".join(subfig2)
	print(subfig2)
	if figid1 ==figid2:
		figid = figid1
		multi = "1"     
		a = ord(subfig1)
		b = ord(subfig2)
		print(a)
		print(b)
		#a = relate(subfig[0])
		#b = relate(subfig[1])
		for i in range(0, b-a+1):
			subfig = chr(a)
			print(subfig)
			insertrow0(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=textfinal, aspect=aspect, objectt=objectt)
			a +=1
	else:    
		insertrow0(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=textfinal, aspect=aspect, objectt=objectt)   


def insertmixless1(figvalue):
	prfig = re.sub(r'[-|to]{1}',' ',fig)   #FIGS. 1 6
	print(prfig)
	prfig = prfig.split( )   #['FIGS.', '1', '6']
	del prfig[0]  #['1', '6']
	print("/", prfig)    
    
	figid = re.findall(r'\d+',prfig[0])    #list
	figid = int("".join(figid)) #list--->string---->integer
	print(figid)
	subfig1 = re.findall(r'[A-Za-z]+',prfig[0])  # list
	subfig1 = "".join(subfig1)
	print(subfig1)
	subfig2 = re.findall(r'[A-Za-z]+',prfig[1])  # list
	subfig2 = "".join(subfig2)    #list--->string
	print(subfig2)		
	multi = "1"   
    
	a = ord(subfig1)
	b = ord(subfig2)
	print(a)
	print(b)
	for i in range(0, b-a+1):
		subfig = chr(a)
		print(subfig)
		insertrow1(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=text, aspect=aspect, objectt=objectt)
		a +=1    

def insertmixless0(figvalue, textfinalvalue):
	prfig = re.sub(r'[-|to]{1}',' ',fig)   #FIGS. 1A C
	print(prfig)
	prfig = prfig.split( )   #['FIGS.', '1A', 'C']
	del prfig[0]  #['1A', 'C']
	print("/", prfig)    
    
	figid = re.findall(r'\d+',prfig[0])    #list
	figid = int("".join(figid)) #list--->string---->integer
	print(figid)
	subfig1 = re.findall(r'[A-Za-z]+',prfig[0])  # list
	subfig1 = "".join(subfig1)
	print(subfig1)
	subfig2 = re.findall(r'[A-Za-z]+',prfig[1])  # list
	subfig2 = "".join(subfig2)    #list--->string
	print(subfig2)		
	multi = "1"   
    
	a = ord(subfig1)
	b = ord(subfig2)
	print(a)
	print(b)
	for i in range(0, b-a+1):
		subfig = chr(a)
		print(subfig)
		insertrow0(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1= figid, subfig1=subfig, text1=textfinal, aspect=aspect, objectt=objectt)
		a +=1
	


def insertsingle1(figvalue):
	multi = "0"
	prfig = fig.split( )
	print(prfig)
	del prfig[0]   #['1A']
	prfig = "".join(prfig)      # convert list into a string
	figid = re.findall(r'\d+',prfig)    #gives a list
	print(figid)
	subfig = re.findall(r'[A-Za-z]+',prfig)  # gives a list 
	print(subfig)
	figid = "".join(figid)  #convert list to string
	subfig = "".join(subfig)   #convert list to string
	insertrow1(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1=figid, subfig1=subfig, text1=text, aspect=aspect, objectt=objectt)# figid, subfig are lists
    
def insertsingle0(figvalue, textfinalvalue):
	multi = "0"
	prfig = fig.split( )
	del prfig[0]   #['1A']
	prfig = "".join(prfig)     # convert list into a string
	print(prfig)
	figid = re.findall(r'\d+',prfig)    #list
	print(figid)    
	subfig = re.findall(r'[A-Za-z]+',prfig)  # list 
	print(subfig)    
	figid = "".join(figid)  #convert list to string
	print(figid)
	subfig = "".join(subfig)   #convert list to string
	print(subfig)
	insertrow0(doc1=doc, id1=id, multiple1=multi, fig1=fig, figid1=figid, subfig1=subfig, text1=textfinal, aspect=aspect, objectt=objectt)
      
def write_text(figvalue):	
	fileObject.write(fig)  
	fileObject.write('\n')       
    
    
    
d=0   
f=0          
c=0
counter1=0
counter2=0
fileObject = open("counter1.txt",'w')   #in the same directory of the python file
listFile=open("xmlfilesdesign.txt", "r")
for x in listFile:    
	infile=open(x.strip(), "r")
	contents=infile.read()
	soup=BeautifulSoup(contents, 'xml')
	try:
		titles=soup.find('description-of-drawings').find_all('p')
	except:
		continue
	try:
		titles2=soup.find('description').find_all('p')
	except:
		continue
	titles3 = [i for i in titles2 if i not in titles]
	doc="US"+soup.find('doc-number').get_text()+"-"+soup.find('date').get_text()
	for title in range(0, len(titles)):
		id=titles[title]['id']
		num=titles[title]['num']
		text=titles[title].get_text()
        
        
        
		# create example sentence
		sentence = Sentence(text)
    
		# predict tags and print
		model.predict(sentence)
    
		output = sentence.to_tagged_string()         #FIG . 1 is a front <B-ASPECT> perspective <I-ASPECT> view <I-ASPECT> of the set <B-OBJECT> of <I-OBJECT> bowls <I-OBJECT> showing my new design ;
		aspect = '0'
		objectt = '0'
		for string1 in sentence.get_spans('ner'):    #Span [6,7,8]: "front perspective view"   [− Labels: ASPECT (0.9998)]  #Span [11,12,13]: "set of bowls"   [− Labels: OBJECT (0.9639)]
                                                            
						
			print('==')
			strint1_split = string1.split('   ')

			label1 = strint1_split[1].split(': ')  #['[− Labels', 'ASPECT (0.9998)]']
			label = label1[1].split(' (')[0]     #ASPECT

			entity = strint1_split[0].split(': ')[1]   #"front perspective view"
			entity = entity.split('"')    #['', 'front perspective view', '']
			entity = entity[1]          #front perspective view

			if label == "ASPECT":
				aspect = entity
			elif label == "OBJECT":
				objectt = entity        
        
        
        
		try:
			fig=titles[title].figref.get_text()
		except:
			continue
		#print("{\"index\":{\"_id\":\"%s\"}}\n{\"patentID\":\"%s\",\"pid\":\"%s\",\"figid\":\"%s\",\"caption\":true,\"description\":\"%s\"}"%(c,doc,id,fig,text))
		if fig.find("FIGS.") == -1:
			d+=1
		elif fig.find("FIGS.") != -1:
			f+=1
        
		c+=1
		try:
			if "and" in fig:
				insertand(figvalue=fig)
			#elif bool(re.search(r'[0-9]{1,2}[A-Za-z][ ][t][o][ ][0-9]{1,2}[A-Za-z]',fig)) == True:   
			#	insertmix1(figvalue=fig) 
			#elif bool(re.search(r'[0-9]{1,2}[A-Za-z][-][0-9]{1,2}[A-Za-z]',fig)) == True:   
			#	insertmix1(figvalue=fig)      
			elif bool(re.search(r'[0-9]{1,3}[A-Za-z][ ][t][o][ ][0-9]{1,3}[A-Za-z]',fig)) == True or bool(re.search(r'[0-9]{1,3}\([A-Za-z]\)[ ][t][o][ ][0-9]{1,3}\([A-Za-z]\)',fig)) == True:   
				insertmix1(figvalue=fig) 
			elif bool(re.search(r'[0-9]{1,3}[A-Za-z][-][0-9]{1,3}[A-Za-z]',fig)) == True or bool(re.search(r'[0-9]{1,3}\([A-Za-z]\)[-][0-9]{1,3}\([A-Za-z]\)',fig)) == True:   
				insertmix1(figvalue=fig) 
			elif bool(re.search(r'[0-9]{1,2}[A-Za-z][-][A-Za-z]',fig)) == True: 
				insertmixless1(figvalue=fig)           						
			elif "-" in fig or "to" in fig: 
				insertdash(figvalue=fig)
			else:
				insertsingle1(figvalue=fig)
			#print(fig,c)
            
		except:
			counter1=counter1+1
			write_text(figvalue=fig)
			print("counter1:", counter1)
			continue 
        
		if title in titles2:
			titles2.remove(title)
	for title in range(0, len(titles3)):
		fig = 0
		id=titles3[title]['id']
		num=titles3[title]['num']
		text=titles3[title].get_text()
		if text.find("FIG.") != -1 or text.find("FIGS.") != -1:
			figs=titles3[title].find_all('figref')
			output=split_into_sentences(text)
			
			n = -1
			for y in range(0, len(output)):
				n += 1
				if output[n].find("FIG.") == -1 and output[n].find("FIGS.") == -1:
					del output[n]
					n -= 1                 
                
			print("%d, %d" %(len(output), len(figs)))
            
			for z in range(0, len(output)):
				#fig = figs[z].get_text()
				#textfinal = output[z]
				#print("%s" %(output[z]), fig)
				
				#print("{\"index\":{\"_id\":\"%s\"}}\n{\"patentID\":\"%s\",\"pid\":\"%s\",\"figid\":\"%s\",\"caption\":false,\"description\":\"%s\"}"%(c,doc,id,fig,output[z]))
				
				try:
					fig = figs[z].get_text()
					textfinal = output[z]
                    
					
                    
                    
                    
                    # create example sentence
					sentence = Sentence(textfinal)
    
					# predict tags and print
					model.predict(sentence)
    
					output = sentence.to_tagged_string()         #FIG . 1 is a front <B-ASPECT> perspective <I-ASPECT> view <I-ASPECT> of the set <B-OBJECT> of <I-OBJECT> bowls <I-OBJECT> showing my new design ;
					aspect = '0'
					objectt = '0'
					for string1 in sentence.get_spans('ner'):    #Span [6,7,8]: "front perspective view"   [− Labels: ASPECT (0.9998)]  #Span [11,12,13]: "set of bowls"   [− Labels: OBJECT (0.9639)]                                 
						print('==')
						strint1_split = string1.split('   ')
						label1 = strint1_split[1].split(': ')  #['[− Labels', 'ASPECT (0.9998)]']
						label = label1[1].split(' (')[0]     #ASPECT
						entity = strint1_split[0].split(': ')[1]   #"front perspective view"
						entity = entity.split('"')    #['', 'front perspective view', '']
						entity = entity[1]          #front perspective view
						if label == "ASPECT":
							aspect = entity
						elif label == "OBJECT":
							objectt = entity
                    
                    
					#print("{\"index\":{\"_id\":\"%s\"}}\n{\"patentID\":\"%s\",\"pid\":\"%s\",\"figid\":\"%s\",\"caption\":false,\"description\":\"%s\"}"%(c,doc,id,fig,output[z]))
					c+=1
					if fig.find("FIGS.") == -1:
						d+=1
					elif fig.find("FIGS.") != -1:
						f+=1
				except:
					counter2=counter2+1
					print("counter2:", counter2)
					continue
				        
                
				try:						
					if "and" in fig:
						insertand0(figvalue=fig, textfinalvalue=textfinal)
					elif bool(re.search(r'[0-9]{1,3}[A-Za-z][ ][t][o][ ][0-9]{1,3}[A-Za-z]',fig)) == True or bool(re.search(r'[0-9]{1,2}\([A-Za-z]\)[ ][t][o][ ][0-9]{1,2}\([A-Za-z]\)',fig)) == True:
						insertmix0(figvalue=fig, textfinalvalue=textfinal) 
					elif bool(re.search(r'[0-9]{1,3}[A-Za-z][-][0-9]{1,3}[A-Za-z]',fig)) == True or bool(re.search(r'[0-9]{1,3}\([A-Za-z]\)[-][0-9]{1,3}\([A-Za-z]\)',fig)) == True:   
						print("you")
						insertmix0(figvalue=fig, textfinalvalue=textfinal)
					elif bool(re.search(r'[0-9]{1,2}[A-Za-z][-][A-Za-z]',fig)) == True: 
						insertmixless0(figvalue=fig, textfinalvalue=textfinal)                        
					elif "-" in fig or "to" in fig: 
						insertdash0(figvalue=fig, textfinalvalue=textfinal)
					else:
						insertsingle0(figvalue=fig, textfinalvalue=textfinal)						
						#print(c)
				except:
					counter1=counter1+1
					write_text(figvalue=fig)
					print("counter1:", counter1)
					continue 
						
                        
	infile.close()
listFile.close()
fileObject.close()
print("d:", d)
print("f:", f)
print("counter1:", counter1)
print("counter2:", counter2)