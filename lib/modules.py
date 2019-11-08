# coding: utf-8
import os, sys
import log

def GetPreview(path,length_limit):
	try:
		preview = open(path,'r').read(length_limit)
		try:
			preview.decode('utf-8')
		except:
			return '存在非法的 utf-8 字符'
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
