#!/usr/bin/python
#This script is being designed to cleanup an NMAP produced text file and insert it into mysql

import sys, os
import re
import MySQLdb
from BeautifulSoup import BeautifulSoup, NavigableString


#####Global variables

last_line = '---'  #if you reach this line, treat previous lines as a single block
scratch_file = "sit_new"
#nmap_output is the file which nmap will be piped to
nmap_output = "SIT_nmap"

#When the flag is set to 0 the script will begin to read
#When the flag is set to 1, the script knows that this is being designated as the last line
flag = 1

# Open the connection to the database
database_connection = MySQLdb.connect('localhost', 'root', 'test', 'nmap');
cursor = database_connection.cursor()
##########################################################################



def createNmap():
    
    
    #Run the nmap command with the option to querry the host OS
    os.system("nmap -O 10.81.5.46 10.81.5.47 10.81.5.48 10.81.5.54 10.81.5.76 172.21.4.148 > '%s'" % str(nmap_output))    
    nmap_unformatted = open(nmap_output, "rw+").readlines()
    #Words to exclude
    word1 = "up"
    word3 = "Starting"
    word4 = "done"
    word5 = "Not"
    word6 = "MAC"
    word7 = "Device"
    word8 = "Network"
    word9 = "detection"
    word0 = "All 1000"

#Here I am redirecting standard out to the scratch file
#So that the info can be more easily managed
    old_stdout = sys.stdout
    sys.stdout = open(scratch_file, "w+")
    for line in nmap_unformatted:
        if word1 not in line and word3 not in line and word5 not in line and word6 not in line and word7 not in line and word8 not in line and word9 not in line and word0 not in line:
     #replace the blank lines with dashes so that they are easier to parse
            if line.isspace():
                print "---"
            else:
                print line.strip()
    #Put the stardard out back to normal
    sys.stdout = old_stdout
##########################################################################    
def parse_dns():
    text = open(scratch_file, "rw+").readlines()
    #filter out the hostname expecting user.company.com
    hostname = re.compile(r'[\w\-][\w\-\.]+.corp.dom')
    #filter out the IP, expecting a 192 address
    ip = re.compile(r'\d+.\d+.\d+.\d+')
    
    computer_id = 1
    #go through the text line by line
    ip_address_list = []
    host_name_list = []
    for word in text:        
        find_ip = ip.findall(word)
        find_ip = " ".join(find_ip)   
        find_hostname = hostname.findall(word)
        find_hostname = " ".join(find_hostname)
        #if the hostname and the IP are blank pass
        if str(find_hostname) == "" and find_ip == "":
            pass
        #If the hostname is not in dns but it has an ip, insert the information into the ip table    
        elif find_hostname == "" and find_ip != "":
            computer_id +=1 
            print "inserting :", find_ip         
            ip_address_list.append(find_ip)
            host_name_list.append("Not Available")
        #This statement assumes that both the dns name and ip are parsed properly and it adds this information to the proper table
        else:
            print "inserting :", find_hostname
            host_name_list.append(find_hostname)
            ip_address_list.append(find_ip)
            computer_id +=1
    
    counter = 0
    #Use the length of the ip_address_list to determine the number of loops to run to add to database

    while counter < len(ip_address_list):
	cursor.execute("SELECT `auto_increment` FROM INFORMATION_SCHEMA.TABLES WHERE table_name ='Computer_Info'")
	aicount = cursor.fetchone()
        ID = aicount[0]
        print "Adding OS ID: ", ID, " IP Address: ", ip_address_list[counter], " and Host Name: ", host_name_list[counter]
        cursor.execute("INSERT INTO Computer_Info(Computer_ID, DNS_Name, Computer_IP_Address, OS_ID) values('%s','%s','%s', '%s')" % (ID, host_name_list[counter], ip_address_list[counter], ID))
        cursor.execute("INSERT INTO Computer_Ports(Computer_ID, Port_ID) values('%s', '%s')" % (ID, ID))
        counter +=1
        
