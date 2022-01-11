#----------------------------------------------------------------------------
# Created By  : Sebastian I. Sosa Salas
# Created Date: 31/08/2021
# Brief: Client Simulation
# ---------------------------------------------------------------------------

"""-------------------------------CLIENT-----------------------------------"""

import os
import sys
import socket

FORMAT = "utf-8"
BLOCKSIZE = 4096

def getHost(address):
    """Takes an address as a parameter and tries to get the ip address in a 
    dot-decimal format. Throws an error and exits the program otherwise."""
    try:
        ipAddress = socket.gethostbyname(address)
        return ipAddress
    except:
        print("\nError: Incorrect IP address or hostname")
        sys.exit()


def checkPort(portNo):
    """Takes a string port number as a parameter, converts it to integer. Throws 
    an error and exits the program if the given port is not within the limits."""
    try:
        portNo = int(portNo)
        if portNo < 1024 or portNo > 64000:
            raise
        return portNo
    except:
        print("\nError: Port number must be a number between 1024 and 64000 (including)")
        sys.exit()
        
        
def checkFile(fileName):
    """Takes a name of a file as parameter and checks if its length is within the 
    range and if it exists within the local directory. Returns True if checkings 
    are passed, prints an error and returns False otherwise."""
    fileNameLength = len(fileName.encode(FORMAT))
    if os.path.isfile(fileName):
        print("\nError: file already exists in local host")
        return False
    elif (fileNameLength > 1024):
        print("\nError: file name is too long")
        return False
    return True
    
    
def createSocket():
    """Tries to create and return a new IPv4 - Stream Socket. 
    Throws an error otherwise"""
    try:
        newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("\nNew Socket created")
        return newSocket
    except:
        print("\nError: Socket error. Unable to create new socket")
        sys.exit()
        
        
def connectSocket(thisSocket, ipAddress, portNo):
    """Takes a socket as a parameter and tries to connect it to the given
    ip address and port number. Throws an error and exits otherwise."""
    try:
        thisSocket.connect((ipAddress, portNo))
        print("Socket connected")
    except:
        thisSocket.close()      
        print("Error: Unable to connect to server")
        sys.exit()
    
        
def createFileRequest(fileName):
    """Takes the fileName as a parameter and creates the FileRequest. 
    Header: magicNo(16bit), type(8bit), FileNameLength(32bit), 
    FileName(variable size)"""
    fileNameLength = len(fileName.encode(FORMAT))
    magicNo = 0x497E
    Type = 1
    header = bytearray(5)
    header[0] = magicNo >> 8
    header[1] = magicNo & 0x00FF
    header[2] = Type
    header[3] = fileNameLength >> 8
    header[4] = fileNameLength & 0x00FF
    fileRequest = header + fileName.encode(FORMAT)
    return fileRequest


def checkResponseValidity(magicNo, Type, statusCode, dataLength):
    """Auxiliar function for readResponse(). Takes the values of the header of 
    the response and the socket and checks 
    its validity or print's the appropiate error message. Returns True all ok."""
    if (magicNo != 0x497E):
        print("Error: Error: Magic number not as expected")
        raise
    elif (Type != 2):
        print("Error: Header type not as expected")
        raise
    elif (dataLength == 0) or (statusCode == 0):
        print("File not found or Server was unable to open the requested file")
        raise
    return True


def readResponse(response, fileName, thisSocket):
    """Takes response contained within a bytearray, extracts the data from it 
    for validation by using the helper function checkResponseValidity(). Closes 
    the socket and prints an error message otherwise."""
    try:
        magicNo = response[0] << 8 | response[1]
        Type = int(response[2])
        statusCode = int(response[3])
        dataLength = response[4] << 24 | \
            response[5] << 16 | \
            response[6] << 8 | \
            response[7]
        if checkResponseValidity(magicNo, Type, statusCode, dataLength):
            if dataLength > 0 and statusCode == 1:
                receiveFile(fileName, dataLength, thisSocket)
        #else:
            #thisSocket.close()
    except:
        print("Error: File-Response corrupted")
        thisSocket.close()  
        
                
def receiveFile(fileName, dataLength, thisSocket):
    """Receives the data sended by the server and writes it into a new file with the 
    name provided as a parameter. Checks that the data received is equal to the 
    parameter dataLength. Throws an error and close a socket if something goes wrong."""
    print("Receiving file...")
    bytesCount = 0
    file = open(fileName, "wb")
    while bytesCount < dataLength:
        try:
            thisSocket.settimeout(1)            
            buffer = thisSocket.recv(BLOCKSIZE)
            thisSocket.settimeout(None)            
            bufferArray = bytearray(buffer)
        except:
            print("\nError: TimeOut while receiving file")
            break 
        dataReceived = len(buffer)
        bytesCount += dataReceived
        file.write(bufferArray)
        if dataReceived == 0: #Checks for gaps of data within the loop
            print("\nError: Data-gap while receiving file")
            break
    file.close()
    if bytesCount == dataLength:
        print("\nFile succesfully received")
    else:
        print("\nError: File transfer interrupted\nConnection closed")
    thisSocket.close()
    print(f"\nBytes transfered: {bytesCount}\nConnection closed.")  
    
    
def client(address, port, fileName):
    """Command line application that operates a TCP client. Accepts three parameters,
    IP address or hostname, port number, and the requested file name. Connects to the 
    server with the given parameters and requests for the file. Proccess the server
    response and receives the file storing it to the folder where the app is 
    being run."""
    ipAddress = getHost(address)
    portNo = checkPort(port)
    if checkFile(fileName):
        clientSocket = createSocket()
        connectSocket(clientSocket, ipAddress, portNo)
        fileRequest = createFileRequest(fileName)
        clientSocket.send(fileRequest)
        clientSocket.settimeout(1)
        try:
            response = clientSocket.recv(8)
            responseRecvd = True
        except socket.timeout:
            print("Error: TimeOut while receiving file response")
            clientSocket.close()
            sys.exit()
        if responseRecvd:
            clientSocket.settimeout(None)            
            fileResponse = bytearray(response)
            readResponse(fileResponse, fileName, clientSocket)
    else:
        sys.exit()
        
        
def main():
    """Main function for the program - reads the paramenters and executes the client"""
    if len(sys.argv) != 4:
        print("Usage: python3 client.py [ipAddress|hostName] [portNumber] [fileName]")
        exit()
    else:
        address = sys.argv[1]
        portNumber = sys.argv[2]
        fileName = sys.argv[3]
        client(address, portNumber, fileName)
        
        
main()