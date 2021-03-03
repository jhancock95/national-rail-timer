from datetime import timedelta
from datetime import datetime
import time
from nredarwin.webservice import DarwinLdbSession
import csv

darwin_sesh = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx", api_key="f9548875-c386-45a6-96dc-de1c554da75c")


stationDict = {}
#Contains station names and their respective station codes

with open('stationcodes.csv') as stationcodes:
    reader = csv.reader(stationcodes)
    for row in reader:
        stationDict[(row[0].upper())] = row[1]

class station():

    def __init__(self, name, walkingTime=None, destination=None):
        # Initialises the user preferences for their station, the time it takes to get there (optional) and their line (optional)
        self.name = name
        self.walkingTime = walkingTime
        self.destination = destination

    def call(self):
        #Calls the platform board and dispays the results

        board = darwin_sesh.get_station_board(self.name)
        print(board.location_name)

        def formatTime(inputTime):
            if type(inputTime) != datetime:
                inputTime = datetime.strptime(inputTime, '%H:%M')
            else:
                pass
            inputTime = str(inputTime)
            inputTime = inputTime[11:19]
            inputTime = datetime.strptime(inputTime, '%H:%M:%S')
            return (inputTime)

        def calulateDifference(arrivalTime, currentTime):
            if arrivalTime.hour == 00 and currentTime.hour in range(20,24):
                arrivalTime = arrivalTime.replace(hour=23)
                currentTime = currentTime.replace(hour=(int(currentTime.hour)-1))
                return (arrivalTime - currentTime)
            else:
                return (arrivalTime-currentTime)

        for item in board.train_services:
            #board.train_services contains the trains on the station board, called with specific function (i.e. .std = departure time)

            arrivalTime = formatTime(item.std)
            currentTime = formatTime(datetime.today())

            diff = calulateDifference(arrivalTime, currentTime)

            if "-" in str(diff):
                pass

            else:
                if self.destination != None:
                    if item.destination_text == self.destination:
                        destination = self.destination

                        output = ("There is a train to {} in {}".format(destination, diff))
                        print(output)

                        if self.walkingTime != None:
                            if diff < timedelta(minutes=self.walkingTime):
                                print("You've missed it")
                            else:
                                print("You've got {}").format(diff - timedelta(minutes=self.walkingTime))
                        else:
                            pass

                else:
                    output = ("There is a train to {} in {}".format(item.destination_text, diff))
                    print(output)

                    if self.walkingTime != None:
                        if diff < timedelta(minutes=self.walkingTime):
                            print("You've missed it")
                        else:
                            print("You've got {}").format(diff - timedelta(minutes=self.walkingTime))
                    else:
                        pass

def application():
    prompt = '> '

    print("Please enter your station")
    name = ""
    while name not in stationDict:
        name = raw_input(prompt)
        try:
            name = stationDict[name.upper()]
            break
        except:
            print("Name not recognised")

    print("Please enter your travel time to the station in minutes")
    walk = (raw_input(prompt)) or None
    if walk != None:
        walk = int(walk)

    print("Please enter your line destination")
    destination = raw_input(prompt) or None
    if destination != None:
        destination = destination.lower().capitalize()

    user = station(name, walk, destination)
    user.call()

application()
