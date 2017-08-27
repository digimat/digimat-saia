import requests
from digimat.saia import SAIANode


def getLakeTemperature():
    try:
        url='http://meteolakes.epfl.ch/meteolac/campbell_buchillon/Buchillon_WeatherSensor.dat'
        data=requests.get(url).text.splitlines()[-1].split(',')[3]
        return float(data)
    except:
        pass


node=SAIANode(253)

while node.isRunning():
    node.registers[0].float=getLakeTemperature()

    node.dump()
    node.sleep(15)
