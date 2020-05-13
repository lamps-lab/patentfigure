#!/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup

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
	text = text.replace(".",".<stop>")
	text = text.replace("?","?<stop>")
	text = text.replace("!","!<stop>")
	text = text.replace("<prd>",".")
	text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
	sentences = text.split("<stop>")
	sentences = sentences[:-1]
	sentences = [s.strip() for s in sentences]
	return sentences

c=0
listFile=open("xmlFiles.txt", "r")
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
		try:
			fig=titles[title].figref.get_text()
		except:
			continue
		print("{\"index\":{\"_id\":\"%s\"}}\n{\"patentID\":\"%s\",\"pid\":\"%s\",\"figid\":\"%s\",\"caption\":true,\"description\":\"%s\"}"%(c,doc,id,fig,text))
		c+=1
		if title in titles2:
			titles2.remove(title)
	for title in range(0, len(titles3)):
		id=titles3[title]['id']
		num=titles3[title]['num']
		text=titles3[title].get_text()
		if text.find("FIG.") != -1:
			figs=titles3[title].find_all('figref')
			for x in range(0, len(figs)):
				fig=figs[x].get_text()
				#print("Text: ", text)
				output=split_into_sentences(text)
				for x in range(0, len(output)):
					if output[x].find("FIG."):
						#print("Sentences: ", output)
						print("{\"index\":{\"_id\":\"%s\"}}\n{\"patentID\":\"%s\",\"pid\":\"%s\",\"figid\":\"%s\",\"caption\":false,\"description\":\"%s\"}"%(c,doc,id,fig,output[x]))
						c+=1
