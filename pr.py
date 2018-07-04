import sys
import argparse
import re
 

def outputJ(other):
	str=''
	if namespace.choice=='je':
		volRegExp='Vol\. \d+'
		issueRegExp='No. \d+'
	elif namespace.choice=='jr':
		volRegExp='[TТ]\. \d+'
		issueRegExp='№ \d+'
	elif namespace.choice=='jres' or namespace.choice=='jees':
		volRegExp='vol\. \d+'
		issueRegExp='no. \d+'
		
	yr=re.findall('\. (\d+)\.', other)
	vol=re.findall(volRegExp, other)
	issue=re.findall(issueRegExp, other)
	pages=re.findall('(\d+)[–-](\d+)', other)
	
	indexVol=5
	indexIssue=4
	if namespace.choice=='jr':
		indexVol=3
		indexIssue=2
	
	if yr:
		str+='\\yr '+yr[0]+'\n'
	if vol:
		str+='\\vol '+vol[0][indexVol:]+'\n'
	if issue:
		str+='\\issue '+issue[0][indexIssue:]+'\n'
	if pages:
		str+='\\pages '+pages[0][0]+'--'+pages[0][1]+'\n'
		
	doi=re.search('DOI:', other)
	doiEnd=re.search(' [(]', other)
	if doi:
		doi=doi.start()
		if doiEnd:
			doiEnd=doiEnd.start()
			str+='\\crossref{http://dx.doi.org/'+other[doi+5:doiEnd]+'}\n'
		else:
			str+='\\crossref{http://dx.doi.org/'+other[doi+5:-1]+'}\n'
		
	return str

def outputB(other):
	str=''
	if namespace.choice=='br':
		pagesRegExp='(\d+) [cс]'
	else:
		pagesRegExp='(\d+) [рp]'

	yr=re.findall(', (\d+)\.', res[1])
	pages=re.findall(pagesRegExp, res[1])

	if yr:
		str+='\\yr '+yr[0]+'\n'
	if pages:
		str+='\\totalpages '+pages[0]+'\n'
	return str
	
def outputC(other):
	str=''
	pagesRegExp='pp. (\d+)[–-](\d+)'
	if namespace.choice=='ce':
		pagesRegExp='P. (\d+)[–-](\d+)'
	yr=re.findall(', (\d+), pp|, (\d+)\.', res[1])
	pages=re.findall(pagesRegExp, other)

	if yr:
		if yr[0][0]:
			str+='\\yr '+yr[0][0]+'\n'
		if yr[0][1]:
			str+='\\yr '+yr[0][1]+'\n'
	if pages:
		str+='\\pages '+pages[0][0]+'--'+pages[0][1]+'\n'
		
	doi=re.search('DOI:', other)
	if doi:
		doi=doi.start()
		str+='\\crossref{http://dx.doi.org/'+other[doi+5:-1]+'}\n'
	return str
	
	
def getAuthor(line):
	add=''
	if re.search('и др. ', line):
		line=line.replace('и др.','')
		add+=' и др.'
	if re.search('et al.', line):
		line=line.replace(', et al.','')
		add+=', et al.'
	res = re.split('\. ', line, maxsplit=1)
	
	by = res[0]
	resby=re.split(', ', by)
	amountOfAuthors=len(resby)
	name=''
	for author in resby:
		resby2=re.split(' ', author)
		initials=re.findall('\w',resby2[1])
		if len(initials)==1:
			if name!='':
				name+=', '
			name+=initials[0]+'.~'+resby2[0]
		else:
			if name!='':
				name+=', '
			name+=initials[0]+'.\,'+initials[1]+'~'+resby2[0]
	str='\\by '+name+add+'\n'
	return str
	
def createParser ():
	parser = argparse.ArgumentParser()
	parser.add_argument ('choice')
	parser.add_argument ('name')
	return parser
 
parser = createParser()
namespace = parser.parse_args()

f = open(namespace.name+'.txt')
fout=open('out.txt','w')

