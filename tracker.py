import socket
import json
import sys
import random
import hashlib

class Tracker:

    def __init__(self, settings):
        self.peer_table = {}
        self.file_table = {}
        self.port = settings["port"]
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("Socket created")
        try:
            self.listening_socket.bind(("", settings["port"]))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        print 'Socket bind complete'
        self.listening_socket.listen(10)
        print 'Socket now listening'

    def create_join_entry(self, msg, addr):
        print(addr[0] + ":" + str(msg["port"]))
        peer_key = hashlib.md5(addr[0] + ":" + str(msg["port"])).hexdigest()
        self.peer_table[peer_key] = {"address": addr[0], "port": msg["port"]}
        return peer_key

    def create_file_entries(self, peer_key, msg):
        for filename in msg["files"]:
            file_key = hashlib.md5(filename).hexdigest()
            if file_key in self.file_table.keys() and peer_key not in self.file_table[file_key]:
                self.file_table[file_key].append(peer_key)
            else:
                self.file_table[file_key] = [peer_key]

    def create_join_reply_message(self, peer_key):
        msg = {}
        msg["msg_type"] = "JOIN_REPLY"
        msg["peer_id"] = peer_key
        msg["neighboring_peers"] = []
        for key, value in self.peer_table.iteritems():
            if key != peer_key:
                msg["neighboring_peers"].append(value)
        return json.dumps(msg)

    def parse_message(self, data, addr):
        print(data)
        msg = json.loads(data)
        if "msg_type" not in msg:
            return
        if msg["msg_type"] == "JOIN":
            peer_key = self.create_join_entry(msg, addr)
            self.create_file_entries(peer_key, msg)
            return self.create_join_reply_message(peer_key)

    def start_tracker(self):
        while 1:
            conn, addr = self.listening_socket.accept()
            # try:
            data = conn.recv(1024)
            print 'Received data'
            print data
            if data:
                return_data = self.parse_message(data, addr)
                conn.sendall(return_data)
            print self.peer_table
            print self.file_table
            conn.close()
            # except:
            #     break
            # print 'Connected with ' + addr[0] + ':' + str(addr[1])
        self.listening_socket.close()