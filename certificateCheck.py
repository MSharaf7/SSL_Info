'''

# Author: Marwan Sharaf
# Date: 5/07/2021

Read list of domains from file, 
Check SSL expiry date,
Return CSV file including: Domain, Expiry Date, and Days Left


'''

import socket
import ssl
import datetime
import pandas as pd
from urllib.parse import urlparse


domains_url = []
with open("domains.txt") as f:
    domains_url  = f.readlines()
domains_url  = [x.strip() for x in domains_url]



def ssl_expiry_datetime(hostname):
	ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'

	context = ssl.create_default_context()
	context.check_hostname = False

	conn = context.wrap_socket(
		socket.socket(socket.AF_INET),
		server_hostname=hostname,
	)
	# 10 second timeout
	conn.settimeout(10.0)

	conn.connect((hostname, 443))
	ssl_info = conn.getpeercert()
	# Python datetime object
	return datetime.datetime.strptime(ssl_info['notAfter'], ssl_dateformat)

if __name__ == "__main__":
	
	domains = []
	dates = []
	daysLeft = []

	for value in domains_url:
		domains.append(value)
		now = datetime.datetime.now()
		try:
			expire = ssl_expiry_datetime(value)
			diff = expire - now
			dates.append(expire.strftime("%d/%m/%Y"))
			daysLeft.append(diff.days)
			print ("Domain name: {} \nExpiry Date: {} \nDays till Expire: {} days\n".format(value,expire.strftime("%d/%m/%Y"),diff.days))

		except Exception as e:
			dates.append(e)
			daysLeft.append(None)
			print ("Domain name: {} \n".format(value), e, "\n")
	
	data = {"Domain Name": domains, "Expiry Date": dates, "Days Left": daysLeft}
	print(data)
	df = pd.DataFrame(data)

	# Write to CSV file:
	df.to_csv('SSL_Info.csv')


