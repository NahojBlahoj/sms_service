try:
	import serial
except:
	pass
import time
import sqlite3
import logging
import locale

_SMSDATABASE = "/home/johan/code/sms_service/sms.db"
_TEAMDATABASE = "/home/johan/code/sms_service/teams.db"
_PORT = "/dev/ttyUSB2"
_SPEED = 115200
logger = logging.getLogger(__name__)

def _send_at(command, back, timeout):
	rec_buff = ""
	try:
		port = serial.Serial(_PORT, _SPEED)
	except:
		logging.error("Unable top open serial port in _send_at")
		return 0
	port.reset_input_buffer()
	try:
		logging.debug("    Sending this AT command: " + command)
		port.write((command + "\r\n").encode())
		time.sleep(timeout)
	except Exception as e:
		logging.error("    send_at outbound failed with: " + str(e))
	if port.inWaiting:
		time.sleep(0.01)
		rec_buff = port.read(port.inWaiting())
		#logging.debug("rec_buff decoded: " + rec_buff.decode('unicode_escape'))
	try:
		if back not in rec_buff.decode('unicode_escape'):
			logging.error("    Error with command: " + command + ". Got back: " + str(rec_buff.decode('unicode_escape').replace("\n",".").replace("\r",".")))
			port.reset_input_buffer()
			port.close()
			return 0
		else:
			logging.debug("    Recieved: " + str(rec_buff.decode('unicode_escape').replace("\n", ",").replace("\r",",")))
			port.reset_input_buffer()
			port.close()
			return str(rec_buff.decode('unicode_escape').replace("\n",",").replace("\r",","))
	except Exception as e:
		logging.error("    send_at inbound failed with: " + str(e))
		port.reset_input_buffer()
		port.close()
		return 0

def reset_modem():
	answer = _send_at("AT+CRESET","OK",5)
	return answer

def send_sms(phone_number, text_message):
	answer = _send_at("AT+CMGF=1","OK",3)
	answer = _send_at("AT+CMGS=\"" + phone_number + "\"",">",4)
	try:
		port = serial.Serial(_PORT, _SPEED)
	except:
		logging.error("Unable to open serial port in send_sms")
		return False
	port.reset_input_buffer()
	port.reset_output_buffer()
	# logging.debug("Sending this text message: " + str(text_message.decode()))
	if answer != 0:
		port.write(text_message)
		port.write(b"\x1A")
		time.sleep(5)
		answer = _send_at("","",5)
		if answer != 0:
			logging.info("   SMS sent ok")
			port.close()
			return True
		else:
			logging.error("   SMS not sent within timeout!")
			port.close()
			return False
	else:
		logging.error("   CMGS error")
		port.write(b"\x1A")
		port.reset_input_buffer()
		port.reset_output_buffer()
		port.close()
		return False

def delete_sms(pos):
	if pos > 30:
		return False
	answer = _send_at('AT+CMGF=1', 'OK',1)
	answer = _send_at('AT+CPMS=\"SM\",\"SM\",\"SM\"', 'OK', 1)
	answer = _send_at('AT+CMGD=' + str(pos),' OK',1)
	if 0 != answer:
		return True
	else:
		return False

def read_sms():
	retval = False
	# Prepare for SMS and memory storage
	answer = _send_at('AT+CMGF=1','OK',1)
	answer = _send_at('AT+CPMS=\"SM\",\"SM\",\"SM\"', 'OK', 1)

	# Read all SMS from SIM card and store to database, delete from SIM afterwards
	answer = _send_at('AT+CMGL="ALL"', 'OK',2)
	try:
		messages = answer.split('+CMGL:')
	except:
		messages = []
	for message in messages:
		pos = message.split(',')
		if 'REC' in message:
			answer = _send_at('AT+CMGR=' + str(pos[0].strip()),'+CMGR:', 3)
			if 0 != answer:
				temp = answer.replace('\n', ',')
				temp = temp.replace('\r', ',')
				temp = temp.split(',')
				number = str(temp[4].replace("\"",""))
				content = temp[9]
				yymmdd = temp[6].replace("\"","")
				hhmmss = temp[7].split("+")[0]
				timestamp_human = "20" + str(yymmdd.replace("/","")) + " " + str(hhmmss)
				#print("From this number: " + number)
				#print("With this content: " + content)
				#logging.debug("timestamp human: " + timestamp_human)
				timestamp = time.strptime(timestamp_human,"%Y%m%d %H:%M:%S")
				#print(time.strftime("%a %b %d %H:%M:%S %Y", timestamp))
				timestamp_db = time.mktime(timestamp)
				add_sms_to_db(number, content, timestamp_db, 0, 0)
				# Log number of total recieved SMS
				f2 = open('/home/johan/logs/sms_counter.log', 'r+')
				n_sms = int(f2.readline())
				n_sms += 1
				f2.seek(0)
				f2.write(str(n_sms))
				f2.close()
				delete_sms(int(pos[0]))
				retval = True
			else:
				retval = False
	return retval

def get_sms_by_id(id):
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM sms WHERE id=?", (id,))
	data = cursor.fetchall()[0]
	cursor.close()
	connection.close()
	ret_sms = sms(id=data[0], number=data[1], content=data[2], timestamp=data[3], valid=data[4], handled=data[5])
	return ret_sms

class team():
	def __init__(self, avdelning="", namn="", kod="", points=0, clues=0, correct="00000000000000000000"):
		self.avdelning = avdelning
		self.namn = namn
		self.kod = kod
		self.points = points
		self.clues = clues
		self.correct = correct

