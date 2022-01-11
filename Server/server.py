#----------------------------------------------------------------------------
# Created By  : Sebastian I. Sosa Salas
# Created Date: 31/08/2021
# Brief: Server Simulation
# ---------------------------------------------------------------------------

"""-------------------------------SERVER-----------------------------------"""

import os
import sys
import socket
from time import gmtime, strftime

FORMAT = "utf-8"

def checkPort(portNo):
    """Takes a port number as a parameter, throws an error and exits the program
    if it is not within the limits."""
    if portNo < 1024 or portNo > 64000:
        print("\nError: Port number must be a number between 1024 and 64000 (including)")
        sys.exit()
        
        
def bindSocket(thisSocket, host, portNo):
    """Takes a socket, a host and a port number as parameters and tries to bind 
    the socket. Throws an error and exits the programm otherwise."""
    try:
        thisSocket.bind((host, portNo))
    except:
        print("\nError: binding was not possible. Socket might be already engaged")
        sys.exit()
        
        
def listenSocket(thisSocket, connections=5):
    """Takes a socket and a number of connections (optional, 5 as default)
    as parameter and puts the socket on listen mode. Throws and error, closes 
    the socket and exits the program otherwise."""
    try:
        thisSocket.listen(connections)
    except:
        print("\nError: unsuccesfull connection")
        thisSocket.close()
        sys.exit()
        
        
def printLogIn(address):
    """Takes the IP address as parameter and prints the Log In message with the 
    corresponding time of the connection."""
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(f"\n{currentTime}: Incomming connection from (IP: {address[0]}, PortNo: {address[1]}) established") 
    
    
def checkRequestValidity(magicNo, Type, fileNameLength, fileName):
    """Helper function for readRequest(). Takes the values of the header and check
    their validity. If something is wrong, prints an error message and close the
    socket"""
    if (magicNo != 0x497E):
        print("\nError: Magic number not as expected")
        raise
    elif (Type != 1):
        print("\nError: Header type not as expected")
        raise
    elif (len(fileName.encode(FORMAT)) != fileNameLength):
        print("\nError: Requested file name corrupted")
        raise
    
    
def readRequest(request, thisSocket):
    """Takes request in a bytearray format and a socket connection as parameters and
    reads the request, checks it's validity by using a helper function, and returns the
    file requested's name if everything is ok. Raises an error and close the 
    socket otherwise."""
    try:
        magicNo = request[0] << 8 | request[1]
        Type = int(request[2])
        fileNameLength = request[3] << 8 | request[4]
        fileName = request[5:].decode(FORMAT)
        checkRequestValidity(magicNo, Type, int(fileNameLength), fileName)
        return fileName
    except:
        thisSocket.close()
        print("\nServer unable to process file request.\nSocket closed.")   
        
        
def sendFile(file, length, thisSocket):
    """Helper function for sendResponse(). Takes the file previously opened in 
    sendResponse, reads its data and sends it through the socket. It also prints the
    message cointaining the amount of bytes transfered."""
    print("\nSending file...")
    try:
        data = file.read()
        bytesCount = thisSocket.send(data)
        file.close()
        thisSocket.close()
        print(f"\nFile sent.\nSocket closed: {bytesCount} bytes transferred.")        
    except:
        print(f"\nError: While sending the file. {bytesCount} bytes sent")
    
        
def sendResponse(fileName, thisSocket):
    """Takes the requested file name and the socket as parameters, tries to open and 
    read the requested file. Builds and sents the appropiate response to the socket.
    Uses sendFile() as a helper function."""
    magicNo = 0x497E
    Type = 2
    header = bytearray(8)
    try:
        infile = open(fileName, "rb")
        dataLength = (os.stat(fileName)).st_size
        statusCode = 1     
    except:
        infile = None
        statusCode = 0
        dataLength = 0        
    header[0] = magicNo >> 8
    header[1] = magicNo & 0x00FF
    header[2] = Type
    header[3] = statusCode
    header[4] = (dataLength >> 24)
    header[5] = (dataLength & 0x00FF0000) >> 16
    header[6] = (dataLength & 0x0000FF00) >> 8
    header[7] = (dataLength & 0x000000FF)
    thisSocket.send(header)
    if statusCode == 1:
        sendFile(infile, dataLength, thisSocket)
    elif statusCode == 0:
        thisSocket.close()
        print("\nError: File not found or Server was unable to open it.\nSocket closed.")
        

    
def server(portNo):
    """Command line application that operates as a TCP server. Takes a port number as 
    a parameter which is an input from the command line and it is the port number 
    to which the server will bind the socket to accept the file transfer requests."""
    localHost = socket.gethostname()
    print(f"\nLocal Host at {localHost}\nServer's IP Address: {socket.gethostbyname(localHost)}")
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    ## Where: AF_INET stands for IPV4 protocol; SOCK_STREAM is for socket type UDP
    bindSocket(serverSocket, localHost, portNo)
    listenSocket(serverSocket)
    while True:
        print("\nServer waiting for incoming connection...")
        (activeConnection, address) = serverSocket.accept()
        activeConnection.settimeout(1)
        printLogIn(address)
        try:
            request = activeConnection.recv(2048)
            requestRecvd = True
        except socket.timeout:
            print("\nError: TimeOut while receiving file request. Socked closed.")
            activeConnection.close()
            requestRecvd = False
        if requestRecvd:
            activeConnection.settimeout(None)
            fileRequest = bytearray(request)
            fileName = readRequest(fileRequest, activeConnection)
            sendResponse(fileName, activeConnection)
            

def main():
    """Main function for the program - reads the paramenter and executes the server"""
    if len(sys.argv) != 2:
        print("Usage: python3 server.py [portNumber]")
        sys.exit()
    else:
        portNo = int(sys.argv[1])        
        checkPort(portNo)
        server(portNo)
            
        
main()