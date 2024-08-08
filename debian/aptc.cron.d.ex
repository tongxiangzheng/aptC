#
# Regular cron jobs for the aptc package
#
0 4	* * *	root	[ -x /usr/bin/aptc_maintenance ] && /usr/bin/aptc_maintenance
