# coding: utf-8
import pymysql
import config

def Connect():
	db_name = config.config['database']['name']
	db_user = config.config['database']['user']
	db_host = config.config['database']['host']
	db_pass = config.config['database']['pass']
	db = pymysql.connect(db_host,db_user,db_pass,db_name)
	cur = db.cursor(cursor=pymysql.cursors.DictCursor)
	return db,cur
def EndConnect(db,cur):
	cur.close()
	db.close()

def Execute(cmd,arg=None):
	db, cur = Connect()
	if arg == None: cur.execute(cmd)
	else: cur.execute(cmd,arg)
	command_name = cmd.split()[0]
	if command_name not in ['SELECT']:
		db.commit()
	res = cur.fetchall()
	EndConnect(db,cur)
	return res

def GetSubmissionInfo(submission_id):
	submission_list = Execute('SELECT * FROM submissions WHERE id=%s',submission_id)
	if len(submission_list) == 0:
		raise ValueError('Submission %d does not exist'%submission_id)
	submission_info = submission_list[0]
	return submission_info
