# Import
tmp_modcur = 0
tmp_modtotal = 11

print('Importing modules...')

import time
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),tmp_modtotal))

import datetime
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),tmp_modtotal))

import random
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),tmp_modtotal))

try:
	import discord
	tmp_modcur+=1
	print('{}/{}...'.format(str(tmp_modcur),tmp_modtotal))
except ModuleNotFoundError:
	print('\'discord\' module wasn\'t found, make sure lilac was started with Python 3.5')
	exit()
import asyncio
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

import db
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

from discord.ext import commands
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

import sys
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

from colorama import init as initcolor
initcolor()
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

from colorama import Fore
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

from colorama import Style
tmp_modcur+=1
print('{}/{}...'.format(str(tmp_modcur),str(tmp_modtotal)))

del tmp_modcur
del tmp_modtotal

# Start
if '-dev' in sys.argv:
	if '-y' in sys.argv:
		choice = 'y'
	else:
		choice = input("Confirm that the bot should start in developer mode (y/n): ")

	if choice == 'y':
		dev=True
		print('Dev mode; starting...')
	else:
		print('Quitting...')
		exit()
else:
	if '-y' in sys.argv:
		choice = 'y'
	else:
		choice = input("Confirm that the bot should start in public mode (y/n): ")

	if choice == 'y':
		dev=False
		print('Public mode; starting...')
	else:
		print('Quitting...')
		exit()

if '-log' in sys.argv:
	log = True
	print('Logging enabled.')
else:
	log = False
	print('Logging disabled.')

db.set_dev(dev)
db.set_log(log)

choice = ''

client = discord.Client()

@client.event
async def on_ready():
	print('====================')
	print('Lilac v2.0.4')
	print('\nLogged in as')
	print(client.user.name)
	print(client.user.id)
	print('Ready!')
	print('====================')

@client.event
async def on_message(message):
	prefixes = ['<@!{}>'.format(client.user.id), '@lilac', 'l,']
	# Shortcut functions for the sake of readability
	def parse(msg):
		return msg.split()

	def checkfor(*matches):
		args = parse(message.content)
		if len(args) > 0: # Sometimes lilac's embeds are detected as empty messages, which throws an IndexError without this line
			if args[0].lower() in prefixes:
				if args[1] in matches:
					return True

	if dev:
		if message.content == 'gen':
			users = list(client.get_all_members())
			for i in users:
				if i.mention.startswith('<@!'):
					continue # Skip bot accounts

				userobj = await client.get_user_info(i.mention[2:-1])
				print(userobj.id)
				print(userobj.name+userobj.discriminator)
				user=userobj.name+userobj.discriminator

				db.create_id_reference(userobj.id,user)


	if checkfor('r', 'return'):
		print('message.content')
		print(message.content)
		print('cleaned message')
		print(message.clean_content)
		await client.send_message(message.channel, "Message returned.")

	if checkfor('scoreboard'):
		await client.send_typing(message.channel)
		await client.send_message(message.channel, "ℹ View all scores here: https://alpha-hedge.github.io/dogspotter-scoreboard")

	if checkfor('help'):
		await client.send_typing(message.channel)
		await client.send_message(message.channel, "ℹ All Lilac commands are here: https://alpha-hedge.github.io/dogspotter-scoreboard/lilac2/index.html")

	# Score commands
	if checkfor('score'):
		# Parse message for processing
		args = parse(message.content)
		# Get user object from mentions
		try:
			userobj = await client.get_user_info(message.raw_mentions[0])
			if userobj.id == client.user.id:
				userobj = await client.get_user_info(message.raw_mentions[1])
		except IndexError:
			if 'me' in args:
				userobj = message.author
			else:
				await client.send_message(message.channel, "⚠ No user tag found.")

		user = userobj.name+userobj.discriminator

		db.user_add(userobj.id,user,userobj.name)

		# reading score
		if args[2] == ('read') or args[2] == ('get'):
			print('\n['+Style.BRIGHT+Fore.BLUE+db.timestamp()+'] message trigger:'+Style.RESET_ALL)
			print(message.clean_content)
			await client.send_typing(message.channel)
			embed = discord.Embed(title="ℹ️ Current User Score", description="Current score of {}:".format(userobj.name), color=0xff00ff)

			embed.set_author(name="Lilac", icon_url='')
			embed.add_field(name="Season:", value=str(db.score_get(userobj.id)['points']), inline=False)
			embed.add_field(name="All-time:", value=str(db.score_get(userobj.id)['allpts']), inline=False)

			await client.send_message(message.channel,embed=embed)
		# changing score
		elif args[2] == 'update' or args[2] == 'change':
			print('\n'+Style.BRIGHT+Fore.BLUE+'['+db.timestamp()+'] message trigger:'+Style.RESET_ALL)
			print(message.clean_content)
			await client.send_typing(message.channel)
			for i in args:
				try:
					amount = int(i)
					break
				except ValueError:
					continue

			before = db.score_get(userobj.id)['points']
			try:
				after = db.score_update(userobj.id,int(amount))['points']

				embed = discord.Embed(title="✅ Score Updated", description="Score of {} was updated.".format(userobj.name), color=0xff00ff)

				embed.set_author(name="Lilac", icon_url='')
				embed.add_field(name="Was:", value=str(before), inline=False)
				embed.add_field(name="Now:", value=str(after), inline=False)

				await client.send_message(message.channel,embed=embed)
			except ValueError:
				await client.send_message(message.channel, "⚠️ No number found in message.".format(amount))
		else:
			await client.send_message(message.channel, "⚠️ No valid command was given after 'score'.")

	if dev:
		if message.content == 'lq':
			print('Quitting...')
			exit()

# Main loop end, begin bot
if dev:
	f = open('devtoken.txt')
	client.run(f.read())

elif not dev:
	f = open('token.txt')
	client.run(f.read())