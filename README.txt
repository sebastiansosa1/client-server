----------------------------------------------------------------------------
Created By: Sebastian I. Sosa Salas
Created Date: 31/08/2021
----------------------------------------------------------------------------

BRIEF:

Client and Server application which allows a client to download a file from 
the folder where the server is located.

The client and the server communicate through stream / TCP sockets,
exchanging control and actual file data.

USAGE:

To execute the SERVER:
    Go to the folder where the Server.py file is located and execute the following command:

    "python3 server.py [portNumber]"

    Without the quotes and replacing [portNumber] for the chosen port number. The server will 
    now execute and print the IP Address where the Client will connect to.

To execute the CLIENT:
    Using another terminal window, open the folder where the Client.py file is located and 
    execute the following command:

        "python3 client.py [ipAddress|hostName] [portNumber] [fileName]"

        Without the quotes and replacing [ipAddress|hostName], [portNumber], and 
        [fileName] with the corresponding parameters, i.e.: ipAddress printed 
        by the server application, port number given to Server.py as parameter and
        the name of the file with the extension requested by the client.

The Client application will then check if the file already exists, and if not,
it will request the file to the server by using the appropriate 
header for the request.
If the file requested by the Client application exists, then the server will send it to
Client through a stream. Both applications will print informative messages once the
transmission has been completed. The client will close the socket, and the server will wait for
the next incoming connection.

If the process fails for any reason, an informative message will be printed.


DISCLAIMER: Both applications have been programmed exclusively for recreation and 
learning purposes only. I have prioritised code-readability over performance at all times.
Software not to be used for commercial purposes.



