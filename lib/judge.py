# coding: utf-8
import sys, os
import config, log, lrun, modules, static

def JudgeByTextCompare(
		data_config,
		input_path,
		output_path
	):
	stdout_path = config.config['stdout_path']
	diff_temp_path = config.config['diff_temp_path']
	diff_command = ' \
		lrun \
		--max-real-time {max_time} \
		--max-memory {max_memory} \
		diff -w "{stdout}" "{output}" \
		>"{diff_temp_path}"'.format(
			max_time = config.config['judging']['max_time']/1000.0,
			max_memory = config.config['judging']['max_memory']*1024*1024,
			stdout = stdout_path,
			output = output_path,
			diff_temp_path = diff_temp_path
		)
	result = lrun.Run(diff_command)

	if result['signaled'] != 0:
		raise BaseException('在验证答案时出现错误: %s'%str(result))
	if result['exceed'] != 'none':
		raise BaseException('在验证答案时出现 %s limit exceed'%result['exceed'])
	if result['exitcode'] == 1:
		judger_message = modules.GetPreview(diff_temp_path,config.config['previews']['judger_message'])
		return {
			'status': static.name_to_id['Wrong Answer'],
			'score': 0,
			'judger_message': judger_message
		}
	else:
		return {
			'status': static.name_to_id['Accepted'],
			'score': 100
		}

def JudgeBySpecialJudge(
		data_config,
		input_path,
		output_path
	):
	stdout_path = config.config['stdout_path']
	diff_temp_path = config.config['diff_temp_path']
	spj_run_command = ' \
		lrun \
		--max-real-time {max_time} \
		--max-memory {max_memory} \
		{spj_exe_path} "{input}" "{stdout}" "{output}" \
		2>"{diff_temp_path}"'.format(
			max_time = config.config['judging']['max_time']/1000.0,
			max_memory = config.config['judging']['max_memory']*1024*1024,
			spj_exe_path = config.config['spj_exe_path'],
			input = input_path,
			stdout = stdout_path,
			output = output_path,
			diff_temp_path = diff_temp_path
		)
	run_result = lrun.Run(spj_run_command)
	spj_message = open(diff_temp_path,'r').read()

	if run_result['signaled'] != 0:
		raise BaseException('在 spj 运行时出现错误: %s'%spj_message)
	if run_result['exceed'] != 'none':
		raise BaseException('在 spj 运行时出现 %s limit exceed'%run_result['exceed'])

	if run_result['exitcode'] == 0:		# AC
		return {
			'status': static.name_to_id['Accepted'],
			'score': 100,
			'judger_message': spj_message
		}
	elif run_result['exitcode'] == 1:	# WA
		return {
			'status': static.name_to_id['Wrong Answer'],
			'score': 0,
			'judger_message': spj_message
		}
	elif run_result['exitcode'] == 2:	# PE
		return {
			'status': static.name_to_id['Wrong Answer'],
			'score': 0,
			'judger_message': spj_message
		}
	elif run_result['exitcode'] in [3,4,8]:	# SPJ Judgement Failed
		return {
			'status': static.name_to_id['SPJ Judgement Failed'],
			'score': 0,
			'judger_message': spj_message
		}
	elif run_result['exitcode'] in [7]:		# PC
		score = float(spj_message.split()[1]) * 100
		return {
			'status': static.name_to_id['Partially Accepted'],
			'score': score,
			'judger_message': spj_message
		}
	else:
		return {
			'status': static.name_to_id['SPJ Judgement Failed'],
			'score': 0,
			'judger_message': 'Unknown exitcode: %d'%run_result['exitcode']
		}


def Judge(
		data_config,
		input_path,
		output_path
	):
	if data_config['data'].get('spj') == None:
		return JudgeByTextCompare(
			data_config = data_config,
			input_path = input_path,
			output_path = output_path
		)
	else:
		return JudgeBySpecialJudge(
			data_config = data_config,
			input_path = input_path,
			output_path = output_path
		)
