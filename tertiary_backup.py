#!/usr/bin/python3

import os
import datetime
import sys
import subprocess
import logging as log
import argparse
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
	log.error("Please set up the config.py file. Copy 'sample.config.py' to 'config.py' and modify the default values.")
	sys.exit(2)

# check for verbose
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--debug", help="max output verbosity", action="store_true")
args = parser.parse_args()
if args.verbose:
	log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
	log.info("Verbose output.")
elif args.debug:
	log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
	log.info("Debug output.")
else:
	log.basicConfig(format="%(levelname)s: %(message)s")

#--------------------------------------------------------------------------------------------#

def main():
	sites = config.sites
	for site, site_details in sites.items():
		run_backup(site, site_details, config.local_storage_path)
#	send_email()
	return 0

def run_backup(site_name, site_details, local_storage_path):
	local_site_path = local_storage_path + "/" + site_name + "/"
	# 0. Make sure destination exists.
	log.info("Creating local path")
	mkdir(local_site_path)

	# 1. rsync all files to local, including the database dump
	log.info("Acquiring latest backup")
	rsync_download(site_details['rsync_dir'], local_site_path, site_details['rsync_user'], site_details['rsync_host'])

	# 2. upload all web files to tertiary via ftp
	log.info("Uploading files")
	ftp_mirror(local_site_path + "/web/", site_details['ftp_dir'], site_details['ftp_user'], site_details['ftp_pass'], site_details['ftp_host'])

	# 3. overwrite database on tertiary
	log.info("Uploading database")
	db_overwrite_tertiary(local_site_path + "/db/", site_details['db_schema'], site_details['db_user'], site_details['db_pass'], site_details['db_host'])

	# 4. send email saying tertiary backup is done
	log.info("Sending email")
	send_email()

def mkdir(local_site_path):
	mkdir_command = ['mkdir', '-p', local_site_path]
	log.debug(mkdir_command)
	subprocess.call(mkdir_command)

# note: must use public/private key authentication. use a .ssh/config file to specify a private key if not using default ssh id_rsa
def rsync_download(remote_latest_backup_location, local_root_dir_location, user, host):
	remote_location = user + '@' + host + ":" + remote_latest_backup_location
	if args.debug:
		rsync_command = ['rsync', '-avxP', '--delete-during', '--exclude', 'wp-config.php', remote_location, local_root_dir_location]
	else:
		rsync_command = ['rsync', '-a', '--ignore-errors', '--delete-during', '--exclude', 'wp-config.php', remote_location, local_root_dir_location]
	log.info("Rsyncing files (excluding wp-config.php) to local machine from " + remote_location)
	log.debug(rsync_command)
	subprocess.call(rsync_command)
	delete_wpconfig_command = ['rm', '-f', local_root_dir_location + '/web/wp-config.php']
	log.debug("Removing wp-config.php file if exists")
	log.debug(delete_wpconfig_command)
	subprocess.call(delete_wpconfig_command)

def ftp_mirror(local_web_dir_location, ftp_web_dir_location, user, password, host):
	if args.debug:
		ftp_command = ['lftp', '-c', 'open --user "' + user + '" --password "' + password + '" sftp://' + host + '/; mirror --exclude .git/ --exclude wp-config.php --exclude web.config -e -c --verbose=9 -R -L "' + local_web_dir_location + '" "' + ftp_web_dir_location + '"']
	else:
		ftp_command = ['lftp', '-c', 'open --user "' + user + '" --password "' + password + '" sftp://' + host + '/; mirror --exclude .git/ --exclude wp-config.php --exclude web.config -e -c --verbose=0 -R -L "' + local_web_dir_location + '" "' + ftp_web_dir_location + '"']
#		ftp_command = lftp -c "open --user NET\st508199 --password "APierOpensMyLoaf92#" sftp://production.med.ucf.edu/; mirror -c --verbose=9 -e -R -L /tmp/website/site_med_prd/web/ '/Sites/COM Public/'"
	log.info("Uploading FTP files to " + ftp_web_dir_location + " on host " + host)
	log.debug(ftp_command)
	subprocess.call(ftp_command)

# takes the standard db dump, prepends drop schema, and uploads via mysql
def db_overwrite_tertiary(local_db_dir_location, schema, user, password, host):

	# get sql dump file
	db_dump_file = db_get_dump_filename(local_db_dir_location)

	# prepend sql commands with drop schema
	db_prepend_drop_schema(db_dump_file, schema)

	# upload database dump to tertiary server
	mysql_command = ['mysql', '-u' + user, '-p' + password, '-h' + host, '--database=' + schema]
	log.info("Reading in database dump " + db_dump_file)
	with open(db_dump_file) as input_file:
		# redirect the db_dump_file as the input to mysql
		log.info("Running mysql commands for schema '" + schema + "' at host '" + host + "'")
		proc = subprocess.Popen(
			mysql_command, stdin = input_file, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
		output,error = proc.communicate()

def db_get_dump_filename(local_db_dir_location):
	for file in os.listdir(local_db_dir_location):
		if file.endswith(".sql"):
			sql_dump = os.path.join(local_db_dir_location, file)
			log.info("Found sql dump at " + sql_dump)
			return sql_dump #return path to the first sql file found
	log.error("No .sql file located in " + local_db_dir_location)
	return #no .sql file detected in the directory given

def db_prepend_drop_schema(dbdump, schema):
	# Prepend the database we want to overwrite.
	log.info("Reading in database dump " + dbdump)
	with open(dbdump, "r") as original:
		data = original.read()

	log.info("Prepending DROP SCHEMA " + schema + " lines")
	with open(dbdump, "w") as modified:
		modified.write("DROP SCHEMA IF EXISTS ")
		modified.write(schema)
		modified.write(";\n")

		modified.write("CREATE SCHEMA ")
		modified.write(schema)
		modified.write(";\n")

		modified.write("USE ")
		modified.write(schema)
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
		log.info("Sendmail exit status", status)

main() # run the script

