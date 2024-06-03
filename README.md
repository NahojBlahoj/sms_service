# sms_service
## Giltigt sms-format
En hashtag (#) används som avgränsare i meddelandet:
#AAA#BBB#CCC#DDD
Där:
- AAA är avdelningens namn för att hålla koll på om meddelandet är giltigt
- BBB är lagets/patrullens namn, för att hålla koll på poäng
- CCC är en hemlig kod som bara patrullen känner till så inga andra kan missbruka lag/patrullnamnet
- DDD är t.ex. "ledtråd 1" eller "svar 6 97" om de vill ha ledtråd till fråga 1 resp.
		om de vill skicka in svaret 97 på fråga 6


Deltagardetaljer, exempel
```
avdelningar = ["torn", "finn"]
lagnamn = ["summus", "araquorna", "clemens", "kastellet"]
koder = {
	"summus" : "abc123",
	"araquorna" : "morakniv",
	"clemens" : "domkyrka",
	"kastellet" : "spinnaker"
}
```
Frågor, exempel
```
questions = {
	"1" : "When did the first IKEA warehouse open?",
	"2" : "Ajax-Juventus-Milan-Barcelona",
	"3" : "Bread and Boat",
	"4" : "Made for cooking"
}
```
Frågenummer med respektive svar, exempel
```
q_and_a = {
	"1" : "1958",
	"2" : "zlatan",
	"3" : "vasa",
	"4" : "gryta"
}
```
Antalet poäng på respektive fråga, exempel
```
q_and_points = {
	"1" : 5,
	"2" : 1,
	"3" : 10,
	"4" : 7
}
```
Ledtrådar till respektive fråga, exempel
```
clues = {
	"1" : "Sweden got a silver medal",
	"2" : "He is cocky on the grass",
	"3" : "It has sunk",
	"4" : "https://maps.app.goo.gl/rYEG9R6RWYzGAc9G9"
}
```
Exempel på konversation enligt reglerna ovan:
<img width="709" alt="image" src="https://github.com/NahojBlahoj/sms_service/assets/94386854/c26757db-59da-4cce-ae44-bc540ed1ac40">
