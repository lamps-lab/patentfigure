xmlExtract.py - uses stanford coreNLP to segment sentences; contains code for both sql and json output
sentLib.py - Professor Wu's custom sentence segmentation tool
xmlExtract2.py - uses Professor Wu's sentence segmenter to segment sentences; output goes to a json file
test.txt - contains the path to the xml file that caused problems in xmlExtract.py
testCases.txt - contains non normal figure ids for testing purposes


xmlExtract12w.py - convert XML files into database of figure descriptions. This version includes "object" and "aspect" in the database.
                 - line 474 is used for the input file to indicate the path of the xml files
