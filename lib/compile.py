#coding: utf-8
import os
import log

def Compile(code_path,exe_path,temp_path,language_config,compile_config):
	log.Log('cyan','Compiling...')
	log.Log('none','Code: ',code_path)
	log.Log('none','Exe: ',exe_path)

	compile_command = language_config['compile_command'].format(
		source = code_path,
		exe = exe_path )
	log.Log('none','Compile command: ',compile_command)

	message = os.popen(' \
		lrun \
		--max-real-time {max_time} \
		--max-memory {max_memory} \
		--max-output {max_output} \
		{compile_command} \
		2>{temp_file} 3>&1'.format(
			max_time = compile_config['max_time']/1000.0,
			max_memory = compile_config['max_memory']*1024*1024,
			max_output = compile_config['max_output'],
			compile_command = compile_command,
			temp_file = temp_path
		)
	).read()

	exceed = message[message.find('EXCEED'):][6:].strip()
	if exceed != 'none':
		if exceed in ['REAL_TIME','CPU_TIME']:
			return { 'success': False, 'message': '编译超时... 你干了什么!?' }
		if exceed == 'MEMORY':
			return { 'success': False, 'message': '编译爆内存... 但愿你不是在攻击' }
		if exceed == 'OUTPUT':
			return { 'success': False, 'message': '编译器输出了太多东西... 建议本机编译一下试试' }
		raise ValueError('Unknown value for "Exceed": %s'%exceed)

	exitcode = int(message[message.find('EXITCODE'):message.find('TERMSIG')][8:].strip())
	if exitcode != 0:
		log.Log('yellow','Result: ','Compile Error.')
		compilier_message = open(temp_path,'r').read()
		print(compilier_message)
		return { 'success': False, 'message': compilier_message }
	else:
		log.Log('green','Compilation Passed.')
		return { 'success': True, 'message': '' }
