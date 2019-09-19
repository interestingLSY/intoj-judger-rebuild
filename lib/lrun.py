import os, sys

def Run(command):
	command += '  3>.lrunres'
	os.system(command)
	message = open('.lrunres').readlines()
	os.system('rm -f .lrunres')
	result = {
		'memory': int(message[0][9:])/1024,
		'cpu_time': int(float(message[1][9:])*1000),
		'real_time': int(float(message[2][9:])*1000),
		'signaled': int(message[3][9:]),
		'exitcode': int(message[4][9:]),
		'termsig': int(message[5][9:]),
		'exceed': message[6][9:].strip(),
	}
	return result
