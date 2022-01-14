from email import message
import sys
import getopt
from time import sleep
import time

import Checksum
import BasicSender
import Packet

import threading

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
# python TestHarness.py -s Sender.py -r Receiver.py
class Sender(BasicSender.BasicSender):

    MAX_DATA_LEN = 500
    MAX_TIME = 0.5 #秒
    MAX_WIN = 5
    


    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)

        #加载文件
        self.buffer = Packet.sendBuffer()
        #print("loadfile")
        self.buffer.loadfile(self.infile,self.MAX_DATA_LEN)
        self.winLeft = 0
        self.winRight = min(self.MAX_WIN,self.buffer.size) #将窗口大小限定
        self.sackMode = sackMode

    # Main sending loop.
    def start(self): 
        t1 = threading.Thread(target=self.listener)
        
        t2 = threading.Thread(target=self.timeChecker)
        #print("buffer:",self.buffer.size)
        #print("start")
        t1.start()
        t2.start()
        i = self.winLeft
        while i< self.winRight: #先把最初的几个包发出去
            self.send_pack(i)
            i += 1
        
        t1.join()
        #print("t1 join")
        t2.join()
        #print("end")


        

    def handle_timeout(self):
        pass

    def handle_new_ack(self, ack):
        pass

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print(msg)

    def listener(self):
        
        #print("listen")
        while self.winLeft<self.buffer.size:
            #print(self.winLeft)
            msg = self.receive(0)   #监听消息
            
            if not msg:
                continue
            msg = msg.decode()
            if not Checksum.validate_checksum(msg):
                #print(1)
                continue
            
            seqnum,sacknum = self.getSeqnumAndSack(msg) #获取ack信息
            #print("L:",self.winLeft,",R:",self.winRight,",seq:",seqnum,',sa:',sacknum)
            self.ackHandler(seqnum,sacknum) #给buffer中确认的块打上确认标记

            if seqnum>self.winLeft:    #若判断窗口能移动，调用过程
                self.winMove()
            

        #移动窗口过程    
    def winMove(self):
        i = self.winLeft
        while i<self.winRight:  
            if self.buffer.buffer[i].ifCheck==True:
                i+=1
            else:
                break
        count = i-self.winLeft  #表示左边释放了多少个
        while count > 0 and self.winLeft<self.buffer.size: #注意左边界不能越界
            count-=1
            self.winLeft += 1
            if self.winRight<self.buffer.size:  #注意右界不能超出
                self.winRight += 1
                self.send_pack(self.winRight-1)
    
    def timeChecker(self):
        while self.winLeft<self.buffer.size:
            sleep(0.1)
            seqs = self.checkTime(self.MAX_TIME) #每100ms检查一下窗口中是否有超时，返回超时包的序号
            if not len(seqs)==0:
                for i in seqs:
                    self.send_pack(i) #将超时的包重发
    
    def checkTime(self,timeOut):    #返回超时的包序号
        t = time.time()
        res = []
        i = self.winLeft
        while i < self.winRight:
            if self.buffer.buffer[i].ifCheck==False and self.buffer.buffer[i].ifSend==True:
                if t-self.buffer.buffer[i].startTime > timeOut :
                    res.append(i)
            i+=1
        return res


    
    def send_pack(self,seqnum):
        pack = self.buffer.buffer[seqnum]
        self.buffer.buffer[seqnum].startTime = time.time()
        self.buffer.buffer[seqnum].ifSend = True
        msg = self.make_packet(pack.type,pack.seqnum,pack.data)
        self.send(msg)
    
    def getSeqnumAndSack(self,msg):
        msg_type, seqno, data, checksum = self.split_packet(msg)
        sacknum = ''
        if self.sackMode==1:
            seqno,sacknum = seqno.split(';')
        seqno = int (seqno)
        if len(sacknum)==0:
            sacknum = []
        else:
            sacknum = [int(i) for i in sacknum.split(',')]
        return seqno,sacknum
    
    def ackHandler(self,seqnum,sackNum):
        #对累计确认的包进行check
        
        if seqnum<=self.winLeft and len(sackNum)==0:
            return
        for i in range(self.winLeft,seqnum):
            self.buffer.checkPacket(i)
        # 将选择确认中的确认包也进行check
        if not len(sackNum) == 0:
            for i in range(sackNum[0], sackNum[-1] + 1):
                self.buffer.checkPacket(i)
        
        

'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print ("RUDP Sender")
        print ("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print ("-p PORT | --port=PORT The destination port, defaults to 33122")
        print ("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print ("-d | --debug Print debug messages")
        print ("-h | --help Print this usage message")
        print ("-k | --sack Enable selective acknowledgement mode")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True
    
    
    s = Sender(dest, port, filename, debug, sackMode)
    
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
