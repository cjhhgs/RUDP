import time

class Packet:
    def __init__(self,type,seqnum,data,time=None):
        self.type = type
        self.seqnum = seqnum
        self.data = data
        self.ifCheck = False
        self.ifSend=False
        self.startTime = time

class sendBuffer:
    def __init__(self):
        self.buffer = []
        self.size = 0

    

    def loadfile(self,file,maxDataLen):
        index = 0
        while True:
            data = file.read(maxDataLen)
            type = 'data'
            if len(self.buffer)==0:
                type = 'start'
            elif data == "":
                self.buffer[index-1].type = 'end'
                break
            
            packet = Packet(type,index,data)
            self.buffer.append(packet)
            index +=1

        self.size = len(self.buffer)
    
    def checkPacket(self,seqnum):
        self.buffer[seqnum].ifCheck = True
