#coding: utf-8
import os, sys, time, datetime
import lib

lib.config.ReadFromFile('config.json')

def Main():
	submission_id = lib.reedis.GetNextQueueingSubmission()
	if submission_id == None: return

	lib.log.Log('green','New Task: ',submission_id)
	lib.reedis.NewQueueingSubmission(submission_id)

	submission_info = lib.db.GetSubmissionInfo(submission_id)
	lib.log.Log('cyan','Submission info:')
	lib.log.Log('none','id:\t\t',submission_id)
	lib.log.Log('none','problem_id:\t',submission_info['problem_id'])
	lib.log.Log('none','contest_id:\t',submission_info['contest_id'])
	lib.log.Log('none','submitter:\t',submission_info['submitter'])
	lib.log.Log('none','language:\t',submission_info['language'])
	lib.log.Log('none','submit_time:\t',submission_info['submit_time'])

	language_config = lib.config.config['languages'][submission_info['language']]
	code_filename = 'main.%s'%language_config['extension']
	code_abs_path = os.path.abspath('temp/%s'%code_filename)
	exe_filename = 'main'
	exe_abs_path = os.path.abspath('temp/%s'%exe_filename)

	with open(code_abs_path,'w') as codefile:
		codefile.write(submission_info['code'])

	compilation_result = lib.compile.Compile(code_abs_path,exe_abs_path,language_config)

lib.log.Log('green','Intoj-judger starts running at',datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'))
while True:
	Main()
	time.sleep(10)
