# tertiary-backup
COM website utility to push files and db to tertiary backup. This should be set up in a cron job to run nightly after the primary servers' nightly backups are complete.

Run this on a machine that has ssh access to both the primary server and the tertiary server. Use ssh public/private key authentication, and set up any ports or other configs in `.ssh/config`.

Copy `sample.config.py` to `config.py` and modify values.

`sendmail = '/usr/sbin/sendmail'` # Location of sendmail program. Used to send notifications of successful backup
`email_from = 'backups@SERVER.med.ucf.edu'` # Email FROM
`email_to = ['recipient@email.com']` # Array of recipients

`local_storage_path = '/tmp/website/'` # Temporary storage location for script to store latest website backup

`sites['`descriptive_slug`'] = {` # array holding all the sites we want to grab from primary and push to tertiary
* `rsync_host: ""` # IP or domain name for the primary server
* `rsync_dir: ""`  # Absolute path to the latest backup, containing a `web` and `db` folder
* `rsync_user: ""` # User account used to connect via ssh. Note, password authentication is not supported, so use the default id_rsa ssh key.
* `ftp_host: ""` # IP or domain name for the tertiary server that hosts the files
* `ftp_dir: ""` # Absolute path to the hosting location for tertiary server files
* `fpt_user: ""` # Username connecting via FTP
* `ftp_pass: ""` # Plaintext password to connect via FTP
* `db_host: ""` # IP or domain name ofr the tertiary server that hosts the SQL database
* `db_schema: ""` # Name of the database to connect to
* `db_user: ""` # Username connecting to SQL database
* `db_pass: ""` # Password connecting to SQL database
`}`
