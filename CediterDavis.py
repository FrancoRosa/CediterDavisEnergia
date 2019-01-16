# This code reads values from the davis station conected to sertain serial port
import serial
from time import sleep
stport ='COM3'
stbaud = 19200
sttimeout = 1.0

stcommand = 'LOOP 1\r'
#stcommand = 'TEST\r'

#DataIndex Acording to Davis Protocol

iBarometer 		= [ 8, 7]
iOutTemp 		= [13,12]
iWindSpeed 		= [15,14]
iWindDirecction = [17,16]
iRainRate 		= [42,41]
iUV 			= [43]
iSolarRadiation = [45,44]
iRainDay 		= [51,50]
iForecast 		= [90,89]


ser = serial.Serial(stport, stbaud, timeout=sttimeout)

def converter(frame,index):
	result = 0
	for i in index:
		result = result*256+ ord(frame[i])
	return result

def far2cel(far):
	return (far-32)*0.5556

def in2mm(val):
	return val*0.0254


while True:
	ser.write(stcommand)	# Writes the command for asking data
	data = ser.read(150)	# Waits for at least 150 Bytes
	data = data[1:]			# Erace aknoledgement from data frame

	print 'iOutTemp:', far2cel(converter(data,iOutTemp)/10.0)
	print 'iBarometer:', in2mm(converter(data,iBarometer))
	#print 'iWindSpeed:', converter(data,iWindSpeed)
	#print 'iWindDirecction:', converter(data,iWindDirecction)
	#print 'iUV:', converter(data,iUV)
	#print 'iSolarRadiation:', converter(data,iSolarRadiation)
	print 'iRainDay:', converter(data,iRainDay)
	print 'iRainRate:', converter(data,iRainRate)
	print "----"
	sleep(3)

