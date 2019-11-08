# coding: utf-8
def Log(bkcolor,*args):
	s = ''
	for arg in args: s += str(arg)+' '
	s = s[:-1]
	if bkcolor not in ['none',None]:
		bkcolor_code = {
			'black': '40',
			'red': '41',
			'green': '42',
			'yellow': '43',
			'blue': '44',
			'purple': '45',
			'cyan': '46',
			'white': '47',
		}
		s = '\033[%sm'%bkcolor_code[bkcolor] + s + '\033[0m'
	print(s)
