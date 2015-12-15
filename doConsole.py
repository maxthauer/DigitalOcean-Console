#!/usr/bin/python3
'''
DigitalOcean account administration script
-Create new droplets & delete existing ones
-List account information, monthly cost and current droplet information
-Show tiers 
-Add, remove and view SSH keys
-Password reset a droplet

Created by Max Thauer

Additional requirements:
pip3 install prettytable
pip3 install requests
-DigitalOcean API token with full account access (read and write)

'''
import requests, time, json
from prettytable import PrettyTable

token = ''


def menu():
	print ("\n#######################################")
	print ("# Welcome to the DigitalOcean Console #")
	print ("#######################################\n")

	print ("Please select an option: ")
	print ("1. List droplets")
	print ("2. Spin up a new droplet")
	print ("3. Delete an existing droplet")
	print ("4. Show tiers")
	print ("5. Display current monthly cost")
	print ("6. Display account information")
	print ("7. List, add or delete SSH keys")
	print ("8. Password reset a droplet")
	print ("9. Exit this console")
	print ("\n")

	userOption = input("Selection: ")
	print ("\n")
	userOption = int(userOption)

	if userOption == 1:
		listDroplets()
	elif userOption == 2:
		newDroplet()
	elif userOption == 3:
		deleteDroplet()
	elif userOption == 4:
		listTiers()
	elif userOption == 5:
		monthlyCost()
	elif userOption == 6:
		accountInfo()
	elif userOption == 7:
		sshOptions()
	elif userOption == 8:
		passwordReset()
	elif userOption == 9:
		exit()	
	else:
		print ("Invalid option, please select an option from the list")
		menu() 


