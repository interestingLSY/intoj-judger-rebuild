# coding: utf-8
import sys, os, time, json
import config, db, log, lrun, judge, modules, static

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
		--max-real-time {real_time_limit} \
		--max-cpu-time {cpu_time_limit} \
		--max-memory {memory_limit} \
		--max-stack {memory_limit} \
		--max-output {output_limit} \
		--max-nfile 0 \
		{run_command} \
		<"{input_path}" \
		1>"{stdout_file}" \
		2>"{stderr_file}"'.format(
			real_time_limit = data_config['time_limit']/1000.0 + 1,
			cpu_time_limit = data_config['time_limit']/1000.0,
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
		'time_usage': run_result['cpu_time'] if run_result['exceed'] not in [ 'REAL_TIME' , 'CPU_TIME' ] else run_result['cpu_time'],
		'memory_usage': run_result['memory'],
		'runner_message': ''
	}

	if run_result['exceed'] == 'OUTPUT':
		result['status'] = static.name_to_id['Output Limit Exceeded']
		result['runner_message'] = 'Output limit exceed:\nThe output limit is %d M.'%config.config['running']['max_output']
	elif run_result['exceed'] in [ 'REAL_TIME' , 'CPU_TIME' ]:
		result['status'] = static.name_to_id['Time Limit Exceeded']
		result['runner_message'] = 'Time limit exceed:\nThe time limit is %d ms.'%data_config['time_limit']
	elif run_result['exceed'] == 'MEMORY':
		result['status'] = static.name_to_id['Memory Limit Exceeded']
		result['runner_message'] = 'Memory limit exceed:\nThe memory limit is %d M.'%data_config['memory_limit']
	elif run_result['signaled'] != 0:
		result['status'] = static.name_to_id['Runtime Error']
		result['runner_message'] = 'Runtime error:\nProgram exited abnormally with signal number %d and exitcode %d.'%(run_result['termsig'],run_result['exitcode'])
	else:
		result['status'] = static.name_to_id['Accepted']

	return result

def UpdateInfo(submission_id,result):
	detail = {
		'subtask': result.get('subtask',False),
		'cases': result.get('cases'),
		'subtasks': result.get('subtasks')
	}
	db.Execute('UPDATE submissions SET time_usage=%s, memory_usage=%s, status=%s, score=%s, detail=%s WHERE id=%s',
				(result['time_usage'],result['memory_usage'],result['status'],result['score'],json.dumps(detail),submission_id))

