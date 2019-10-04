import os, sys

def GetPreview(path,length_limit):
	preview = open(path,'r').read(length_limit)
	length = os.path.getsize(path)
	if length <= length_limit:
		return preview
	if preview[-1] != '\n': preview += '\n'
	return preview + '... (%d chars omitted)'%(length-length_limit)

def EscapeFilename(filename):
	filename.replace('"','\\"')
	return filename
