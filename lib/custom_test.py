# coding: utf-8
import sys, os, time, json
import config, db, log, run_and_judge, modules, static

def CustomTest(
		submission_id,
		submission_info,
		code_path,
		exe_path,
		language_config
	):
	log.Log('cyan','Running...')

	input_data = db.Execute('SELECT input FROM custom_tests WHERE id=%s',submission_id)[0]['input']
	input_path = config.config['custom_test_stdin_path']
	with open(input_path,'w') as inputfile:
		inputfile.write(input_data)

	data_config = {
		'time_limit': config.config['custom_test']['max_time'],
		'memory_limit': config.config['custom_test']['max_memory']
	}
	run_result = run_and_judge.Run(
		data_config = data_config,
		exe_path = exe_path,
		input_rel_path = '',
		output_rel_path = '',
		input_path = input_path,
		output_path = '',
		language_config = language_config
	)
	if run_result['status'] == static.name_to_id['Accepted']:
		run_result['status'] = static.name_to_id['Done']
	output_data = modules.GetPreview(config.config['stdout_path'],config.config['custom_test']['max_output_show'])
	run_detail = {
		'stderr_preview': run_result['stderr_preview'],
		'runner_message': run_result['runner_message']
	}
	db.Execute('UPDATE custom_tests SET output=%s WHERE id=%s',(output_data,submission_id))
	db.Execute('UPDATE submissions SET time_usage=%s, memory_usage=%s, status=%s, detail=%s WHERE id=%s',
				(run_result['time_usage'],run_result['memory_usage'],run_result['status'],json.dumps(run_detail),submission_id))
	log.Log('green','Done.')
