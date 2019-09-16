#!/usr/bin/python3

import os
import datetime
import sys
import subprocess
import logging as log

def module_exists(module_name):
	try:
		__import__(module_name)
	except ImportError:
		return False
	else:
		return True

# load passwords and other configs (stored separately in a file not tracked by git)
if module_exists("config"):
	import config
else:
	print("Please set up the config.py file. Copy 'sample.config.py' to 'config.py' and modify the default values.")
sys.exit(2)

def main():
	sites = config.sites
	for site in sites:
		run_backup(sites[site])
	send_email()
	return 0

def run_backup(site):
	# 1. rsync all files to local, including the database dump
	print("Acquiring latest backup")
#	rsync_download(site['rsync_dir'], site['local_dir'], site['rsync_user'], site['rsync_host'])

	# 2. upload all web files to tertiary via ftp
	print("Uploading files")
#	ftp_upload(web_root_file_location, ftp_root_file_location, site['ftp_user'], site['ftp_pass'], site['ftp_host'])

	# 3. overwrite database on tertiary
	print("Uploading database")
#	db_overwrite_tertiary(db_dump_file_location, site['schema'], site['db_user'], site['db_pass'], site['db_host'])

# note: must use public/private key authentication. use a .ssh/config file to specify a private key if not using default ssh id_rsa
def rsync_download(remote_latest_backup_location, local_root_file_location, user, host):
	remote_location = user + '@' + host + ":" + remote_latest_backup_location
	rsync_command = ['rsync', '-a', '--delete-during', remote_location, local_root_file_location]
	log.info("Rsyncing files to local machine from " + remote_location)
	subprocess.call(rsync_command)

def ftp_upload(local_root_file_location, ftp_root_file_location, user, password, host):
	ftp_command = ['lftp', '-e', 'mirror -R ' + web_root_file_location + ' ' + ftp_root_file_location, '-u', user + ',' + password, host]
	log.info("Uploading FTP files to " + ftp_root_file_location + " on host " + host)
	subprocess.call(ftp_command)

# takes the standard db dump, prepends drop schema, and uploads via mysql
def db_overwrite_tertiary(db_dump_file, schema, user, password, host):
	db_prepend_drop_schema(db_dump_file, schema)

	mysql_command = ['mysql', '-u' + user, '-p' + password, '-h' + host, '--database=' + schema]
	log.info("Reading in database dump " + db_dump_file)
	with open(db_dump_file) as input_file:
		# redirect the db_dump_file as the input to mysql
		log.info("Running mysql dump commands for schema '" + schema + "' at host '" + host + "'")
		proc = subprocess.Popen(
			mysql_command, stdin = input_file, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
		output,error = proc.communicate()


def db_prepend_drop_schema(db_dump_file, schema):
	# Prepend the database we want to overwrite.
	log.info("Reading in database dump " + db_dump_file)
	with open(dbdump, "r") as original:
		data = original.read()

	log.info("Prepending DROP SCHEMA " + schema + " lines")
	with open(dbdump, "w") as modified:
		modified.write("DROP SCHEMA IF EXISTS ")
		modified.write(schema_name)
		modified.write(";\n")

		modified.write("CREATE SCHEMA ")
		modified.write(schema_name)
		modified.write(";\n")

		modified.write("USE ")
		modified.write(schema_name)
		modified.write(";\n")

		modified.write(data)


def get_date_time():
    date = datetime.datetime.today()
    return date.strftime("%Y-%m-%d_%s")

# send log email saying backups were completed
def send_email():
	SENDMAIL = config.sendmail
	FROM = config.email_from
	TO = config.email_to

	SUBJECT = "Nightly Tertiary Backup"
	TEXT = "The nightly tertiary backup for " + get_date_time() + """ completed. \n\n\
Date: """ + get_date_time()

	message = """\
From: %s
To: %s
Subject: %s

%s
	""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
	p = os.popen("%s -t -i" %SENDMAIL, "w")
	p.write(message)
	status = p.close()
	if status:
		print("Sendmail exit status", status)

main() # run the script

