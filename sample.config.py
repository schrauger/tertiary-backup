sendmail = '/usr/sbin/sendmail'
email_from = 'backups@SERVER.med.ucf.edu'
email_to = ['recipient@email.com']

local_storage_path = '/tmp/website/'		# temporary storage location for script to store latest website backup

sites = {}

#sites['site_med_prd'] = {
#	'rsync_host': "2.3.4.5",		# server with the latest backup copy
#	'rsync_dir': "/var/backups/latest/",	# directory on server with backups
#	'rsync_user': "rsyncuser",		# ssh user with read access to the backups folder - requires public key auth
#	'ftp_host': "1.2.3.4",			# tertiary FTP server
#	'ftp_dir': "/tertiary/directory",	# FTP directory
#	'ftp_user': "FTP_USER",			# FTP username
#	'ftp_pass': "FTP_PASSWORD",		# FTP password
#	'db_host': "1.2.3.5",			# tertiary database server
#	'db_schema': "DB",			# tertiary database schema
#	'db_user': "DB_USER",			# tertiary database username
#	'db_pass': "DB_PASSWORD"		# tertiary database password
#}

sites['site_med_prd'] = {
	'rsync_host': "2.3.4.5",
	'rsync_dir': "/var/backups/{location}/latest/",
	'rsync_user': "rsyncuser",
	'ftp_host': "1.2.3.4",
	'ftp_dir': "/tertiary/directory",
	'ftp_user': "FTP_USER",
	'ftp_pass': "FTP_PASSWORD",
	'db_host': "1.2.3.5",
	'db_schema': "DB",
	'db_user': "DB_USER",
	'db_pass': "DB_PASSWORD"
}
sites['site_med_dev'] = {
	'rsync_host': "2.3.4.5",
	'rsync_dir': "/var/backups/{location_dev}/latest/",
	'rsync_user': "rsyncuser",
	'ftp_host': "1.2.3.4",
	'ftp_dir': "/tertiary/directorydev",
	'ftp_user': "FTP_USERdev",
	'ftp_pass': "FTP_PASSWORDdev",
	'db_host': "1.2.3.5",
	'db_schema': "DBdev",
	'db_user': "DB_USERdev",
	'db_pass': "DB_PASSWORDdev"
}
