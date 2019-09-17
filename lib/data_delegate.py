#coding: utf-8
import sys, os
import config, db, log

def Delegate(submission_id,submission_info,testdata_path):
	log.Log('cyan','Fetching data info...')

	data_config = {}

	problem_id = submission_info['problem_id']
	problems = db.Execute('SELECT time_limit, memory_limit FROM problems WHERE id=%s',problem_id)
	if len(problems) == 0:
		raise BaseException('题目 %d 不存在'%problem_id)
	data_config['time_limit'] = problems[0]['time_limit']
	data_config['memory_limit'] = problems[0]['memory_limit']

	print(os.listdir(testdata_path))
	print(data_config)
	log.Log('green','Fetched.')

	return data_config