def listDroplets():
	url = requests.get('https://api.digitalocean.com/v2/droplets?page=1&per_page=999', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	i = 0
	print("-----------------------------------\n")
	table = PrettyTable(["Droplet Name", "vCPU's", "Memory", "Disk", "Status", "ID"])
	networkTable0 = PrettyTable(["Droplet Name","IP Address 1", "Netmask 1", "Gateway 1", "Type 1"])
	networkTable1 = PrettyTable(["Droplet Name", "IP Address 2", "Netmask 2", "Gateway 2", "Type 2"])	
	droplets = data['droplets']
	for droplet in droplets:
		dropletId = data['droplets'][i]['id']
		name = data['droplets'][i]['name']
		memory = data['droplets'][i]['memory']
		vcpus = data['droplets'][i]['vcpus'] 
		disk = data['droplets'][i]['disk'] #GB
		status = data['droplets'][i]['status']

		ipV4_0 = data['droplets'][i]['networks']['v4'][0]['ip_address']
		netmaskV4_0 = data['droplets'][i]['networks']['v4'][0]['netmask']
		gatewayV4_0 = data['droplets'][i]['networks']['v4'][0]['gateway']
		netTypeV4_0 = data['droplets'][i]['networks']['v4'][0]['type']

		n = 0 
		ipv4Count = data['droplets'][i]['networks']['v4']
		for droplet in ipv4Count:
			n = n + 1
		n = n - 1
		if n > 0:
			ipV4_1 = data['droplets'][i]['networks']['v4'][1]['ip_address'] 
			netmaskV4_1 = data['droplets'][i]['networks']['v4'][1]['netmask']
			gatewayV4_1 = data['droplets'][i]['networks']['v4'][1]['gateway']
			netTypeV4_1 = data['droplets'][i]['networks']['v4'][1]['type']
		else:
			ipV4_1 = "N/A"
			netmaskV4_1 = "N/A"
			gatewayV4_1 = "N/A"
			netTypeV4_1 = "N/A"

		dropletTotal = data['meta']['total']
		i = i + 1
		table.add_row([name,vcpus,memory,disk,status,dropletId])
		networkTable0.add_row([name,ipV4_0,netmaskV4_0,gatewayV4_0,netTypeV4_0])
		networkTable1.add_row([name,ipV4_1,netmaskV4_1,gatewayV4_1,netTypeV4_1])

		if i == dropletTotal:
			print (table)
			print (networkTable0)
			print (networkTable1)
			print("-----------------------------------\n")
			time.sleep(2)	
			menu()

def newDroplet():
	url = requests.get('https://api.digitalocean.com/v2/images?page=1&per_page=999&type=distribution', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	table = PrettyTable(["Number","Image"])
	if url.status_code == 200:
		i = 0
		x = 0
		imgList = []
		data = url.json()
		total = data['meta']['total']
		images = data['images']
		for image in images:
			imageID = data['images'][i]['id']
			name = data['images'][i]['name']
			distro = data['images'][i]['distribution']
			slug = data['images'][i]['slug']
			details = x,slug
			imgList.insert(x, details)
			table.add_row([x,slug])
			i = i + 1
			x = x + 1
			if i == total:
				print (table)
		selection = input("Enter the number of your desired image: \n")
		selection = int(selection)
		if selection in imgList[selection]:
			image = (imgList[selection][1])
	else:
		print("Status code: {}".format(url.status_code))

	regionTable = PrettyTable(["Name", "Region", "Tiers"])
	i = 0
	url = requests.get('https://api.digitalocean.com/v2/regions', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	regionTotal = data['meta']['total']
	regions = data['regions']
	print("-----------------------------------\n")
	for site in regions:
		siteName = data['regions'][i]['name']
		siteId = data['regions'][i]['slug']
		tiers = data['regions'][i]['sizes']
		available = data['regions'][i]['available']
		i = i + 1
		if available == True:			
			regionTable.add_row([siteName,siteId,tiers])
	print (regionTable)
	regionSelection = input("Please enter a region from the table above: (e.g. sfo1 or nyc3)\n")
	dropletTier = input("Please enter your desired tier fron the table above:  (e.g. 512mb or 64gb)\n")
	hostname = input("Please enter a hostname for your droplet: (e.g. example.com or WEB02)\n")
	useKey =  input ("Would you like to use one of your SSH keys with this droplet?  Y|N\n")
	if useKey == 'Y' or useKey == 'y':
		useKey = 'true'
		keyUrl = requests.get('https://api.digitalocean.com/v2/account/keys', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
		data = keyUrl.json()
		keyTable = PrettyTable(["Name", "ID", "Fingerprint"])
		i = 0
		keyTotal = data['meta']['total']
		keys = data['ssh_keys']
		for key in keys:
			keyId = data['ssh_keys'][i]['id']
			fingerprint = data['ssh_keys'][i]['fingerprint']
			keyName = data['ssh_keys'][i]['name']
			keyTable.add_row([keyName,keyId,fingerprint])
			i = i + 1
			if i == keyTotal:
				print (keyTable)
		keySelection = input("Please enter the Fingerprints of the keys you would like to use, each separated by a space: \n")
		keySelection = keySelection.split()
	elif useKey == 'N' or useKey == 'n':
		keySelection = False
	else:
		print("Invalid option, returning to start of new droplet creation\n")
		time.sleep(2)
		newDroplet()

	enableIPv6 = input("Would you like to enable IPv6?  Y|N \n")	
	if enableIPv6 == 'Y' or enableIPv6 == 'y':
		enableIPv6 = 'true'
	elif enableIPv6 == 'N' or enableIPv6 == 'n':
		enableIPv6 = 'false'
	else:
		print("Invalid option, returning to start of new droplet creation\n")
		time.sleep(2) 
		newDroplet()

	enablePN = input("Would you like to enable private networking?  Y|N \n")
	if enablePN == 'Y' or enablePN == 'y':
		enablePN = 'true'
	elif enablePN == 'N' or enablePN == 'n':
		enablePN = 'false'
	else:
		print("Invalid option, returning to start of new droplet creation\n")
		time.sleep(2)	
		newDroplet()

	payload = {"name":''+hostname+'',"region":''+regionSelection+'',"size":''+dropletTier+'',"image":''+image+'',
		"backups": 'false',
		"ipv6": ''+enableIPv6+'',
		"user_data": 'null',
		"ssh_keys": keySelection,
		"private_networking": ''+enablePN+''}

	dropletCreateUrl = requests.post('https://api.digitalocean.com/v2/droplets', 
		headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token}, 
		data=json.dumps(payload))
	print (payload)
	print (dropletCreateUrl.text)
	if dropletCreateUrl.status_code == 202:
		print ("Now creating droplet with the following parameters\n")
		data = dropletCreateUrl.json()

		dID = data['droplet']['id']
		name = data['droplet']['name']
		memory  = data['droplet']['memory']
		vcpus = data['droplet']['vcpus']
		disk = data['droplet']['disk']
		createTime = data['droplet']['created_at']
		print ("Name: {} | Droplet ID: {}\nvCPU's: {} | Memory: {} | Disk: {}GB\nCreated at: {}\n".format(name,dID,vcpus,memory,disk,createTime))
		print ("Droplet should be available within the next minute.\n")
		menu()
	else:
		print ("Invalid paramters, returning to start of new droplet creation\n")
		time.sleep(2)	
		newDroplet()

def deleteDroplet():
	url = requests.get('https://api.digitalocean.com/v2/droplets?page=1&per_page=999', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	i = 0
	print("-----------------------------------\n")
	droplets = data['droplets']
	for droplet in droplets:
		dropletId = data['droplets'][i]['id']
		name = data['droplets'][i]['name']
		dropletTotal = data['meta']['total']
		i = i + 1
		print("Droplet Name: {} | Droplet ID: {}\n".format(name,dropletId))

	dropletSelection = input("Please enter the Droplet ID of the droplet\nyou would: like to delete (e.g. 3164494)\n")
	url = requests.delete('https://api.digitalocean.com/v2/droplets/'+dropletSelection+'\'', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	if url.status_code == 204:
		print ("\nDroplet deletion request was successful. Please wait a minute.\n")
		menu()
	else:
		print ("\nInvalid deletion request. Returning to menu.\n")
		menu()	

def listTiers():
	url = requests.get('https://api.digitalocean.com/v2/sizes', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	i = 0
	table = PrettyTable(["Tier", "vCPU's", "Memory", "Disk", "Transfer(TB)", "$/Month", "$/Hour","Available"])
	regionTotal = data['meta']['total']
	sizes = data['sizes'][i]
	print("-----------------------------------\n")
	for region in sizes:
		slug = data['sizes'][i]['slug']
		memory = data['sizes'][i]['memory']
		vcpus = data['sizes'][i]['vcpus']
		disk = data['sizes'][i]['disk']
		transfer = data['sizes'][i]['transfer']
		ppM = data['sizes'][i]['price_monthly']
		ppH = data['sizes'][i]['price_hourly']
		regions = data['sizes'][i]['regions']
		available = data['sizes'][i]['available']
		i = i + 1
		table.add_row([slug,vcpus,memory,disk,transfer,ppM,ppH,available])
		if i == regionTotal:
			print(table)
			menu()

def monthlyCost():
	url = requests.get('https://api.digitalocean.com/v2/droplets?page=1&per_page=999', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	# this assumes users pay $5 per 512MB, lines up with base account plans
	i = 0
	memTotal = 0
	droplets = data['droplets']
	for droplet in droplets:
		dropletTotal = data['meta']['total']
		memory = data['droplets'][i]['memory']
		i = i + 1
		memTotal = memTotal + memory 	
		if i == dropletTotal:
			print("-----------------------------------\n")
			print ("Currently running {} droplets".format(i))
			totalCostMonth = memTotal * 0.009765625
			# price hourly = memory total / 68817.204301    (number = mb/hourly price)
			totalCostHr = (memTotal/68817.204301)
			totalCostHr = round(totalCostHr,5)
			print ("Total cost per:")
			print ("Month: ${} | Hour: ${}\n".format(totalCostMonth,totalCostHr))
			print("-----------------------------------\n")
			menu() 
		
def accountInfo():
	url = requests.get('https://api.digitalocean.com/v2/account', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	for account in data:
		dropletLimit = data['account']['droplet_limit']
		ipFloatLimit = data['account']['floating_ip_limit']
		email = data['account']['email']
		uuid = data['account']['uuid']
		verified = data['account']['email_verified']
		status = data['account']['status']
		statusMsg = data['account']['status_message']
		print("-----------------------------------\n")
		print("\nEmail Address: {}\nUUID: {} \nDroplet Limit: {} | Floating IP Limit: {}\nEmail Verified: {}\nAccount Status: {}\nAccount Message: {}\n".format(email,uuid,dropletLimit,ipFloatLimit,verified,status,statusMsg))
		print("-----------------------------------\n")
	menu() 

def sshOptions():
	keyUrl = requests.get('https://api.digitalocean.com/v2/account/keys', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = keyUrl.json()
	i = 0
	keyTable = PrettyTable(["Name", "ID", "Fingerprint"])
	keyTotal = data['meta']['total']
	keys = data['ssh_keys']
	for key in keys:
		keyId = data['ssh_keys'][i]['id']
		fingerprint = data['ssh_keys'][i]['fingerprint']
		keyName = data['ssh_keys'][i]['name']
		keyTable.add_row([keyName,keyId,fingerprint])
		i = i + 1
		if i == keyTotal:
			print ("Current Keys:\n")
			print (keyTable)
	addDelKey =  input("Would you like to add a key [A]\nDelete a key [D]\nReturn to main menu [M]\n")
	if addDelKey == 'A' or addDelKey == 'a':
		keyName = input ("Enter a name for the new key: \n")
		key = input ("Please paste your key here: \n")
		payload = {"name":""+keyName+"","public_key":""+key+""}
		url = requests.post('https://api.digitalocean.com/v2/account/keys', 
		headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token}, 
		data=json.dumps(payload))
		if url.status_code == 201:
			print ("Key sucessfully added.\n")
			time.sleep (2)
			sshOptions()
		else:
			print ("Invalid parameters, returning to start of SSH options:\n")
			time.sleep(2)
			sshOptions()
	elif addDelKey == 'D' or addDelKey == 'd':
		keySelection = input ("Please paste the fingerptint of your key here: \n")
		url = requests.delete('https://api.digitalocean.com/v2/account/keys/'+keySelection, 
		headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
		if url.status_code == 204:
			print ("Key sucessfully deleted.\n")
			time.sleep (2)
			sshOptions()
		else:
			print ("Invalid parameters, returning to start of SSH options:\n")
			time.sleep(2)
			sshOptions()
	elif addDelKey == 'M' or addDelKey == 'm':
		menu()
	else:
		print("Invalid option, returning to main menu\n")
		time.sleep(2)	
		menu()

def passwordReset():
	url = requests.get('https://api.digitalocean.com/v2/droplets?page=1&per_page=999', headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token})
	data = url.json()
	i = 0
	print("-----------------------------------\n")
	droplets = data['droplets']
	for droplet in droplets:
		dropletId = data['droplets'][i]['id']
		name = data['droplets'][i]['name']
		dropletTotal = data['meta']['total']
		i = i + 1
		print("Droplet Name: {} | Droplet ID: {}\n".format(name,dropletId))

	dropletSelection = input("Please enter the Droplet ID of the droplet\nwhose password you would like to reset (e.g. 3164494)\n")
	payload = {"type":"password_reset"}
	pwResetUrl = requests.post('https://api.digitalocean.com/v2/droplets/'+dropletSelection+'/actions', 
		headers={'Content-Type': 'application/json','Authorization': 'Bearer '+token}, 
		data=json.dumps(payload))
	if pwResetUrl.status_code == 201:
		print ("\nReset successfully initiated. Please check your email.\n")
		menu()
	else:
		print ("Invalid droplet ID, returning to menu")
		menu()

menu()

