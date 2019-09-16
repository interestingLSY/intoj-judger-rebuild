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
	return redis.lpop('intoj-waiting-judge')

def NewQueueingSubmission(submission_id):
	redis = NewConnection()
	redis.rpush('intoj-waiting-judge',submission_id)
