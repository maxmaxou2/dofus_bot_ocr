import Paquet as P

class MapComplementaryInformationsDataMessage :
    def __init__(self, packet : P.Paquet) :
        self.subAreaId = packet.readVarShort()
        self.mapId = packet.readDouble()

class CurrentMapMessage :
    def __init__(self, packet : P.Paquet) :
        #print("Content", packet.content)
        self.mapId = packet.readDouble()