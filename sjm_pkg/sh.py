#!/usr/bin/env python

import sys, time, string, re, threading
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

class SmartHubComm(QObject):

    new_inouts = pyqtSignal(list, list, list, list, list, list, name = 'new_smhub_inouts')
    new_fullblock = pyqtSignal(str, name = 'new_smhub_raw')
    
    def __init__(self, parent=None):
        super(SmartHubComm, self).__init__(parent)

        self.smarthubIP = '198.17.154.164'
        self.router_dim = 20
        self.min_smhub_status_size = 1000
        self.msg_total = 0
        self.smhub_status_block = ""
        self.raw_model_string = ""
        self.this_is_set_smhub_phase = False

        self.inportl = list(range(self.router_dim))
        self.inlabell = ["Unknown"] * self.router_dim
        self.outportl = list(range(self.router_dim))
        self.outlabell = ["Unknown"] * self.router_dim
        self.routein = list(range(self.router_dim))
        self.routeout = list(range(self.router_dim))
        
        self.new_fullblock.connect(self.parse_hub_data)
        self.new_inouts.connect(self.on_shdata_parsed)
        self.invoke_query_of_smhub()

    def invoke_query_of_smhub(self):
        self.sock = QTcpSocket()
        self.sock.error.connect(self.on_tcp_error)
        self.sock.readyRead.connect(self.on_ready_read)

        try:
            self.sock.connectToHost(self.smarthubIP, 9990)
            if not self.sock.waitForConnected(1000):
                errstr = "Error Communicating with SmartHub"
                print(errstr)
        except:
            print(self.sock.SocketError())

    def on_shdata_parsed(self,inportl, inlabell, outportl, outlabell, routein, routeout):
        self.inportl = inportl
        self.inlabell = inlabell
        self.outportl = outportl
        self.outlabell = outlabell,
        self.routein = routein
        self.routeout = routeout

    def get_smhub_inouts(self):

        return(self.inportl, self.inlabell, self.outportl, self.outlabell, self.routein, self.routeout)
        
    def on_ready_read(self):

        instream = QTextStream(self.sock)
        inblock = ()

        bytes_avail = self.sock.bytesAvailable()
        inblock = instream.readAll() 
        self.smhub_status_block += inblock
        self.msg_total = self.msg_total + bytes_avail

        if self.msg_total >= self.min_smhub_status_size:
            self.sock.close()
            self.new_fullblock.emit(self.smhub_status_block)

    def parse_hub_data(self, fullblock):

        blocklist = ()
        blocklist = fullblock.split('\n')
        
        ila = []; ola = []; vra = []; inportl = []; inlabell = []
        outportl = []; outlabell = []; routein = []; routeout = []

        modre = re.compile('^Model name')
        ilre = re.compile('^INPUT LABELS:$')
        olre = re.compile('^OUTPUT LABELS:$')
        vore = re.compile('^VIDEO OUTPUT ROUTING:$')

        modind = [i for i, item in enumerate (blocklist) if modre.match(item)][0]

        self.raw_model_string = str(blocklist[modind])
        #print("Smarthub model:",self.raw_model_string)

        # Find lines starting the input label list, output label list, and routing list
        ilind = [i for i, item in enumerate (blocklist) if ilre.match(item)][0]
        olind = [i for i, item in enumerate (blocklist) if olre.match(item)][0]
        voind = [i for i, item in enumerate (blocklist) if vore.match(item)][0]

        # Read in the input and output label blocks, and the routing list
        for i in range((ilind+1), (ilind+(self.router_dim+1))):
            ila.append(blocklist[i])

        for i in range((olind+1), (olind+(self.router_dim+1))):
            ola.append(blocklist[i])

        # The routing list is just two numbers (input port and matched output port).
        for i in range((voind+1), (voind+(self.router_dim+1))):
            vra.append(blocklist[i])

        # Parse the label lists and populate a data structure to hold the labels
        for i in range(0, len(ila) ):
            line = ila[i]
            #print line
            try:
                [port, label] = filter(None, line.split(' '))
            except:
                try:
                    [port, label1, label2] = line.split(' ')
                    label = label1 + " " + label2
                except:
                    try:
                        [port, label1, label2, label3] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3
                    except:
                        [port, label1, label2, label3, label4] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3 + " " + label4
            inportl.append(port)
            inlabell.append(label)

        for i in range(0, len(ola) ):
            line = ola[i]
            #print line
            try:
                [port, label] = filter(None, line.split(' '))
            except:
                try:
                    [port, label1, label2] = line.split(' ')
                    label = label1 + " " + label2
                except:
                    try:
                        [port, label1, label2, label3] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3
                    except:
                        [port, label1, label2, label3, label4] = line.split(' ')
                        label = label1 + " " + label2 + " " + label3 + " " + label4

            outportl.append(port)
            outlabell.append(label)

        for i in range(0, len(vra) ):
            line = vra[i]
            try:
                [outport, inport] = line.split(' ')
                inport = int(inport)
                outport = int(outport)
            except:
                print("Failed to parse route line %d") % (i)
            routein.append(inport)
            routeout.append(outport)
            #print(routeout)
        self.new_inouts.emit(inportl, inlabell, outportl, outlabell, routein, routeout)

    def on_tcp_error(self, connect_error):

        if connect_error == QAbstractSocket.RemoteHostClosedError:
            print("ERROR: Remote host closed")
        elif connect_error == QAbstractSocket.HostNotFoundError:
            print("ERROR: Host was not found")
        elif connect_error == QAbstractSocket.ConnectionRefusedError:
            print("ERROR: The connection was refused by the peer")
        else:
            print("The following error occurred: %l" % self.sock.errorString())

    def get_smarthub_model(self):
             
        return self.raw_model_string
 

