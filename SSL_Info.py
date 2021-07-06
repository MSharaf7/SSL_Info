'''

# Author: Marwan Sharaf
# Date Created: 5/07/2021
# 

Requirements:
- Python3
- install pandas module
- install pyopenssl module
- Each url/domain should be in its own line

Read list of domains/URLs from a text file,
Check SSL expiry date,
Return CSV file including: Domain, Expiry Date, and Days Left


# Version: 1.1
# Date: 6/07/2021

Port Number can now be read in the format domain:port
If no port number is available, default to port 443


# Version: 1.2
# Date: 6/07/2021

Certificate Issuer and Issued to are now returned


# Version 1.3
# Date: 6/07/2021

Can now read URLs and return results



'''

import socket
import ssl
import datetime
import pandas as pd
from urllib.parse import urlparse


domains_url = []
ports = []


# number of seconds until timeoout
delay = 10

# make sure file name is the same as file being read
with open("domains2.txt") as f:
	
	#Remove protocol from URL
	for line in f:
		line = line.lower()

		if line[0:5] == 'https':
			line = line[8:len(line)]
		if line[0:4] == 'http':
			line = line[7:len(line)]

		#Split domain and port number
		currLine = line.split(":",1)
		domains_url.append(currLine[0])
		try: 
			ports.append(currLine[1])
		except:
			ports.append("443")

#Clean up domains
domains_url = [x.strip() for x in domains_url]
domains_url = [x.split('/',1)[0] for x in domains_url]

#Clean up port number
ports = [x.strip() for x in ports]
ports = [x.split('/',1)[0] for x in ports]
ports = [int(x) for x in ports]

#Return SSL Information
def ssl_information(hostname, portNum):
	ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'

	context = ssl.create_default_context()
	context.check_hostname = False

	conn = context.wrap_socket(
		socket.socket(socket.AF_INET),
		server_hostname=hostname,
	)

	conn.settimeout(delay)

	conn.connect((hostname, port))
	ssl_info = conn.getpeercert()
	
	return ssl_info

def ssl_expiry_datetime(ssl_info):
	ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'
	return datetime.datetime.strptime(ssl_info['notAfter'], ssl_dateformat)


def ssl_issuer(ssl_info):
	for issuerName in ssl_info['issuer']:
		if issuerName[0][0] == 'commonName':
			return issuerName[0][1]

def ssl_issued_to(ssl_info):
	for org in ssl_info['subject']:
		if org[0][0] == 'organizationName':
			return org[0][1]


if __name__ == "__main__":
	
	dates = []
	daysLeft = []
	certIssue = []
	issuedTo = []


	for value, port in zip(domains_url, ports):
		now = datetime.datetime.now()
		try:
			info = ssl_information(value, port)
			expire = ssl_expiry_datetime(info)
			issuer = ssl_issuer(info)
			issTo = ssl_issued_to(info)

			diff = expire - now

			dates.append(expire.strftime("%d/%m/%Y"))
			daysLeft.append(diff.days)
			certIssue.append(issuer)
			issuedTo.append(issTo)

			print ("Domain name: {} \nPort Number: {} \nCertificate Issuer: {} \nIssued To: {} \nExpiry Date: {} \nDays till Expire: {} days\n"
				.format(value,port,issuer,issTo,expire.strftime("%d/%m/%Y"),diff.days))

		except Exception as e:
			dates.append(e)
			daysLeft.append(None)
			certIssue.append(None)
			issuedTo.append(None)
			print ("Domain name: {} \nPort Number: {}\n".format(value, port), e, "\n")
	
	data = {"Domain Name": domains_url, "Port Number": ports, "Certificate Issuer": certIssue, "Issued To": issuedTo, "Expiry Date": dates, "Days Left": daysLeft}
	
	print(data)
	
	df = pd.DataFrame(data)

	# Write to CSV file:
	filename = "SSL_Info_" + datetime.datetime.now().strftime("%d:%m:%Y__%Hh%Mm%Ss.csv")  
	df.to_csv(filename)


