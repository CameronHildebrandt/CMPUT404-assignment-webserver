#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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

protocol = 'HTTP/1.1'
code = '200 OK'

class Error(Exception):
    """Base class for other exceptions"""
    pass

class NotFoundError(Error):
    """Couldn't find the requested file"""
    pass

class MethodNotAllowedError(Error):
    """Couldn't find the requested file"""
    pass

class MovedPermanentlyError(Error):
    """Couldn't find the requested file"""
    pass


class MyWebServer(socketserver.BaseRequestHandler):

    def checkFileTypeValid(self, fileName):
        if(fileName[-5:] == ".html"):
            return True
        elif(fileName[-4:] == ".css"):
            return True
        return False

    def parseRequest(self, req):
        bytearraySyntaxRemoved = str(req)[2:-1]
        tokenList = bytearraySyntaxRemoved.split("\\r\\n")
        return tokenList

    def parseMethodToken(self, methodToken):
        return methodToken.split(" ")

    def handleGET(self, path):
        contentType = 'text/html'

        if(".css" in path):
            contentType = 'text/css'

        if path[-1] == '/':
            path += 'index.html'

        if not self.checkFileTypeValid(path):
            # 301 redirect to path + '/'
            return self.errorResponse(MovedPermanentlyError, {'redirectLocation': path + '/'})
            
    
        try:
            return self.buildResponse(self.openFile(path), contentType)
        except Exception as e:
            return self.errorResponse(NotFoundError) #theoretically we'll just directly pass through the error (e is "" right now?) Just defaulting to not found seems to do the trick for now tho..


    def buildResponse(self, data, contentType=""):
        headers = ""

        contentLength = len(data)
        
        if(contentType != None): headers += "\r\nContent-Type: {contentType};".format(contentType=contentType)
        headers += "\r\nContent-Length: {contentLength};".format(contentLength=str(contentLength))

        response = '{protocol} {code}{headers}\n\n{data}'.format(protocol=protocol, code=code, data=data, headers=headers)
        return response.encode('utf-8')

    def errorResponse(self, error, data={}):
        errorCode = ""
        headers = ""

        contentLength = 0

        headers += "\r\nContent-Length: {contentLength};".format(contentLength=str(contentLength))

        if error == NotFoundError:
            errorCode = "404 Not Found"
        elif error == MethodNotAllowedError:
            errorCode = "405 Method Not Allowed"
        elif error == MovedPermanentlyError:
            errorCode = "301 Moved Permanently"
            headers += "\r\nLocation: {location}".format(location=data['redirectLocation'])

        response = '{protocol} {errorCode}{headers}'.format(protocol=protocol, errorCode=errorCode, headers=headers)
        return response.encode('utf-8')

    def openFile(self, path):
        stringifiedFile = ''

        # The server already seems to disallow '..' in the url..
        # If this becomes an issue, just strip any occurrences of '../' here to fix

        try:
            with open('www/' + path, 'r') as file:
                stringifiedFile = file.read()
            return stringifiedFile
        except:
            raise NotFoundError()
    
    def handle(self):
        response = ''

        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)

        parsedRequest = self.parseRequest(self.data)
        methodToken = self.parseMethodToken(parsedRequest[0])

        # print("================")
        # print("Request:", methodToken)
        # print("================")

        if(methodToken[0] == "GET"):
            response = self.handleGET(methodToken[1])
        else:
            response = self.errorResponse(MethodNotAllowedError)

        # print("================")
        # print("Response:", response)
        # print("================")


        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
