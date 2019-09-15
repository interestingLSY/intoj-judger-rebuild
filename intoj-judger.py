#coding: utf-8
import os, sys
import lib

lib.config.ReadFromFile('config.json')

def Main():
	submission_id = lib.redis.GetNextQueueingSubmission()

Main()
