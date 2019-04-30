import time
import pyrebase
import discord
import random
import json
from datetime import datetime
from colorama import init as initcolor
from colorama import Fore, Style
initcolor()

# Get firebase config
f = open('dbconfig.json')

config = json.loads(f.read())

f.close()

# Init firebase
firebase = pyrebase.initialize_app(config)

fdb = firebase.database()

# Defaults
dev=True
log=False

def timestamp():
	return str(datetime.now())

def log_event(func):
	print(Style.BRIGHT+Fore.CYAN+"\n[{stamp}]: db.".format(stamp=timestamp())+"{func}".format(func=func)+Style.RESET_ALL)

def user_ref_get():
	# Gets the users of the firebase database and returns it as a dictionary
	return dict(fdb.child('users').get().val())

def alias_ref_get():
	# Gets the users of the firebase database and returns it as a dictionary
	return dict(fdb.child('aliases').get().val())

def set_dev(d):
	global dev
	dev=d
	print('db: dev set to {}'.format(dev))

def set_log(l):
	global log
	log=l
	print('db: log set to {}'.format(log))

def get_users():
	if dev:
		return fdb.child('testing').child('users')
	else:
		return fdb.child('users')

def get_user_names():
	return get_users().get().val()

def create_id_reference(ID,user):
	if dev:
		if fdb.child('testing/IDs/{}'.format(ID)).get().val() == None:
			fdb.child('testing/IDs').update({ID:user})
	else:
		if fdb.child('userIDs/{}'.format(ID)).get().val() == None:
			fdb.child('userIDs').update({ID:user})

def find_user_from_id(ID):
	if dev:
		return fdb.child('testing').child('IDs').child(ID).get().val()
	else:
		return fdb.child('userIDs').child(ID).get().val()

def user_add(ID, user, name):
	log_event('user_add')
	print(ID, user, name)
	name = name.replace('<','&lt;')
	name = name.replace('>','&gt;')
	if dev:
		# Create ID reference if it doesn't exist
		if fdb.child('testing/IDs/{}'.format(ID)).get().val() == None:
			fdb.child('testing/IDs').update({ID:user})

		user = fdb.child('testing/IDs/{}'.format(ID)).get().val()

		if fdb.child('testing/users/{}'.format(user)).get().val() == None:
			fdb.child('testing/users').update({user: {'allpts':0, 'name':name, 'points': 0}})
		else:
			return False
	else:
		# Create ID reference if it doesn't exist
		if fdb.child('userIDs/{}'.format(ID)).get().val() == None:
			fdb.child('userIDs').update({ID:user})

		user = fdb.child('userIDs/{}'.format(ID)).get().val()

		if fdb.child('users/{}'.format(user)).get().val() == None:
			fdb.child('users').update({user: {'allpts':0, 'name':name, 'points': 0}})
		else:
			return False

# score
def score_get(ID):
	log_event('score_get')
	print(ID)
	user = find_user_from_id(ID)
	return dict(get_users().child(user).get().val())

def score_update(ID,amount):
	log_event('score_update')
	print(ID,amount)
	user = find_user_from_id(ID)
	season_score = score_get(ID)['points']
	alltime_score = score_get(ID)['allpts']
	get_users().child(user).update({'points':season_score+int(amount)})
	get_users().child(user).update({'allpts':alltime_score+int(amount)})
	print('Value of {user} changed by {amount}: {before} -> {after}'.format(
		user=find_user_from_id(ID), 
		amount=amount, 
		before=season_score, 
		after=score_get(ID)['allpts']))
	return score_get(ID)