def create_teams_database():
	connection = sqlite3.connect(_TEAMDATABASE)
	cursor = connection.cursor()
	try:
		cursor.execute("CREATE TABLE IF NOT EXISTS teams (avdelning TEXT, namn TEXT, kod TEXT, points INTEGER, clues INTEGER, correct TEXT)")
	except:
		logging.info("Team Database table already created")
	cursor.close()
	connection.close()

def reset_teams_database():
	connection = sqlite3.connect(_TEAMDATABASE)
	cursor = connection.cursor()
	try:
		cursor.execute("DROP TABLE IF EXISTS teams")
	except:
		logging.error("Unable to reset team database")
	logging.info("Team database reset")
	cursor.close()
	connection.close()

class sms:
	def __init__(self, id=0, number="", content="", timestamp=0, handled=False, valid=False):
		self.id = id
		self.number = number
		self.content = content
		self.timestamp = timestamp
		self.handled = handled
		self.valid = valid

def create_sms_database():
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	try:
		cursor.execute("CREATE TABLE IF NOT EXISTS sms (id INTEGER, number TEXT, content TEXT, timestamp INTEGER, handled INTEGER, valid INTEGER)")
	except:
		logging.info("SMS Database table already created")
	cursor.close()
	connection.close()

def get_highest_id():
	highest = int(0)
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("SELECT id FROM sms ORDER BY id DESC")
	try:
		highest = cursor.fetchall()[0][0]
	except:
		highest = 0
	cursor.close()
	connection.close()
	return highest

def add_sms_to_db(number="", content="", timestamp=0, handled=0, valid=0):
	id = get_highest_id() + 1
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	# TODO sanitize content variable
	cursor.execute("INSERT INTO sms VALUES (?, ?, ?, ?, ?, ?)",(id, number, content, timestamp, handled, valid))
	logging.debug("Added SMS to table, id: {}, number {}, content {}, handled {}, valid {}.".format(id, number, content, timestamp, handled, valid))
	cursor.close()
	connection.commit()
	connection.close()

def get_oldest_valid_unhandled_sms():
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM sms WHERE valid=? AND handled=? ORDER BY timestamp ASC", (1,0,))
	try:
		data = cursor.fetchall()[0]
		retval = data[0]
	except:
		retval = 0
	cursor.close()
	connection.close()
	return retval

def get_oldest_invalid_unhandled_sms():
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM sms WHERE valid=? AND handled=? ORDER BY timestamp ASC", (0,0,))
	try:
		data = cursor.fetchall()[0]
		retval = data[0]
	except:
		retval = 0
	cursor.close()
	connection.close()
	return retval

def validate_to_db(id):
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("UPDATE sms SET valid=1 WHERE id=?",(id,))
	cursor.fetchall()
	cursor.close()
	connection.commit()
	connection.close()

def invalidate_to_db(id):
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("UPDATE sms SET valid=0 WHERE id=?",(id,))
	cursor.fetchall()
	cursor.close()
	connection.commit()
	connection.close()

def handled_to_db(id):
	connection = sqlite3.connect(_SMSDATABASE)
	cursor = connection.cursor()
	cursor.execute("UPDATE sms SET handled=1 WHERE id=?",(id,))
	cursor.fetchall()
	cursor.close()
	connection.commit()
	connection.close()

def add_team_to_db(avdelning="", namn="", kod="", points=0, clues=0, correct="00000000000000000000"):
	connection = sqlite3.connect(_TEAMDATABASE)
	cursor = connection.cursor()
	cursor.execute("INSERT INTO teams VALUES (?, ?, ?, ?, ?, ?)",(avdelning, namn, kod, points, clues, correct))
	cursor.close()
	connection.commit()
	connection.close()

def save_team_progress_to_db(namn, points, clues, correct):
	connection = sqlite3.connect(_TEAMDATABASE)
	cursor = connection.cursor()
	cursor.execute("UPDATE teams SET points=? WHERE namn=?",(points,namn))
	cursor.execute("UPDATE teams SET clues=? WHERE namn=?",(clues,namn))
	cursor.execute("UPDATE teams SET correct=? WHERE namn=?",(correct,namn))
	cursor.fetchall()
	cursor.close()
	connection.commit()
	connection.close()

def get_team_from_db(avdelning, namn, kod):
	connection = sqlite3.connect(_TEAMDATABASE)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM teams WHERE avdelning=? AND namn=? AND kod=?",(avdelning, namn, kod))
	try:
		data = cursor.fetchall()[0]
	except:
		logging.error("Team {} not found in database".format(namn))
		raise Exception
	cursor.close()
	connection.close()
	ret_team = team(avdelning=data[0], namn=data[1], kod=data[2], points=data[3], clues=data[4], correct=data[5])
	return ret_team

def get_top_three(avdelning):
	connection = sqlite3.connect(_TEAMDATABASE)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM teams WHERE avdelning=? ORDER BY points DESC LIMIT 3",(avdelning,))
	data = cursor.fetchall()
	cursor.close()
	connection.close()
	retval = ""
	try:
		retval = retval +  "1: " + str(data[0][1]) + ". "
	except:
		pass
	try:
		retval = retval +  "2: " + str(data[1][1]) + ". "
	except:
		pass
	try:
		retval = retval +  "3: " + str(data[2][1]) + "."
	except:
		pass
	return retval