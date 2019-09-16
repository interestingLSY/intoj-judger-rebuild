import log

def Compile(code_abs_path,exe_abs_path,language_config):
	log.Log('cyan','Compiling...')
	log.Log('none','Code: ',code_abs_path)
	log.Log('none','Exe: ',exe_abs_path)

	compile_command = language_config['compile_command'].format(
		source = code_abs_path,
		exe = exe_abs_path )
	log.Log('none','Compile command: ',compile_command)
