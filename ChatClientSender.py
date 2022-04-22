#sender
from socket import *
import sys
import time
import re
import hashlib

bufferSize = 1024
timeout = 1.0

def alloc_args(numArgs1, numArgs2):
	""" Returns arg 4-tuple"""
	length = len(sys.argv)
	if (length != numArgs1) & (length != numArgs2):
		print("Recieved {}  arg(s)".format(length))
		sys.exit()
	server_name = ""
	port_number = ""
	filename = ""
	new_filename = ""
	i = 1
	while i < length:
		add_by = 2
		apple = sys.argv[i]
		match apple:
			case "-s":
				server_name = sys.argv[i+1]
			case "-p":
				port_number = sys.argv[i+1]
			case "-t":
				filename = sys.argv[i+1]
				new_filename = sys.argv[i+2]
				i = i + 1
			case _:
				print("{} didn't match".format(sys.argv[i]))
				sys.exit()
		i = i + add_by
	print(server_name, port_number, filename, new_filename)
	return server_name, int(port_number), filename, new_filename	

def basedOnSpecification(filename, new_filename):
	if not filename and not new_filename:
		 return sys.stdin.readline()

def tryRcv(bitMsg):
	global bufferSize
	global timeout
	msg = ""
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	
	while True:
		clientSocket.sendto(bitMsg, (server_name, port_number))
		clientSocket.settimeout(timeout)
		try:
			msg, server = clientSocket.recvfrom(bufferSize)
			print(f'tryRcv : Message from Server: {msg} \n')
		except:
			print('tryRcv : REQUEST TIMED OUT')
			clientSocket.close()
			return msg
		else:
			break
	clientSocket.close()
	return msg

def getRcv(bitMsg):
	msg = ""
	while msg == "":
		msg = tryRcv(bitMsg)
	return msg

def verifyRcv(msgSEND, shouldRcvStart, typee):
	elapsed = 0
	t0 = time.time()
	while elapsed < 2:
		print("msg sent is -{}-".format(msgSEND))
		rcvd = getRcv(msgSEND)
		if (rcvd.startswith(shouldRcvStart) or rcvd.startswith(b'. ')) and rcvd.endswith(b"\n"):
			return rcvd
		elapsed = time.time() - t0
		print("{} should start with {} or {}".format(rcvd, shouldRcvStart, b'. '))
	print("verifyRcv {}: Still cannot CONN-- Elapsed Time is {}".format(typee, elapsed))
	sys.exit(1)
	return rcvd

# specifying should result in transferring the contents of the local file filename1 correctly to the remote end and stored there as filename2 
# not specifying filename and filename2 should transfer any standard input from the sender to the standard output of the receiver 
#python ChatClientSender.py -s server_name -p port_number (-t filename1 filename2) 
if __name__ == "__main__":
	server_name, port_number, filename, new_filename = alloc_args(5, 8)
	myNAME = "Helenni55"
	theirNAME = "Mariaa55"
	## NOT TESTED ##
	msgNAME = str.encode("NAME " + myNAME)
	msgCONN = str.encode("CONN " + theirNAME)
	msgPERIOD = str.encode(". ")
	msgQUIT = str.encode("QUIT")
	#theirIP = rcved.decode().split(' ')[5]

	rcvMsgNotCONN = str.encode("OK Relaying to {} who is probably offline".format(theirNAME))
	rcvMsgCONN = str.encode("OK Relaying to {} at ".format(theirNAME))
	rcvMsgNAME = str.encode("OK Hello {}".format(myNAME))
	rcvMsgPERIOD = str.encode("OK Not relaying")
	rcvMsgQUIT = str.encode("OK Bye")

	verifyRcv(msgNAME, rcvMsgNAME, "NAME")
	verifyRcv(msgCONN, rcvMsgCONN, "CONN")
	verifyRcv(msgPERIOD, rcvMsgPERIOD, "PERIOD")
	verifyRcv(msgQUIT, rcvMsgQUIT, "QUIT")

	# Sending File || StdInputs			TODO: Design Header: Sequence Number, CheckSum LIBARY, (windowing)  && ACKs , NAKs
	#'HEYO\nSequenceNumber:_\nCheckSum\n\nPAYLOADBODY' // TODO Q : checksum calc on PAYLOADBODY too? what to calculate on?

	# not specifying filename and filename2 like below should transfer any standard input from the sender to the standard output of the receiver, len(filename) == 0		

	md5_hash = hashlib.md5()
	filename1 = "soda.txt"
	filename2 = "filename2"
	seq_num = 3
	f = open(filename1, "r+b")
	# Add header
	header = filename1 + "\n" + filename2 + "\n" + str(seq_num) + "\n"
	print("HEADER")
	print(header.encode())
	segment = header.encode() + b'\n'
	# Read from file
	body = b''
	byte = f.read(1)
	while byte:
		body += byte
		byte = f.read(1)
	print("BODY")
	print(body)
	# Checksum
	md5_hash.update(segment + body)				# update hash object's contents with the file contents
	digest = md5_hash.hexdigest()				# saves the hash into a hexidecimal string
	print("CHECKSUM")
	print(digest.encode())
	datagram = header.encode() + digest.encode() + b'\n\n' + body
	print("FINAL")
	print(datagram)
	# Send to server
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.sendall(datagram.encode())

	print("Finished")