for line in f:
			
	if namespace.choice[0]!='e':
		res = re.split('\. ', line, maxsplit=1)
		str=getAuthor(line)

	
	if namespace.choice=='jres':
		paper=re.split('\.', res[1])[0]
		str+='\\paper '+paper+'\n'
		
		joirStart=re.search('[[]',res[1]).start()
		joirEnd=re.search('(])\. ',res[1]).end()
		joir=res[1][joirStart+1:joirEnd-3]		
		str+='\\joir '+joir+'\n'
		
		str+=outputJ(res[1])
		
	elif namespace.choice=='jees':		
		digitsStart=re.search('\. \d', res[1]).start()
		digits=re.findall('(\d+)', res[1][digitsStart:])
			
		other=re.split('\. ', res[1][:digitsStart])

		str+='\\paper '
		for i in range(len(other)-1):
			if i!=len(other)-2:
				str+=other[i]+'. '
			else:
				str+=other[i]+'\n'
			
		str+='\\joir '+other[len(other)-1]+'\n'	
				
		str+=outputJ(res[1])
	
	if namespace.choice=='jr':
		paper=re.split('//', res[1])[0]
		str+='\\paper '+paper+'\n'
				

		other=re.split('//', res[1])[1]
		joir=re.split('\. [0-9]', other, maxsplit=1)[0]
		str+='\\joir'+joir+'\n'
	
				
		str+=outputJ(other)
			
	if namespace.choice=='je':
		paper=re.split('//', res[1])[0]
		str+='\\paper '+paper[:-1]+'\n'
				
		other=re.split('//', res[1])[1]
		joir=re.split('\. [0-9]', other, maxsplit=1)[0]
		str+='\\joir'+joir+'\n'

		str+=outputJ(other)
		
		
	if namespace.choice=='ce':
		other=re.split('// ', res[1])[1]
		
		paper=re.split('//', res[1])[0]
		str+='\\paper '+paper+'\n'
		
		procinfoS=re.search('[(]\w+,', other)
		if procinfoS:
			procinfoS=procinfoS.start()
			procinfoE=re.search('[)],', other).start()
			joir=other[:procinfoS]
			str+='\\inbook '+joir+'\n'
			str+='\\procinfo '+other[procinfoS+1:procinfoE]+'\n'
			str+=outputC(other)
		else:
			joir=re.split(', ', other, maxsplit=1)[0]
			str+='\\inbook '+joir+'\n'
			procinfoStart=re.search(', ', other).start()
			procinfoEnd=re.search('\. ', other).end()
			str+='\\procinfo '+other[procinfoStart+1:procinfoEnd-2]+'\n'
			other=other[procinfoEnd:-2]
			publaddr=re.findall('\. [A-Z]\w+' , other)
			publaddrStart=re.search(publaddr[0] , other).start()
			publaddrEnd=re.search(': ', other).start()
			
			publ=other[:publaddrStart]
			str+='\\publ '+publ+'\n'
			str+='\\publaddr '+other[publaddrStart+2:publaddrEnd]+'\n'

			digits=re.findall('(\d+)', other)
			str+='\\yr '+digits[0]+'\n\\pages '+digits[1]+'--'+digits[2]+'\n'
		
		
		
	elif namespace.choice=='cr':
		paper=re.split('//', res[1])[0]
		str+='\\paper '+paper+'\n'
			

		other=re.split('// ', res[1])[1]

		
		joir=re.split(' [(]', other, maxsplit=1)[0]
		str+='\\inbook '+joir+'\n'


		procinfoStart=re.search('[(]', other).start()
		procinfoEnd=re.search('[)]', other).end()
		str+='\\procinfo '+other[procinfoStart+1:procinfoEnd-1]+'\n'


		other=other[procinfoEnd+2:-2]
		publaddrEnd=re.search(': ', other).start()
		publEnd=re.search(', ', other).start()
		publaddr=other[:publaddrEnd]
		publ=other[publaddrEnd+2:publEnd]
		str+='\\publ '+publ+'\n'
			
		if publaddr[0]=='М':
			publaddr='Москва'
		
		str+='\\publaddr '+publaddr+'\n'

		digits=re.findall('(\d+)', other)
		str+='\\yr '+digits[0]+'\n\\pages '+digits[1]+'--'+digits[2]+'\n'
		outputC(other)
		
	elif namespace.choice=='cres':
		paper=re.split('\.', res[1])[1]
		str+='\\paper'+paper+'\n'
			
		joirStart=re.search('[[]',res[1]).start()
		other=res[1][joirStart:]
		
		
		joirEnd=re.search(' [(]',other).end()
		joir=other[1:joirEnd-2]
		str+='\\inbook '+joir+'\n'
		
		procinfoStart=re.search(' [(]', other).start()
		procinfoEnd=re.search('[)]', other).end()
		str+='\\procinfo '+other[procinfoStart+2:procinfoEnd-1]+'\n'
					
		
		other=other[procinfoEnd+2:-1]
	
		publaddrEnd=re.search(', [A-Z]\w+' , other)
		if publaddrEnd:
			publaddrEnd=publaddrEnd.start()
			
		publEnd=re.search(', \d', other).start()
		
		publaddrEnd=re.search(', ', other).start()
		publEnd=re.search(', \d', other).start()
		
		publ=other[publaddrEnd+2:publEnd]
		publaddr=other[:publaddrEnd]
		
		if publ:
			str+='\\publ '+other[publaddrEnd+2:publEnd]+'\n'
			str+='\\publaddr'+other[:publaddrEnd]+'\n'
		else:
			str+='\\publ'+other[:publaddrEnd]+'\n'
		
		str+=outputC(other)
		
	elif namespace.choice=='cees':
		other=re.split('\.', res[1], maxsplit=1)
		str+='\\paper '+other[0]+'\n'
			
		other=other[1]
		

		
		procinfoS=re.search('[(]\w+,', other)
		if procinfoS:
			procinfoS=procinfoS.start()
			procinfoE=re.search('[)],', other).start()
			joir=other[:procinfoS]
			str+='\\inbook'+joir+'\n'
			str+='\\procinfo '+other[procinfoS+1:procinfoE]+'\n'
			str+=outputC(other)
		else:
			joir=re.split(', ', other, maxsplit=1)[0]
			str+='\\inbook'+joir+'\n'
			procinfoStart=re.search(', ', other).start()
			procinfoEnd=re.search('\. ', other).end()
			str+='\\procinfo'+other[procinfoStart+1:procinfoEnd-2]+'\n'
			
			
			other=other[procinfoEnd:-2]
			
			publaddr=re.findall('\. [A-Z]\w+' , other)
			publaddrStart=re.search(publaddr[0] , other).start()
			publaddrEnd=re.search('\. \d', other).start()
			publ=other[:publaddrStart]
			
			str+='\\publ '+publ+'\n'
			str+='\\publaddr '+other[publaddrStart+2:publaddrEnd]+'\n'

			digits=re.findall('(\d+)', other)
			str+='\\yr '+digits[0]+'\n\\pages '+digits[1]+'--'+digits[2]+'\n'
	
	
	if namespace.choice=='br':
		other=re.split('\. ', res[1])	
	
		publTillEnd=other[1]
		
		str+='\\book '+other[0]+'\n'
		publaddrEnd=re.search('.: ', publTillEnd).start()
		publEnd=re.search(', ', publTillEnd).start()
		publ=publTillEnd[publaddrEnd+3:publEnd]
		
		publaddr=publTillEnd[:publaddrEnd+1]
		if publaddr[0]=='М':
			publaddr='Москва'
		
		str+='\\publ '+publ+'\n'
		str+='\\publaddr '+publaddr+'\n'
	
		str+=outputB(publTillEnd)		
		
	elif namespace.choice=='be' or namespace.choice=='bees':
		other=re.split('\. ', res[1])	
		
		publTillEnd=other[1]
		
		str+='\\book '+other[0]+'\n'
		publaddrEnd=re.search(', ', publTillEnd).start()
		publEnd=re.search(', \d', publTillEnd).start()
		
		publ=publTillEnd[publaddrEnd+2:publEnd]
		publaddr=publTillEnd[:publaddrEnd]
		
		if publ:
			str+='\\publ '+publ+'\n'
			str+='\\publaddr '+publaddr+'\n'
		else:
			str+='\\publ '+publaddr+'\n'
		
		
		str+=outputB(res[1])
		
	elif namespace.choice=='bres':
		other=re.split('\. ', res[1])	
				
		publTillEnd=other[1]
		
		bookStart=re.search(' [[]', other[0]).start()
		bookEnd=re.search('[]]', other[0]).end()
		
		str+='\\book '+other[0][bookStart+2:bookEnd-1]+'\n'

		
		publaddrEnd=re.search(', ', publTillEnd).start()
		publEnd=re.search(', \d', publTillEnd).start()
		publ=publTillEnd[publaddrEnd+2:publEnd]
		publaddr=publTillEnd[:publaddrEnd]
			
		str+='\\publ '+publ+'\n'
		str+='\\publaddr '+publaddr+'\n'
		
		str+=outputB(res[1])
		
		
		
	if namespace.choice=='er' or namespace.choice=='ee':
		author=re.search('[А-ЯA-Z]\.|(et al.)', line)
		
		author1=re.search('\. \w+', line).start()
		
		str=''
		if author:
			str=getAuthor(line)
			other=line[author1+2:]
		else:
			other=line
		urlStart=re.search('URL:', other).start()
		
		str+='\\eprint '+other[:urlStart-2]+'\n'
		
		urlEnd=re.search(' [(]', other).start()
		
		url=other[urlStart+5:urlEnd]
		
		str+='\\href{'+url+'}{{\\tt '+url+'}\n\n'
		
	elif namespace.choice=='eees':
	
		author=re.search('[А-ЯA-Z]\.|(et al.)', line)
		
		author1=re.search('\. \w+', line).start()
		
		str=''
		if author:
			str=getAuthor(line)
			other=line[author1+2:]
		else:
			other=line
		urlStart=re.search('Available at: ', other).end()
		
		str+='\\eprint '+other[:urlStart-15]+'\n'
		
		urlEnd=re.search(' [(]', other).start()
		url=other[urlStart:urlEnd]
		str+='\\href{'+url+'}{{\\tt '+url+'}}\n\n'
	
	elif namespace.choice=='eres':
	
		author=re.search('[А-ЯA-Z]\.|(et al.)', line)
		
		author1=re.search('\. \w+', line).start()
		
		str=''
		if author:
			str=getAuthor(line)
			other=line[author1+2:]
		else:
			other=line
	
		eprintStart=re.search(' [[]', other).start()
		eprintEnd=re.search('[]]', other).end()
		
		urlStart=re.search('Available at: ', other).end()
		
		
		urlEnd=re.search(' [(]', other).start()
		url=other[urlStart:urlEnd]
		str+='\\eprint '+other[eprintStart+2:eprintEnd-1]+'\n\\href{'+url+'}{{\\tt '+url+'}}\n\n'
		
	fout.write(str)
		
		
	

	
	

	
	


