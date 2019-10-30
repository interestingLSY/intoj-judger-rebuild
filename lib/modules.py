import os, sys
import log

def GetPreview(path,length_limit):
	try:
		preview = open(path,'r').read(length_limit)
		length = os.path.getsize(path)
		if length <= length_limit:
			return preview
		if preview[-1] != '\n': preview += '\n'
		return preview + '... (%d chars omitted)'%(length-length_limit)
	except:
		return 'An error occurred when getting preview for %s'%path

def EscapeFilename(filename):
	filename.replace('"','\\"')
	return filename
