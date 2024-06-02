#!/usr/bin/python3

import time
import sms_helpers
import logging
import locale

import logging.handlers

def log_setup():
    log_handler = logging.handlers.WatchedFileHandler('/home/johan/logs/sms_service.log')
    formatter = logging.Formatter(
        '%(asctime)s sms_service [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')
    #formatter.converter = time.gmtime  # if you want UTC time
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

# Deltagardetaljer, exempel
avdelningar = ["torn", "finn"]
lagnamn = ["summus", "araquorna", "clemens", "kastellet"]
koder = {
	"summus" : "abc123",
	"araquorna" : "morakniv",
	"clemens" : "domkyrka",
	"kastellet" : "spinnaker"
}
# Frågenummer med respektive svar, exempel
q_and_a = {
	"1" : "1958",
	"2" : "zlatan",
	"3" : "vasa",
	"4" : "gryta"
}
# Antalet poäng på respektive fråga, exempel
q_and_points = {
	"1" : 5,
	"2" : 1,
	"3" : 10,
	"4" : 7
}
# Ledtrådar till respektive fråga
clues = {
	"1" : "Sweden got a silver medal",
	"2" : "He is cocky on the grass",
	"3" : "It has sunk",
	"4" : "https://maps.app.goo.gl/rYEG9R6RWYzGAc9G9"
}

log_setup()

def check_sms_validity(id):
	# Checks if an sms is valid
	mysms = sms_helpers.get_sms_by_id(id)
	try:
		if mysms.content.lower().split("#")[1] in avdelningar and mysms.content.lower().split("#")[2] in lagnamn:
			# SMS has valid format, store in db
			sms_helpers.validate_to_db(id)
			logging.debug("Validated sms {} with content {}.".format(str(id), str(mysms.content)))
		else:
			# Invalid sms, just make it handled so it won't pop up again
			sms_helpers.handled_to_db(id)
			logging.debug("Invalid sms {} with content {}.".format(str(id), str(mysms.content)))
	except:
		# Assuming invalid if error in format
		sms_helpers.handled_to_db(id)
		logging.debug("Invalid sms {} with content {}.".format(str(id), str(mysms.content)))

logging.debug("Creating databases if not already done")
sms_helpers.create_sms_database()
sms_helpers.create_teams_database()

logging.debug("---- Starting sms service ----")

locale.setlocale(locale.LC_ALL, "sv_SE.UTF-8")
while True:
	try:
		sms_helpers.read_sms()

		while sms_helpers.get_oldest_invalid_unhandled_sms() > 0:
			logging.debug("Found an unhandled and invalid sms to check")
			check_sms_validity(sms_helpers.get_oldest_invalid_unhandled_sms())
		logging.debug("No invalid and unhandled sms in db")

		while sms_helpers.get_oldest_valid_unhandled_sms() > 0:
			mysms = sms_helpers.get_sms_by_id(sms_helpers.get_oldest_valid_unhandled_sms())
			avdelning = mysms.content.lower().split("#")[1]
			namn = mysms.content.lower().split("#")[2]
			kod = mysms.content.lower().split("#")[3]
			logging.debug("nummer: " + str(mysms.number) + ", avdelning: " + str(avdelning + ", namn: " + str(namn) + ", kod: " + str(kod)))
			if koder[namn] == kod:
				logging.debug("SMS with correct code recieved")
				try:
					myteam = sms_helpers.get_team_from_db(avdelning, namn, kod)
				except:
					# Laget finns inte, lägg till det i databasen
					sms_helpers.add_team_to_db(avdelning, namn, kod, 0, 0)
					myteam = sms_helpers.get_team_from_db(avdelning, namn, kod)
					logging.debug("Added team " + str(namn) + " to db")

				content = mysms.content.lower().split("#")[4]
				if "clue" in content:
					clue_nbr = content.split(" ")[1]
					reply = "Clue " + str(clue_nbr) + " is: " + str(clues[clue_nbr])
					sms_helpers.send_sms(mysms.number, reply.encode("utf-8"))
					logging.info("Lag " + str(namn) + " har fått ledtråd " + str(clue_nbr))
					myteam.clues += 1
					sms_helpers.save_team_progress_to_db(myteam.namn, myteam.points, myteam.clues)
				elif "answer" in content:
					question_nbr = content.split(" ")[1]
					answer = content.split(" ")[2]
					if answer == q_and_a[question_nbr]:
						myteam.points += q_and_points[question_nbr]
						reply = "Correct answer on question " + str(question_nbr) + "! Points: " + str(q_and_points[question_nbr]) + ", Total: " + str(myteam.points)
						sms_helpers.send_sms(mysms.number, reply.encode("utf-8"))
						logging.info("Lag " + str(namn) + " har svarat rätt på fråga " + str(question_nbr) + " med svaret " + str(answer))
					else:
						logging.info("Lag " + str(namn) + " har svarat fel på fråga " + str(question_nbr) + " med svaret " + str(answer))
						reply = "Wrong answer on question " + str(question_nbr)
						sms_helpers.send_sms(mysms.number, reply.encode("utf-8"))
					sms_helpers.save_team_progress_to_db(myteam.namn, myteam.points, myteam.clues)
				else:
					# Felformaterat men giltigt SMS
					# TODO svara något? Förlåtande analys av innehållet?
					logging.info("Giltigt SMS men felformaterat. Nummer: " + str(mysms.number) + " och innehåll: " + str(mysms.content))
					sms_helpers.invalidate_to_db(mysms.id)
				sms_helpers.handled_to_db(mysms.id)
			else:
				logging.info("Meddelande med fel kod skickad (fusk?). Nummer: " + str(mysms.number) + "meddelande: " + str(mysms.content))
				sms_helpers.invalidate_to_db(mysms.id)
				sms_helpers.handled_to_db(mysms.id)
		time.sleep(5)
	except Exception as e:
			logger.exception(e)
	finally:
			logger.debug("---- Looping sms_service ----")

