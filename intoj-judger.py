#coding: utf-8
import os, sys, time, datetime
import lib

lib.config.ReadFromFile('config.json')

def Main():
	submission_id = lib.reedis.GetNextQueueingSubmission()
	if submission_id == None: return

	lib.log.Log('green','New Task: ',submission_id)
	# lib.reedis.NewQueueingSubmission(submission_id)
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
	code_abs_path = os.path.abspath('temp/%s'%code_filename)
	exe_filename = 'main'
	exe_abs_path = os.path.abspath('temp/%s'%exe_filename)

	with open(code_abs_path,'w') as codefile:
		codefile.write(submission_info['code'])

	compile_result = lib.compile.Compile(code_abs_path,exe_abs_path,os.path.abspath('temp/comp.txt'),language_config,compile_config)
	if not compile_result['success']:
		lib.log.Log('yellow','Result: ','Compile Error.')
		lib.db.Execute('UPDATE submissions SET status=3, compilier_message=%s WHERE id=%s',(compile_result['message'],submission_id))
		return
	else:
		lib.log.Log('green','Result: ','Compilation Passed.')
		lib.db.Execute('UPDATE submissions SET status=12, compilier_message=%s WHERE id=%s',(compile_result['message'],submission_id))
		return

lib.log.Log('green','Intoj-judger starts running at',datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'))
while True:
	Main()
	time.sleep(1)
