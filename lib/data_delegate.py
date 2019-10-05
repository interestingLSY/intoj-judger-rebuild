#coding:utf-8
import sys, os, json
import config, modules, db, log

def GetTestdataInfo(testdata_path):
	config_path = os.path.join(testdata_path,'config.json')
	if not os.path.exists(config_path):
		raise BaseException('测试数据目录 %s 下没有 config.json'%testdata_path)

	config = json.loads(open(config_path,'r').read())
	return config

def ValidateDataExistenceWithoutSubtask(testdata_path,config):
	count = int(config['testcasesCount'])
	prefix = config['prefix']
	input_suffix = config['inputSuffix']
	output_suffix = config['outputSuffix']
	for id in range(1,count+1):
		input_filename = '%s%d%s' % (prefix,id,input_suffix)
		output_filename = '%s%d%s' % (prefix,id,output_suffix)
		if not os.path.exists(os.path.join(testdata_path,input_filename)):
			raise BaseException('输入文件 %s 不存在'%input_filename)
		if not os.path.exists(os.path.join(testdata_path,output_filename)):
			raise BaseException('输出文件 %s 不存在'%output_filename)

def ValidataDataExistenceWithSubtask(testdata_path,config):
	input_suffix = config['inputSuffix']
	output_suffix = config['outputSuffix']
	for subtask in config['subtasks']:
		count = int(subtask['testcasesCount'])
		prefix = subtask['prefix']
		score = subtask['score']
		for id in range(1,count+1):
			input_filename = '%s%d%s' % (prefix,id,input_suffix)
			output_filename = '%s%d%s' % (prefix,id,output_suffix)
			if not os.path.exists(os.path.join(testdata_path,input_filename)):
				raise BaseException('输入文件 %s 不存在'%input_filename)
			if not os.path.exists(os.path.join(testdata_path,output_filename)):
				raise BaseException('输出文件 %s 不存在'%output_filename)

def Delegate(submission_id,submission_info,testdata_path):
	log.Log('cyan','Fetching data info...')

	data_config = {}

	problem_id = submission_info['problem_id']
	problems = db.Execute('SELECT time_limit, memory_limit FROM problems WHERE id=%s',problem_id)
	if len(problems) == 0:
		raise BaseException('题目 %d 不存在'%problem_id)
	data_config['time_limit'] = problems[0]['time_limit']
	data_config['memory_limit'] = problems[0]['memory_limit']

	data_config['data'] = GetTestdataInfo(testdata_path)

	print("data_config:")
	print(data_config)
	log.Log('green','Fetched.')

	log.Log('cyan','Validate data existence...')
	if data_config['data'].get('subtask',False) == False:
		ValidateDataExistenceWithoutSubtask(testdata_path,data_config['data'])
	else:
		ValidataDataExistenceWithSubtask(testdata_path,data_config['data'])
	log.Log('green','Validated.')

	return data_config
