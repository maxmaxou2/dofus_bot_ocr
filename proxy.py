from scapy.all import *
from scapy.layers.inet import TCP
import struct
from Messages import *
import mapPosition as mP
import Paquet as P
import threading
import time

class Proxy :

    def __init__(self, max_duration) :
        self.max_duration = max_duration
        self.pos = (None,None)
        self.queue = [b'',b'']
        self.changed = False
        self.start_time = time.time()
        self.threading_function()
        """sniff_thread = threading.Thread(target=self.threading_function)
        sniff_thread.start()"""

    def stop_filter(self, pkt):
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.max_duration or self.changed :
            return True
        return False

    def threading_function(self) :
        sniff(prn=self.packet_callback, stop_filter=self.stop_filter)
    
    def packet_callback(self, packet):
        if TCP in packet and (packet[TCP].dport == 5555 or packet[TCP].sport == 5555):
            packet_data = bytes(packet[TCP].payload)
            if packet[TCP].dport == 5555 :
                self.queue[0] += b''#packet_data
            elif packet[TCP].sport == 5555 :
                self.queue[1] += packet_data
            #self.processQueue(False)
            self.processQueue(True)

    def processQueue(self, received) :
        while len(self.queue[1 if received else 0]) >= 2 :
            packet_id, length, content, leftover = self.decode_packet(self.queue[1 if received else 0], received)
            if len(self.queue[1 if received else 0]) >= length+2+(0 if received else 4) :
                self.queue[1 if received else 0] = leftover
                return self.processMessage(P.Paquet(packet_id, length, content))
            else :
                return
            
    def decode_packet(self, packet_data, received):
        #print(packet_data[0:2])
        hi_header = struct.unpack('>H', packet_data[:2])[0]
        #print(hi_header)
        packet_id = hi_header >> 2
        len_type = hi_header & 0b11
        #print("Len type", len_type)
        #print(packet_data[0:2])
        content_offset = 0
        if not received :
            content_offset += 4
        if len_type == 0 :
            packet_length = 0
            content_offset += 2
        elif len_type == 1:
            packet_length = struct.unpack('>H', b'\x00' + packet_data[content_offset+2:content_offset+3])[0]
            content_offset += 3
        elif len_type == 2:
            packet_length = struct.unpack('>H', packet_data[content_offset+2:content_offset+4])[0]
            content_offset += 4
        elif len_type == 3:
            packet_length = struct.unpack('>i', b'\x00' + packet_data[content_offset+2:content_offset+5])[0]
            content_offset = 5
        else:
            queue = b''
            return 0,0,b'',b''
        #print("Offset", content_offset)
        #print("Data", packet_data)
        #print("Length", packet_length)
        content = packet_data[content_offset:content_offset + packet_length]
        #print("Content", content)
        leftover = b''
        if len(packet_data) > content_offset + packet_length:
            leftover = packet_data[content_offset + packet_length:]
        return packet_id, packet_length, content, leftover
            
    def processMessage(self, current_paquet : P.Paquet) :
        if current_paquet.isComplete() :
            match current_paquet.id :
                case 2307 : #ChatServerMessage 0100000110100000111100000010110000011000000000000000
                    a = 0
                case 8323 : #GameMapMovementMessage
                    a = 0
                case 7745 : #GameContextRefreshEntityLookMessage
                    a = 0
                case 7865 : #ChatServerWithObjectMessage
                    a = 0
                case 9954 : #PrismAddOrUpdateMessage
                    a = 0
                case 4351 : #SetCharacterRestrictionsMessage
                    a = 0
                case 4094 : #MapComplementaryInformationsDataMessage
                    message = MapComplementaryInformationsDataMessage(current_paquet)
                    #print("SubAreaId : ", message.subAreaId)
                    #print("MapId : ", message.mapId)
                    self.pos = mP.findPos(message.mapId)
                    self.changed = True
                    print("Proxy changed ", self.changed)
                    print(f"Pos : ({self.pos[0]},{self.pos[1]})")
                    return True
                case 5244 : #CurrentMapMessage
                    message = CurrentMapMessage(current_paquet)
                    #print("MapId : ", message.mapId)
                    self.pos = mP.findPos(message.mapId)
                    self.changed = True
                    print("Proxy changed ", self.changed)
                    print(f"Pos : ({self.pos[0]},{self.pos[1]})")
                    return True
                case _ :
                    print(f"Paquet ID: {current_paquet.id}, Type : {current_paquet.type}")
                    a=0
        return False
    
Proxy(1000)