def RunAndJudgeWithoutSubtask(
		submission_id,
		submission_info,
		data_config,
		testdata_path,
		code_path,
		exe_path,
		language_config
	):
	testcases_count = data_config['data']['testcasesCount']
	result = {
		'time_usage': 0,
		'memory_usage': 0,
		'status': static.name_to_id['Running'],
		'score': 0,
		'cases': [ {
			'status': static.name_to_id['Waiting'],
			'time_usage': 0,
			'memory_usage': 0,
			'score': 0,
			'full_score': 0
		} for i in range(testcases_count) ]
	}
	all_statuses = []
	UpdateInfo(submission_id,result)

	for id in range(1,testcases_count+1):
		result['cases'][id-1]['status'] = static.name_to_id['Running']
		UpdateInfo(submission_id,result)

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

		if run_result['status'] != static.name_to_id['Accepted']:
			result['cases'][id-1]['score'] = 0
		else:
			judge_result = judge.Judge(
				data_config = data_config,
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
		# UpdateInfo(submission_id,result)
		# 下一个测试点开始时会调用 UpdateInfo
		# 故省略本次

	result['status'] = min(all_statuses)
	UpdateInfo(submission_id,result)

def RunAndJudgeWithSubtask(
		submission_id,
		submission_info,
		data_config,
		testdata_path,
		code_path,
		exe_path,
		language_config
	):
	result = {
		'subtask': True,
		'time_usage': 0,
		'memory_usage': 0,
		'status': static.name_to_id['Running'],
		'score': 0,
		'subtasks': [ {
			'name': subtask.get('name',''),
			'status': static.name_to_id['Waiting'],
			'time_usage': 0,
			'memory_usage': 0,
			'score': 0,
			'full_score': subtask['score'],
			'cases': [{
				'status': static.name_to_id['Waiting'],
				'time_usage': 0,
				'memory_usage': 0,
				'score': 0,
				'full_score': subtask['score']
			} for i in range(subtask['testcasesCount']) ]
		} for subtask in data_config['data']['subtasks'] ]
	}

	subtask_statuses = []
	for _subtask_id, subtask in enumerate(data_config['data']['subtasks']):
		subtask_id = _subtask_id + 1
		print('Running on subtask %d...'%subtask_id)

		skip_this_subtask = 0
		for reliance in subtask.get('rely',[]):
			if result['subtasks'][reliance-1]['status'] not in [static.name_to_id['Accepted'],static.name_to_id['Partially Accepted']]:
				skip_this_subtask = 1
				break
		if skip_this_subtask:
			result['subtasks'][subtask_id-1] = {
				'name': subtask.get('name',''),
				'status': static.name_to_id['Skipped'],
				'time_usage': 0,
				'memory_usage': 0,
				'score': 0,
				'full_score': subtask['score'],
				'cases': [{
					'status': static.name_to_id['Skipped'],
					'time_usage': 0,
					'memory_usage': 0,
					'score': 0,
					'full_score': subtask['score']
				} for i in range(subtask['testcasesCount']) ]
			}
			UpdateInfo(submission_id,result)
			continue

		result['subtasks'][subtask_id-1]['status'] = static.name_to_id['Running']
		UpdateInfo(submission_id,result)
		subtask_result = {
			'name': subtask.get('name',''),
			'status': static.name_to_id['Running'],
			'time_usage': 0,
			'memory_usage': 0,
			'score': subtask['score'],
			'full_score': subtask['score'],
			'cases': [{
				'status': static.name_to_id['Waiting'],
				'time_usage': 0,
				'memory_usage': 0,
				'score': 0,
				'full_score': subtask['score']
			} for i in range(subtask['testcasesCount']) ]
		}

		testcases_count = subtask['testcasesCount']
		cases_statuses = []
		for id in range(1,testcases_count+1):
			result['subtasks'][subtask_id-1]['cases'][id-1]['status'] = static.name_to_id['Running']
			UpdateInfo(submission_id,result)

			input_rel_path = '%s%d%s' % (subtask['prefix'],id,data_config['data']['inputSuffix'])
			output_rel_path = '%s%d%s' % (subtask['prefix'],id,data_config['data']['outputSuffix'])
			input_path = os.path.join(testdata_path,input_rel_path)
			output_path = os.path.join(testdata_path,output_rel_path)

			case_result = Run(
				data_config = data_config,
				exe_path = exe_path,
				input_rel_path = modules.EscapeFilename(input_rel_path),
				output_rel_path = modules.EscapeFilename(output_rel_path),
				input_path = modules.EscapeFilename(input_path),
				output_path = modules.EscapeFilename(output_path),
				language_config = language_config
			)
			case_result['score'] = subtask['score']
			case_result['full_score'] = subtask['score']
			# print(run_result)

			if case_result['status'] != static.name_to_id['Accepted']:
				case_result['score'] = 0
			else:
				judge_result = judge.Judge(
					data_config = data_config,
					input_path = modules.EscapeFilename(input_path),
					output_path = modules.EscapeFilename(output_path)
				)
				case_result['status'] = judge_result['status']
				case_result['score'] = judge_result['score']*case_result['full_score']/100.0
				case_result['judger_message'] = judge_result.get('judger_message')

			cases_statuses.append(case_result['status'])
			result['time_usage'] += case_result['time_usage']
			result['memory_usage'] = max(case_result['memory_usage'],result['memory_usage'])
			subtask_result['time_usage'] += case_result['time_usage']
			subtask_result['memory_usage'] = max(case_result['memory_usage'],subtask_result['memory_usage'])
			subtask_result['cases'][id-1] = case_result

			subtask_result['score'] = min(subtask_result['score'],case_result['score'])
			if case_result['status'] not in [static.name_to_id['Accepted'],static.name_to_id['Partially Accepted']]:
				for i in range(id+1,testcases_count+1):
					subtask_result['cases'][i-1]['status'] = static.name_to_id['Skipped']
				result['subtasks'][subtask_id-1] = subtask_result
				break

			result['subtasks'][subtask_id-1] = subtask_result
			UpdateInfo(submission_id,result)

		subtask_result['status'] = min(cases_statuses)
		subtask_statuses.append(subtask_result['status'])
		result['score'] += subtask_result['score']
		UpdateInfo(submission_id,result)

	result['status'] = min(subtask_statuses)
	UpdateInfo(submission_id,result)

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

	if data_config['data'].get('subtask',False) == False:
		RunAndJudgeWithoutSubtask(
			submission_id = submission_id,
			submission_info = submission_info,
			data_config = data_config,
			testdata_path = testdata_path,
			code_path = code_path,
			exe_path = exe_path,
			language_config = language_config
		)
	else:
		RunAndJudgeWithSubtask(
			submission_id = submission_id,
			submission_info = submission_info,
			data_config = data_config,
			testdata_path = testdata_path,
			code_path = code_path,
			exe_path = exe_path,
			language_config = language_config
		)
