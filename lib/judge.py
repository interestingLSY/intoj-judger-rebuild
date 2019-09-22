#coding: utf-8
import sys, os
import config, log, lrun, modules

def Judge(
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
		diff -w {stdout} {output} \
		>{diff_temp_path}'.format(
			max_time = config.config['judging']['max_time']/1000.0,
			max_memory = config.config['judging']['max_memory']*1024*1024,
			stdout = stdout_path,
			output = output_path,
			diff_temp_path = diff_temp_path
		)

	result = lrun.Run(diff_command)
	if result['signaled'] != 0:
		raise BaseException('在验证答案时出现错误: %s'%str(result))

	if result['exitcode'] == 1:
		judger_message = modules.GetPreview(diff_temp_path,config.config['previews']['judger_message'])
		return {
			'status': 5,
			'score': 0,
			'judger_message': judger_message
		}
	else:
		return {
			'status': 11,
			'score': 100
		}
