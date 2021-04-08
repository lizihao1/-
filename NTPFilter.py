from scapy.all import *
import thread

rawData = "\x17\x00\x03\x2a" + "\x00" * 80

Inputfile = open('ntp.txt', 'r')

OutputFile = open('NTPServers.txt', 'a')
def detect():

  DetectedResult = sniff(filter="udp port 50001 and dst net 47.92.137.85", store=0, prn=filterer)
def filterer(packet):
 
  if len(packet) > 200:
    if packet.haslayer(IP):
      print packet.getlayer(IP).src

      OutputFile.write(packet.getlayer(IP).src + '\n')
thread.start_new_thread(detect, ())

for address in Inputfile:
  send(IP(dst=address)/UDP(sport=50001, dport=123)/Raw(load=rawData))
print 'End'