import os, sys
import config

def Run(command):
	lrun_temp_path = config.config['lrun_temp_path']
	command += '  3>%s'%lrun_temp_path
	os.system(command)

	message = open(lrun_temp_path,'r').readlines()
	result = {
		'memory': int(message[0][9:])/1024,
		'cpu_time': int(float(message[1][9:])*1000),
		'real_time': int(float(message[2][9:])*1000),
		'signaled': int(message[3][9:]),
		'exitcode': int(message[4][9:]),
		'termsig': int(message[5][9:]),
		'exceed': message[6][9:].strip(),
	}
	# print(result)
	return result
