import sys, os, time, json
import config, db, log, lrun, judge, modules

def Run(
		data_config,
		exe_path,
		input_rel_path,
		output_rel_path,
		input_path,
		output_path,
		language_config
	):
	stdout_path = config.config['stdout_path']
	stderr_path = config.config['stderr_path']

	run_command = language_config['run_command'].format(exe=exe_path)
	run_result = lrun.Run(' \
		lrun \
		--max-real-time {time_limit} \
		--max-memory {memory_limit} \
		--max-stack {memory_limit} \
		--max-output {output_limit} \
		--max-nfile 0 \
		{run_command} \
		<"{input_path}" \
		1>"{stdout_file}" \
		2>"{stderr_file}"'.format(
			time_limit = data_config['time_limit']/1000.0,
			memory_limit = data_config['memory_limit']*1024*1024,
			output_limit = config.config['running']['max_output']*1024*1024,
			run_command = run_command,
			input_path = input_path,
			stdout_file = stdout_path,
			stderr_file = stderr_path
		)
	)

	input_preview = modules.GetPreview(input_path,config.config['previews']['input'])
	output_preview = modules.GetPreview(output_path,config.config['previews']['output'])
	stdout_preview = modules.GetPreview(stdout_path,config.config['previews']['stdout'])
	stderr_preview = modules.GetPreview(stderr_path,config.config['previews']['stderr'])

	result = {
		'input_rel_path': input_rel_path,
		'output_rel_path': output_rel_path,
		'input_preview': input_preview,
		'output_preview': output_preview,
		'stdout_preview': stdout_preview,
		'stderr_preview': stderr_preview,
		'time_usage': run_result['cpu_time'] if run_result['exceed'] != 'REAL_TIME' else run_result['real_time'],
		'memory_usage': run_result['memory'],
		'runner_message': ''
	}

	if run_result['exceed'] == 'OUTPUT':
		result['status'] = 6
		result['runner_message'] = 'Output limit exceed:\nThe output limit is %d M.'%config.config['running']['max_output']
	elif run_result['exceed'] == 'REAL_TIME':
		result['status'] = 7
		result['runner_message'] = 'Time limit exceed:\nThe time limit is %d ms.'%data_config['time_limit']
	elif run_result['exceed'] == 'MEMORY':
		result['status'] = 8
		result['runner_message'] = 'Memory limit exceed:\nThe memory limit is %d M.'%data_config['memory_limit']
	elif run_result['signaled'] != 0:
		result['status'] = 9
		result['runner_message'] = 'Runtime error:\nProgram exited abnormally with signal number %d and exitcode %d.'%(run_result['termsig'],run_result['exitcode'])
	else:
		result['status'] = 11

	return result

def UpdateInfo(submission_id,result):
	db.Execute('UPDATE submissions SET time_usage=%s, memory_usage=%s, status=%s, score=%s, detail=%s WHERE id=%s',
				(result['time_usage'],result['memory_usage'],result['status'],result['score'],json.dumps(result['cases']),submission_id))

def RunAndJudge(
		submission_id,
		submission_info,
		data_config,
		testdata_path,
		code_path,
		exe_path,
		language_config
	):
	log.Log('cyan','Running...')

	testcases_count = data_config['data']['testcasesCount']
	result = {
		'time_usage': 0,
		'memory_usage': 0,
		'status': 0,
		'score': 0,
		'cases': [ {
			'status': 1,
			'time_usage': 0,
			'memory_usage': 0,
			'score': 0,
			'full_score': 0
		} for i in range(testcases_count) ]
	}
	all_statuses = []
	UpdateInfo(submission_id,result)

	for id in range(1,testcases_count+1):
		input_rel_path = '%s%d%s' % (data_config['data']['prefix'],id,data_config['data']['inputSuffix'])
		output_rel_path = '%s%d%s' % (data_config['data']['prefix'],id,data_config['data']['outputSuffix'])
		input_path = os.path.join(testdata_path,input_rel_path)
		output_path = os.path.join(testdata_path,output_rel_path)

		run_result = Run(
			data_config = data_config,
			exe_path = exe_path,
			input_rel_path = modules.EscapeFilename(input_rel_path),
			output_rel_path = modules.EscapeFilename(output_rel_path),
			input_path = modules.EscapeFilename(input_path),
			output_path = modules.EscapeFilename(output_path),
			language_config = language_config
		)
		print(run_result)

		full_score = 100.0 / testcases_count
		run_result['full_score'] = full_score

		result['cases'][id-1] = run_result

		if run_result['status'] != 11:
			result['cases'][id-1]['score'] = 0
		else:
			judge_result = judge.Judge(
				data_config = data_config['data'],
				input_path = modules.EscapeFilename(input_path),
				output_path = modules.EscapeFilename(output_path)
			)
			result['cases'][id-1]['status'] = judge_result['status']
			result['cases'][id-1]['score'] = judge_result['score']*full_score/100.0
			result['cases'][id-1]['judger_message'] = judge_result.get('judger_message')

		result['time_usage'] += run_result['time_usage']
		result['memory_usage'] = max(result['memory_usage'],run_result['memory_usage'])
		result['score'] += result['cases'][id-1]['score']
		all_statuses.append(result['cases'][id-1]['status'])
		UpdateInfo(submission_id,result)

	result['status'] = min(all_statuses)
	UpdateInfo(submission_id,result)
