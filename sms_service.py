#!/usr/bin/python3

import time
import sms_helpers
import logging

logger = logging.getLogger(__name__)
LOGGER_FORMAT = '%(asctime)s  %(message)s'
logging.basicConfig(filename='/home/johan/logs/sms_service.log', encoding='utf-8', level=logging.DEBUG, format=LOGGER_FORMAT)
# .debug is used for debugging and in english
# .info används för tävlingen och är på svenska

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
	"3" : "vasa"
}
# Antalet poäng på respektive fråga, exempel
q_and_points = {
	"1" : 5,
	"2" : 1,
	"3" : 10
}
# Ledtrådar till respektive fråga
clues = {
	"1" : "sverige fick silvermedalj",
	"2" : "Han var kaxig med bollen",
	"3" : "Det har sjunkit"
}

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

logging.debug("---- Starting main loop----")

try:

# TODO make while loop here

	sms_helpers.read_sms() # TODO this is time consuming and dependent, move to separate service

	while sms_helpers.get_oldest_invalid_unhandled_sms() > 0:
		logging.debug("Found an unhandled and invalid sms to check")
		check_sms_validity(sms_helpers.get_oldest_invalid_unhandled_sms())
	logging.debug("No invalid and unhandled sms in db")
	
	while sms_helpers.get_oldest_valid_unhandled_sms() > 0:
		mysms = sms_helpers.get_sms_by_id(sms_helpers.get_oldest_valid_unhandled_sms())
		avdelning = mysms.content.lower().split("#")[1]
		namn = mysms.content.lower().split("#")[2]
		kod = mysms.content.lower().split("#")[3]
		logging.debug("avdelning: " + str(avdelning + ", namn: " + str(namn) + ", kod: " + str(kod)))
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
			if "ledtråd" in content:
				clue_nbr = content.split(" ")[1]
				sms_helpers.send_sms(mysms.number, clues[clue_nbr])
				logging.info("Lag " + str(namn) + " har fått ledtråd " + str(clue_nbr))
				myteam.clues += 1
				sms_helpers.save_team_progress_to_db(myteam.namn, myteam.points, myteam.clues)

			elif "svar" in content:
				question_nbr = content.split(" ")[1]
				answer = content.split(" ")[2]
				if answer == q_and_a[question_nbr]:
					# TODO kolla så de inte redan fått poäng för denna fråga
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
except Exception as e:
	logger.exception(e)
finally:
	logger.debug("Ending sms_service")
