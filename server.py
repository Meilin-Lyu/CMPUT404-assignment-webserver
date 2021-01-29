#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, 2021 Meilin Lyu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

# stolen from martim https://stackoverflow.com/users/4760185/martim
# From Stackoverflow
# https://stackoverflow.com/questions/25389095/python-get-path-of-root-project-structure
# "ROOT_DIR = os.path.abspath(os.curdir)" I used in line 87
# refer to https://docs.python.org/3/library/os.path.html
# "os.path.isfile(path), os.path.isdir(path)"
#  used in line 94 and line 107

class MyWebServer(socketserver.BaseRequestHandler):
    
    def check_method(self,method):
        if method == "GET":
            return True
        else:
            return False

    def read_file(self,path):
        file = open(path) 
        response = file.read()
        file.close()
        return response
                
    def valid_mime_types(self,path):
        if(path.endswith(".css") or path.endswith(".html")):
            return True
        else:
            return False
    
    def _200_response(self,content_type,path,header,response):
        header += 'HTTP/1.1 200 OK\r\n'
        header += 'Content-Type: '+ content_type +'\r\n'
        response += self.read_file(path)
        self.request.sendall((header +"\r\n"+ response).encode('utf8'))

    def _301_response(self,path):
        header = 'HTTP/1.1 301 MOVED PERMANENTLY\r\n'
        header += "Location: " + path + "\r\n"
        self.request.sendall((header).encode('utf8'))
    
    def _404_response(self):
        header = 'HTTP/1.1 404 Not Found\r\n'
        response = "<html><body><h3>404 File not found</h3></body</html>"
        self.request.sendall((header+"\r\n"+response).encode('utf8'))

    def _405_response(self):
        header = 'HTTP/1.1 405 Method Not Allowed\r\n'
        self.request.sendall((header).encode('utf8'))
        
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # decode the received data
        if self.data:
            # if data is not none
            split_decode_data = self.data.decode('utf-8').split()
            # get method type and request file from data
            method,request_file = split_decode_data[0],split_decode_data[1]
            # form the path with "www" folder
            path = os.path.abspath("www") +request_file
            
            if self.check_method(method):
                # initialize the header and response which are used to send
                response = ""
                header = "" 
                # the path should be ether a file or just a directory
                if os.path.isdir(path):
                    # doesnt contain any file, default case
                    # detect 301 error
                    if not path.endswith("/"):
                        request_file +="/"
                        # used for Location in response
                        self._301_response(request_file)
                        path += "/"
                    
                    path += "index.html"
                    content_type = "text/html"
                    self._200_response(content_type,path,header,response)
                            
                elif os.path.isfile(path):
                # contains file
                    if self.valid_mime_types(path):
                        if(path.endswith(".html")):
                            content_type = 'text/html'
                            self._200_response(content_type,path,header,response)
                        elif(path.endswith(".css")):
                            content_type = 'text/css'
                            self._200_response(content_type,path,header,response)
                        else:
                            self._404_response()
                    else:
                        self._404_response()
                else:
                    self._404_response()
            else:
                self._405_response()
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
