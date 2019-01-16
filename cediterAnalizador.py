#!/usr/bin/env python
import serial, minimalmodbus, MySQLdb
from time import sleep, strftime, localtime, time
# meterID
idestacion = "1"
# Power Analizer ModBus Registers
rV_U  = 37 
rV_V  = 38 
rV_W  = 39 

rV_UV = 40  
rV_VW = 41  
rV_WU = 42  

rI_U  = 43 
rI_V  = 44 
rI_W  = 45 

rP_U  = 46 
rP_V  = 47 
rP_W  = 48 
rP_T  = 49 

rQ_U  =  50
rQ_V  =  51
rQ_W  =  52
rQ_T  =  53

rPF_U =  54 
rPF_V =  55 
rPF_W =  56 
rPF_T =  57 

rS_U  =  58
rS_V  =  59
rS_W  =  60
rS_T  =  61

rFrec =  62

rWWP = [63, 64]
rWPN = [65, 66]
rWQP = [67, 68]
rWQN = [69, 70]
rEPP = [71, 72]
rEPN = [73, 74]
rEQP = [75, 76]
rWQN = [77, 78]

# Modbus configuration Options
instrument = minimalmodbus.Instrument('/dev/ttyUSB0',12) # port name, slave address (in decimal)
#instrument.debug = True
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity   = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 1  # seconds
instrument.mode = minimalmodbus.MODE_RTU 

# DB Configuration parameters
DBhost = "cediter.com"
DBpass = "some_pass"
DBuser = "phpmyadmin"
DBport = "3306"
DBdb   = "sisconectividad"
DBtable= "datos"

# DB Configuration parameters
filedir = "/home/pi/meterData.csv"
filedata = open(filedir, "a") 

def connDB():
	global conn
	global cur
	try:
		conn = MySQLdb.connect(DBhost,DBuser,DBpass,DBdb)
		cur = conn.cursor()
		print "...DB connected"
	except:
		print "...DB ERROR"
		pass

def insertDB():
	global fechahora
	global voltaje
	global corriente
	global potactiva
	global potreactiva
	global potaparente
	global factpotencia
	global frecuencia
	global energia

	c_insert="""
	INSERT INTO %s(idestacion, fechahora,
	voltaje,corriente,potactiva,potreactiva,potaparente,
	factpotencia,frecuencia,energia)
	VALUES ('%s', '%s','%5.2f','%5.2f','%5.2f','%5.2f','%5.2f',
		'%5.2f','%5.2f','%5.2f');
	"""%(DBtable,idestacion,fechahora,voltaje,corriente,potactiva,potreactiva,potaparente,
		factpotencia,frecuencia,energia)
	#print c_insert
	try:
		cur.execute(c_insert)
		conn.commit()
	except:
		print "... insert ERROR"
		connDB()
		pass

def readreg(reg,dec):
	# Function to read a MODBUS register
	while True:
		sleep(0.1)
		try:
			return instrument.read_register(reg, dec)
			
		except:
			pass	
			
def dataver():
	if frecuencia > 40 and frecuencia < 80:
		if factpotencia > 0.1 and factpotencia < 1.1:
			return True
	return False


def readdata():
	# Function to read all requested data
	global fechahora
	global voltaje
	global corriente
	global potactiva
	global potreactiva
	global potaparente
	global factpotencia
	global frecuencia
	global energia
	global filedata

	fecha = strftime('%Y-%m-%d',localtime())
	hora = strftime('%H:%M:%S',localtime())

	fechahora = "%s %s"%(fecha, hora)
	for i in range(5): 
		voltaje			= readreg(rV_UV, 1)
		corriente		= readreg(rI_U,  1)
		potactiva 		= readreg(rP_U,  1)
		potreactiva 	= readreg(rQ_U,  1)
		potaparente 	= readreg(rS_U,  1)
		factpotencia	= readreg(rPF_U, 3)
		frecuencia 		= readreg(rFrec, 2)
		wwp1 			= readreg(rWWP[0],  1) # Registernumber, number of decimals
		wwp2 			= readreg(rWWP[1],  1) # Registernumber, number of decimals
		energia 		= wwp1*wwp2
		if dataver():
			break

	filedata.write(("%s,%5.2f,%5.2f,%5.2f,%5.2f,%5.2f,%5.2f,%5.2f,%5.2f\n")%(fechahora,voltaje,corriente,potactiva,potreactiva,potaparente,factpotencia,frecuencia,energia))

	print " "
	print "%s"%fechahora
	print "voltaje:", voltaje
	print "corriente:", corriente
	print "potactiva:", potactiva
	print "potreactiva:", potreactiva
	print "potaparente:", potaparente
	print "factpotencia:", factpotencia
	print "frecuencia:", frecuencia
	print "energia:", energia
	
	print "w1, w2:", wwp1, wwp2

def checktime(sec):
	# Function to trigger the readdata funtion from "sec" to "sec"
	while True:
		res = round(time()%sec)
		if res==0.0:
			readdata()
			insertDB()
		sleep(0.2)

connDB()
while True:
	checktime(10)

