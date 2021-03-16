from datetime import timedelta
from datetime import datetime
from nredarwin.webservice import DarwinLdbSession
import csv
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

darwin_sesh = DarwinLdbSession(wsdl="https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx", api_key="f9548875-c386-45a6-96dc-de1c554da75c")

app = Flask(__name__)

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

        trainlist = []
        trainOrder = 1

        for item in board.train_services:
            #board.train_services contains the trains on the station board, called with specific function (i.e. .std = departure time)

            output = {}

            arrivalTime = formatTime(item.std)
            currentTime = formatTime(datetime.today())

            diff = calulateDifference(arrivalTime, currentTime)

            if "-" in str(diff):
                pass

            else:
                if self.destination != None:
                    if item.destination_text == self.destination:
                        destination = self.destination

                        output['destination'] = str(destination)
                        output['trainTime'] = str(diff)

                        if self.walkingTime != None:
                            if diff < timedelta(minutes=self.walkingTime):
                                output['walkTime'] = 'missed'
                            else:
                                output['walkTime'] = (str(diff - timedelta(minutes=self.walkingTime)))
                        else:
                            pass
                        trainlist.append(output)
                        #trainlist[trainOrder] = output
                        #trainOrder += 1



                else:
                    output['destination'] = item.destination_text
                    output['trainTime'] = str(diff)
                    #print(output)

                    if self.walkingTime != None:
                        if diff < timedelta(minutes=self.walkingTime):
                            output['walkTime'] = 'missed'
                        else:
                            td = (diff - timedelta(minutes=self.walkingTime))
                            output['walkTime'] = str(diff - timedelta(minutes=self.walkingTime))
                    else:
                        pass
                    trainlist.append(output)
                    #trainlist[trainOrder] = output
                    #trainOrder += 1

        return(trainlist)

user = station('DHM', 10, None)
x = user.call()
amount = 3



@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':

        userStation = stationDict[str(request.form['userStation']).upper()]

        userWalk = (request.form['userWalk'])
        if userWalk == "":
            userWalk = None
        else:
            userWalk = int(request.form['userWalk'])

        userDestination = request.form['userDestination']
        if userDestination == "":
            userDestination = None
        else:
            userDestination = (str(request.form['userDestination'])).lower().capitalize()

        user = station(userStation, userWalk, userDestination)
        call = user.call()

        return render_template('index.html', call=call)


    else:
        try:
            return render_template('index.html', call=call)
        except:
            return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

