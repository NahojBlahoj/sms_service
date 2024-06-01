# sms_service
##Giltigt sms-format
en hashtag (#) används som avgränsare i meddelandet:
**#AAA#BBB#CCC#DDD**
Där:
- AAA är avdelningens namn för att hålla koll på om meddelandet är giltigt
- BBB är lagets/patrullens namn, för att hålla koll på poäng
- CCC är en hemlig kod som bara patrullen känner till så inga andra kan missbruka lag/patrullnamnet
-DDD är t.ex. "ledtråd 1" eller "svar 6 97" om de vill ha ledtråd till fråga 1 resp.
		om de vill skicka in svaret 97 på fråga 6

Hur DDD formateras är valfritt.

'''
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
	"3" : "Vasa"
}
# Antalet poäng på respektive fråga, exempel
q_and_points = {
	"1" : 5,
	"2" : 1,
	"3" : 10
}
# Ledtrådar till respektive fråga, exempel
clues = {
	"1" : "sverige fick silvermedalj",
	"2" : "Han var kaxig med bollen",
	"3" : "Det har sjunkit"
}
'''