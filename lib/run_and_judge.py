import sys, os, time, json
import config, db, log, lrun

def Run(
		data_config,
		exe_path,
		input_rel_path,
		output_rel_path,
		input_path,
		output_path,
		stdout_path,
		stderr_path):
	run_command = '{exe}'.format(exe=exe_path)
	run_result = lrun.Run(' \
		lrun \
		--max-real-time {time_limit} \
		--max-memory {memory_limit} \
		--max-output {output_limit} \
		{run_command} \
		1>{stdout_file} \
		2>{stderr_file}'.format(
			time_limit = data_config['time_limit']/1000.0,
			memory_limit = data_config['memory_limit']*1024*1024,
			output_limit = config.config['running']['max_output']*1024,
			run_command = run_command,
			stdout_file = stdout_path,
			stderr_file = stderr_path
		)
	)

	input_preview = open(input_path,'r').read(config.config['previews']['input'])
	output_preview = open(output_path,'r').read(config.config['previews']['output'])
	stdout_preview = open(stdout_path,'r').read(config.config['previews']['stdout'])
	stderr_preview = open(stdout_path,'r').read(config.config['previews']['stderr'])

	result = {
		'input_rel_path': input_rel_path,
		'output_rel_path': output_rel_path,
		'input_preview': input_preview,
		'output_preview': output_preview,
		'stdout_preview': stdout_preview,
		'stderr_preview': stderr_preview,
		'time_usage': run_result['cpu_time'],
		'memory_usage': run_result['memory']
	}

	if run_result['exceed'] == 'OUTPUT':
		result['status'] = 6
	elif run_result['exceed'] == 'REAL_TIME':
		result['status'] = 7
	elif run_result['exceed'] == 'MEMORY':
		result['status'] = 8
	elif run_result['exitcode'] != 0:
		result['status'] = 9
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
		stdout_path,
		stderr_path):
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
	overall_status = 0
	UpdateInfo(submission_id,result)

	for id in range(1,testcases_count+1):
		input_rel_path = '%s%d%s' % (data_config['data']['prefix'],id,data_config['data']['inputSuffix'])
		output_rel_path = '%s%d%s' % (data_config['data']['prefix'],id,data_config['data']['outputSuffix'])
		input_path = os.path.join(testdata_path,input_rel_path)
		output_path = os.path.join(testdata_path,output_rel_path)

		run_result = Run(
			data_config = data_config,
			exe_path = exe_path,
			input_rel_path = input_rel_path,
			output_rel_path = output_rel_path,
			input_path = input_path,
			output_path = output_path,
			stdout_path = stdout_path,
			stderr_path = stderr_path
		)
		print(run_result)

		full_score = 100.0 / testcases_count
		run_result['full_score'] = full_score

		result['cases'][id-1] = run_result
		overall_status = max(overall_status,run_result['status'])
		UpdateInfo(submission_id,result)

		if run_result['status'] != 11:
			result['cases'][id-1]['score'] = 0
			continue
		result['cases'][id-1]['score'] = full_score
		result['score'] += full_score
		UpdateInfo(submission_id,result)

	result['status'] = overall_status
	UpdateInfo(submission_id,result)