#########################################################################    
def parse_ports():
    
        ###############Parse known ports from the IANA list ####################
    #open the xml file for reading
    ports_xml = open("port_numbers.xml", "w+")
    search_xml = BeautifulSoup(ports_xml) 

    #This tells beautiful soup to pull out only the name tag 
    search_unassigned_numbers = search_xml.findAll('record')
    #The file contains stuff we dont want (unassined and reserved ports)
    #This list contains the known ports that we want
    filtered_entries = []

    #append the appropriate ports to the filtered_entries list
    for entries in search_unassigned_numbers:
        entries = str(entries)
        if "Unassigned" in entries or "Reserved" in entries:
            pass
        else:
            filtered_entries.append(entries)

    #Turn the list into text so that Beautiful soup can use it
    filtered_entries = "".join([x for x in filtered_entries])

    #Change the soup tags so that it is searching the filtered entries
    search_xml = BeautifulSoup(filtered_entries)
    search_port = search_xml.findAll('record')

    #set the list for the port_descriptions
    port_description = []


    port_names = re.compile(r'<name>.*</name>')
    counter = 0
    #while counter < len(port_number):
    for ports in search_port:
        ports = str(ports)
        find_ports = port_names.findall(ports)    
        find_ports = " ".join(find_ports)
        if "name" in find_ports:

            find_ports = find_ports.replace("<name>", "").replace("</name>", "")
            print find_ports
            port_description.append(find_ports)
        else:
            port_description.append("")
        
    #set the list for the port numbers
    port_number = []
    port_names = re.compile(r'<number>.*</number>')
    counter = 0
    for ports in search_port:
        ports = str(ports)
        find_ports = port_names.findall(ports)    
        find_ports = " ".join(find_ports)
        if "number" in find_ports:
            #remove the tags and leave only the port numbers going into the list
            find_ports = find_ports.replace("<number>", "").replace("</number>", "")
            print find_ports
            port_number.append(find_ports)
        else:
            port_number.append("") 


    protocol_name = []

    protocol_names = re.compile(r'<protocol>.*</protocol>')
    counter = 0
    for protocol in search_port:
        ports = str(ports)
        find_ports = port_names.findall(ports)    
        find_ports = " ".join(find_ports)
        if "protocol" in find_ports:
        #remove the tags and leave only the protocol names going into the list

            find_ports = find_ports.replace("<protocol>", "").replace("</protocol>", "")
            protocol_name.append(find_ports)
        else:
            protocol_name.append("")

        #############Begin parsing nmap###################
    port_list = []
    nmap_file = open(scratch_file)
    for line in nmap_file:
        if line.startswith('Nmap'):
            flag = 0
        if last_line in line:
            flag = 1
        if not flag and not last_line in line:
            #append the line to the list and strip the dashes away
            port_list.append(line.strip('---').rstrip())
    
    #set the computer_id to 0. The computer_id represents the ID of the computer
    #each port can have the same ID. In this way ports 80, 22, 443 etc all reference computer by ID
    cursor.execute("SELECT `auto_increment` FROM INFORMATION_SCHEMA.TABLES WHERE table_name ='Computer_Info'")
    cmpid = cursor.fetchone()
    computer_id = cmpid[0] - 1
    existing_ports = []

    for ports_open in port_list:
        starts_with_digit = re.match(r"[0-9]", ports_open) is not None
        parse_os(computer_id);
        #For the ports section we dont want anything that starts with a letter
        #If the line starts with a digit, parse out only the port number
        if starts_with_digit == True:
            ports_open = ports_open.split('/')[0]
            print "Inserting: ", ports_open
            existing_ports.append(ports_open)
            cursor.execute("INSERT INTO Ports_Table(Comp_ID, Port_Number) values('%s','%s')" % ( computer_id, ports_open))
            database_connection.commit()

            continue
        #If the line starts with Port, increase the computer_id. Nmap lists the PORT heading only once per computer
        #Therefore it is a reliable way to indicate the ID of a new computer
        elif starts_with_digit == False and "Nmap" in ports_open:
            computer_id +=1
        elif "All 1000" in ports_open:
            print "no ports open at ID ", computer_id
            ports_open = 0
            cursor.execute("INSERT INTO Ports_Table(Comp_ID, Port_Number) values('%s','%s')" % (computer_id, ports_open))
    #Loop through the open ports on your network and only add port descriptions of ports which exist on your network
    #This was done to reduce querry time against the list of known ports
    x = 0
    while x < len(port_number):
        if port_number[x] in existing_ports:
            print "adding ", port_number[x], port_description[x], protocol_name[x], " to the database"
            cursor.execute("INSERT INTO Port_Description(Port_Number, Port_Description, Port_Protocol) values('%s', '%s', '%s')" % (port_number[x], port_description[x], protocol_name[x]))
        else:
            print "This port is not found among the open ports on your network.... OMITTING"
        x +=1

#######################################################################   
def parse_os(computerid):
    OS_list = []
    nmap_file = open(scratch_file)
    for line in nmap_file:
        if line.startswith('Nmap'):
            flag = 0
        if last_line in line:
            flag = 1
        if not flag and not last_line  in line:
            #append the line to the list and strip the dashes away
            OS_list.append(line.strip('---').rstrip())
    #set the computer_id to 0. The computer_id represents the ID of the computer
    #Each computer will only have a single OS at the time of scanning. Link the ID to the OS
    computer_id = 0
    for host_os in OS_list:
        starts_with_digit = re.match(r"[0-9]", host_os) is not None
        #If the line starts with a digit, skip it and look for the OS information
        if starts_with_digit == True:
            continue
        #If the line starts with Port, increase the computer_id. Nmap lists the PORT heading only once per computer
        #Therefore it is a reliable way to indicate the ID of a new computer
        elif "Nmap" in host_os:
            computer_id +=1
        elif "OS" in host_os and "OS:" not in host_os and "Warn" not in host_os and "Running"not in host_os and "Agg" not in host_os and "Microsoft" not in host_os :
            host_os = host_os.strip("OS details: ")
            if "No" in host_os or "Too many" in host_os:
                host_os = "Not available"
                print "Not available"
                cursor.execute("INSERT INTO OS_Table(OS_Name,Comp_id) values('%s','%s')" % (host_os, computerid))
            else:
                host_os = host_os.split(",")
                print "Inserting: ", host_os[0]
                cursor.execute("INSERT INTO OS_Table(OS_Name,Comp_id) values('%s','%s')" % (host_os[0], computerid) )
        elif "Microsoft" in host_os and "OS" not in host_os and "JUST" not in host_os:
            host_os = host_os.split("Running: ") 
            print "Inserting: ", host_os[1]
            cursor.execute("INSERT INTO OS_Table(OS_Name,Comp_id) values('%s', '%s')" % (host_os[1], computerid))
##############################################################################
createNmap()

compid = parse_ports()
parse_dns()
#parse_os(compid)
#close the database connection
database_connection.commit()
cursor.close()
database_connection.close()
#clean up after yourself
#os.remove(scratch_file)
#os.remove(nmap_output)
