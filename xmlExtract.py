#!/opt/anaconda3/bin/python
#import mysql.connector
from bs4 import BeautifulSoup
from nltk.parse.corenlp import CoreNLPParser

stanford = CoreNLPParser('http://localhost:9000')
#mydb=mysql.connector.connect(
	#host="hawking.cs.odu.edu",
	#user="mgryder",
	#passwd="TueJan7202011:46",
	#database="uspto_2001_2020_figs",
	#auth_plugin="mysql_native_password"
#)

#mycursor=mydb.cursor()

#mycursor.execute("CREATE TABLE USPTOFigs (id INT PRIMARY KEY AUTO_INCREMENT, patentID VARCHAR(255), pid VARCHAR(255), figid VARCHAR(255), caption ENUM('0', '1'), description VARCHAR(10000))")

listFile=open("test.txt", "r")
for x in listFile:
	print("File: ", x)
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
	#print(doc)
	for title in range(0, len(titles)):
		id=titles[title]['id']
		num=titles[title]['num']
		text=titles[title].get_text()
		try:
			fig=titles[title].figref.get_text()
		except:
			continue
		#print(fig)
		sql = "INSERT INTO USPTOFigs (patentID, pid, figid, caption, description) VALUES (%s, %s, %s, %s, %s)"
		val = (doc, id, fig, "1", text)
		#mycursor.execute(sql, val)
		if title in titles2:
			titles2.remove(title)
			#print(id, num, text)
	for title in range(0, len(titles3)):
		id=titles3[title]['id']
		num=titles3[title]['num']
		text=titles3[title].get_text()
		if text.find("FIG.") != -1:
			#fig=titles3[title].figref.get_text()
			#print(fig)
			figs=titles3[title].find_all('figref')
			for x in range(0, len(figs)):
				fig=figs[x].get_text()
				print("Text: ", text)
				' '.join(next(stanford.raw_parse(text)).leaves())
				next(stanford.raw_parse(text))
				stanford.api_call
				stanford.api_call(text, properties={'annotators': 'tokenize,ssplit'})
				output_json = stanford.api_call(text, properties={'annotators': 'tokenize,ssplit'})
				for sent in output_json['sentences']:
					#print(sent)
					start_offset = sent['tokens'][0]['characterOffsetBegin']
					end_offset = sent['tokens'][-1]['characterOffsetEnd']
					sent_str = text[start_offset:end_offset]
					#print(sent_str)
				#sql = "INSERT INTO USPTOFigs (patentID, pid, figid, caption, description) VALUES (%s, %s, %s, %s, %s)"
				#val = (doc, id, fig, "0", text)
              		 		#mycursor.execute(sql, val)
                			#print(id, num, text)
			#mydb.commit()
	#print(mycursor.rowcount, "record inserted.")
	infile.close()
listFile.close()
