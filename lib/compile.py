#coding: utf-8
import os
import modules, config, log, lrun

def Compile(
		code_path,
		exe_path,
		language_config
	):
	log.Log('cyan','Compiling...')
	log.Log('none','Code: ',code_path)
	log.Log('none','Exe: ',exe_path)

	compile_command = language_config['compile_command'].format(
		source = code_path,
		exe = exe_path )
	log.Log('none','Compile command: ',compile_command)

	result = lrun.Run(' \
		lrun \
		--max-real-time {max_time} \
		--max-memory {max_memory} \
		--max-output {max_output} \
		{compile_command} \
		2>"{temp_file}"'.format(
			max_time = config.config['compilation']['max_time']/1000.0,
			max_memory = config.config['compilation']['max_memory']*1024*1024,
			max_output = config.config['compilation']['max_output']*1024,
			compile_command = compile_command,
			temp_file = config.config['comp_temp_path']
		)
	)

	if result['exceed'] != 'none':
		if result['exceed'] in ['REAL_TIME','CPU_TIME']:
			return { 'success': False, 'message': '编译超时... 你干了什么!?' }
		if result['exceed'] == 'MEMORY':
			return { 'success': False, 'message': '编译爆内存... 但愿你不是在攻击' }
		if result['exceed'] == 'OUTPUT':
			return { 'success': False, 'message': '编译器输出了太多东西... 建议本机编译一下试试' }
		raise ValueError('Unknown value for "EXCEED": %s'%exceed)

	if result['exitcode'] != 0:
		log.Log('yellow','Compile Error.')
		compilier_message = modules.GetPreview(config.config['comp_temp_path'],1024)
		print(compilier_message)
		return { 'success': False, 'message': compilier_message }
	else:
		log.Log('green','Compilation Passed.')
		return { 'success': True, 'message': '' }
