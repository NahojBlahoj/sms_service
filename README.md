# sms_service
## Giltigt sms-format
En hashtag (#) används som avgränsare i meddelandet:
**#AAA#BBB#CCC#DDD**
Där:
- AAA är avdelningens namn för att hålla koll på om meddelandet är giltigt
- BBB är lagets/patrullens namn, för att hålla koll på poäng
- CCC är en hemlig kod som bara patrullen känner till så inga andra kan missbruka lag/patrullnamnet
- DDD är t.ex. "ledtråd 1" eller "svar 6 97" om de vill ha ledtråd till fråga 1 resp.
		om de vill skicka in svaret 97 på fråga 6

Hur DDD formateras är valfritt.


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