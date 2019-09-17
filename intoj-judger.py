#coding: utf-8
import os, sys, time, datetime, traceback
import lib

lib.config.ReadFromFile('config.json')

def JudgerMain(submission_id):
	lib.db.Execute('UPDATE submissions SET status=0 WHERE id=%s',submission_id)

	submission_info = lib.db.GetSubmissionInfo(submission_id)
	lib.log.Log('cyan','Submission info:')
	lib.log.Log('none','id:\t\t',submission_id)
	lib.log.Log('none','problem_id:\t',submission_info['problem_id'])
	lib.log.Log('none','contest_id:\t',submission_info['contest_id'])
	lib.log.Log('none','submitter:\t',submission_info['submitter'])
	lib.log.Log('none','language:\t',submission_info['language'])
	lib.log.Log('none','submit_time:\t',submission_info['submit_time'])

	compile_config = lib.config.config['compilation']
	language_config = lib.config.config['languages'][submission_info['language']]
	code_filename = 'main.%s'%language_config['extension']
	code_path = os.path.abspath('temp/%s'%code_filename)
	exe_filename = 'main'
	exe_path = os.path.abspath('temp/%s'%exe_filename)

	with open(code_path,'w') as codefile:
		codefile.write(submission_info['code'])

	compile_result = lib.compile.Compile(code_path,exe_path,os.path.abspath('temp/comp.txt'),language_config,compile_config)
	if not compile_result['success']:
		lib.db.Execute('UPDATE submissions SET status=3, compilier_message=%s WHERE id=%s',(compile_result['message'],submission_id))
		return

	lib.db.Execute('UPDATE submissions SET compilier_message=%s WHERE id=%s',(compile_result['message'],submission_id))

	if not os.path.exists('data'):
		raise BaseException('目录 data 不存在')
	testdata_path = os.path.abspath('data/%d'%submission_info['problem_id'])
	if not os.path.exists(testdata_path):
		raise BaseException('目录 %s 不存在'%testdata_path)

	data_config = lib.data_delegate.Delegate(submission_id,submission_info,testdata_path)

def Main():
	submission_id = lib.reedis.GetNextQueueingSubmission()
	if submission_id == None: return

	submission_id = int(submission_id)
	lib.log.Log('none','-----------------------------------------')
	lib.log.Log('green','New Task: ',submission_id)
	lib.reedis.NewQueueingSubmission(submission_id)
	try:
		JudgerMain(submission_id)
	except BaseException as exception:
		lib.log.Log('red','An Error occured:')
		lib.log.Log('none',traceback.format_exc(exception))
		lib.db.Execute('UPDATE submissions SET status=2, system_message=%s WHERE id=%s',(traceback.format_exc(exception),submission_id))

lib.log.Log('green','Intoj-judger starts running at',datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'))
if not os.path.exists('temp'):
	raise BaseException('目录 temp 不存在')
while True:
	Main()
	time.sleep(1)
