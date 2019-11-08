# coding: utf-8
from redis import StrictRedis
import config

def NewConnection():
	return StrictRedis(
		host = config.config['redis']['host'],
		port = config.config['redis']['port'],
		db = 0,
		password = config.config['redis']['pass']
	)

def GetNextQueueingSubmission():
	redis = NewConnection()
	submission_id = redis.lpop('intoj-waiting-judge')
	if submission_id != None:
		return submission_id
	else:
		submission_id = redis.lpop('intoj-waiting-rejudge')
		return submission_id

def NewQueueingSubmission(submission_id):
	redis = NewConnection()
	redis.rpush('intoj-waiting-judge',submission_id)
