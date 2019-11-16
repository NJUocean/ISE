import sys
import os
import clang.cindex
import tempfile
import subprocess
from clang.cindex import Config
from optparse import OptionParser

Config.set_library_file("libclang-6.0.so.1")

def format(str):
	line = str.strip()
	deleteflag = False
	if line == "" or line.startswith("//") or line.startswith("#include"):
		deleteflag = True
	return line,deleteflag

def traverse(node,code_sequence,hashtable,position):
    for child in node.get_children():
    	position.append(node.location.line)
    	code_sequence.append(hashtable.index(node.kind))
    	traverse(child,code_sequence,hashtable,position)

def LCS(s1,s2,maxlen):
	l1 = len(s1)
	l2 = len(s2)
	match = []
	if l1 == 0 or l2 == 0:
		return match
	for i in range(l1):
		for j in range(l2):
			k = 0
			while i+k < l1 and j+k <l2 and s1[i+k]>0 and s2[j+k]>0 and s1[i+k]==s2[j+k]:
				k=k+1
			if k > maxlen:
				match = [[k,i,j]]
				maxlen = k
			elif k == maxlen:
				match.append([k,i,j])
	return match

def codesim(code1, code2, verbose = False):
	with open(code1) as file:
		code_lines1 = file.readlines()
	file.close()
	with open(code2) as file:
		code_lines2= file.readlines()
	file.close()

	delete1 = []
	for i in range(len(code_lines1)):
		line = code_lines1[i]
		line, flag= format(line)
		if flag:
			delete1.append(i)

	delete2 = []
	for i in range(len(code_lines2)):
		line = code_lines2[i]			
		line, flag= format(line)
		if flag:
			delete2.append(i)

	for i in range(len(delete1)-1,-1,-1):
		del code_lines1[delete1[i]]

	for i in range(len(delete2)-1,-1,-1):
		del code_lines2[delete2[i]]

	tmpdir = tempfile.mkdtemp()
	file1 = tmpdir + "/file1.cpp"
	file2 = tmpdir + "/file2.cpp"

	with open(file1,"w") as f:
		f.writelines(code_lines1)
	f.close()

	with open(file2,"w") as f:
		f.writelines(code_lines2)
	f.close()

	index = clang.cindex.Index.create()
	tu1 = index.parse(file1)
	tu2 = index.parse(file2)
	s1 = []
	s2 = [] 

	root1 = tu1.cursor 
	root2 = tu2.cursor 
	hashtable = root1.kind.get_all_kinds()  
	position1 = [] 
	position2 = [] 
	traverse(root1,s1,hashtable,position1)
	traverse(root2,s2,hashtable,position2)

	match1 = LCS(s1,s2,5)
	s3 = s1[0:(match1[0][1])]
	s4 = s1[(match1[0][1]+match1[0][0]):]
	s5 = s2[0:(match1[0][2])]	
	s6 = s2[(match1[0][2]+match1[0][0]):]

	ss=[]
	ss.append(s3)
	ss.append(s4)
	sss=[]
	sss.append(s5)
	sss.append(s6)

	second = 0
	match = []
	for i in ss:
		for j in sss:
			temp = LCS(i,j,5)
			if len(temp)>0 and temp[0][0] > second:
				second = temp[0][0]
				match = temp 
	sim = 100*float((match1[0][0] + match[0][0]))/min(len(s1),len(s2))

	if verbose == False:
		print ('%.2f' %sim)
	else:
		print ('%.2f' %sim)
		print ("\n")
		clonecode1 = list(set(position1[match1[0][1]:(match1[0][0]+match1[0][1])]) | set(position1[match[0][1]:(match[0][0]+match[0][1])]))
		clonecode2 = list(set(position2[match1[0][2]:(match1[0][0]+match1[0][2])]) | set(position2[match[0][2]:(match[0][0]+match[0][2])]))
		print ("In %s :" %code1) 
		for i in clonecode1:
			print (code_lines1[i])
		print ("\n")
		print ("In %s :" %code2)
		for i in clonecode2:
			print (code_lines2[i])

if __name__ == '__main__':
	usage = "codesim [-v|--verbose] [-h|--help] code1.c/cpp code2.c/cpp"
	parser = OptionParser(usage)
	parser.add_option("-v","--verbose",default = False, action = "store_true", dest = "verbose", help="enable verbose parsing, default: false")
	(options,args) = parser.parse_args()
	if len(args)==2 and (args[0].endswith(".cpp") or args[0].endswith(".c")) and (args[1].endswith(".cpp") or args[1].endswith(".c")):
		codesim(code1= args[0], code2= args[1], verbose = options.verbose)
	else:
		print("Wrong Input!\n" + "Usage: " + usage)
