#!/usr/bin/env python2.7

import getopt
import logging
import os
import socket
import sys
import time
import re
# Constants

ADDRESS  = ''
HOST     = ''
PORT     = 80
PROGRAM  = os.path.basename(sys.argv[0])
LOGLEVEL = logging.INFO
REQUESTS = 1
PROCESSES = 1

# Utility Functions

def usage(exit_code=0):
        print >>sys.stderr, '''Usage: {program} [-r REQUESTS -p PROCESSES -v] URL

    Options:

        -h       Show this help message
        -v       Set logging to DEBUG level

        -r REQUESTS  Number of requests per process (default is 1)
        -p PROCESSES Number of processes (default is 1)
    '''.format(port=PORT, program=PROGRAM, address=ADDRESS)
        sys.exit(exit_code)

# TCPClient Class

class TCPClient(object):

    def __init__(self, address=ADDRESS, port=PORT):
        ''' Construct TCPClient object with the specified address and port '''
        self.logger  = logging.getLogger()                              # Grab logging instance
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Allocate TCP socket
        self.address = address                                          # Store address to listen on
        self.port    = int(PORT)                                        # Store port to lisen on

    def run(self):
        try:
            # CONNECT TO SERVER AND CREATE FILE OBJECT
            self.socket.connect((self.address, self.port))
            self.stream = self.socket.makefile('w+')
        except socket.error as e:
            self.logger.error('Could not connect to {}:{}: {}'.format(self.address, self.port, e))
            sys.exit(1)

        # DISPLAY REQUESTED DEBUGGING INFORMATION
        self.logger.debug('URL: {}'.format(URL))
        self.logger.debug('HOST: {}'.format(HOST))
        self.logger.debug('PORT: {}'.format(PORT))
        self.logger.debug('PATH: /')
        self.logger.debug('Connected to {}:{}...'.format(self.address, self.port))

        # SEND THE REQUEST, AND PRINT THE RESPONSE
        try:
            self.logger.debug('Sending Request...')
            self.socket.sendall(REQUEST_STR)
            self.logger.debug('Recieving Response...')
            print self.socket.recv(4096)

        except Exception as e:
            self.logger.exception('Exception: {}', e)
        finally:
            self.finish()

    def finish(self):
        #Finish the connection by shutting down the socket, then deallocating it
        self.logger.debug('Finish')
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

# EchoClient Class

class HTTPClient(TCPClient):
    def handle(self):
        self.logger.debug('Handle')

        try:
            data = sys.stdin.readline()
            while data:
                # Send STDIN to Server
                self.stream.write(data)
                self.stream.flush()

                # Read from Server to STDOUT
                data = self.stream.readline()
                sys.stdout.write(data)

        except socket.error:
            pass    # Ignore socket errors

# Main Execution

if __name__ == '__main__':
# Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hvr:p:")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == '-v':
            LOGLEVEL = logging.DEBUG
        elif option == "-r":
        	REQUESTS = value
        elif option == "-p":
        	PROCESSES = value
     	else:
            usage(1)

    if len(arguments) >= 1:
        URL = arguments[0]
# End 

# Set up logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )
# End 

# Parse the URL and make request string
    try:
        #Using REGEX to parse the contents of the URL.....
        p = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        m = re.search(p,URL)

        HOST = m.group('host') 
        if m.group('port'):
            PORT = m.group('port') 

        # Generate the Request which will be sent to the HOST
        REQUEST_STR = ('GET / HTTP/1.1\r\n' + 'Host: ' + HOST + '\r\n' + '\r\n')

        # Obtain an ACTUAL address from the URL provided
        ADDRESS = socket.gethostbyname(HOST)
    except socket.gaierror as e:
        logging.error('Unable to lookup {}: {}'.format(ADDRESS, e))
        sys.exit(1)
# End 

# Instantiate and run client, using fork.

for process in range(int(PROCESSES)):
    #Ever Process Will compute average time by adding up the total time then dividing by number of requests
    totalTime = 0;

    for request in range(int(REQUESTS)):

        client = HTTPClient(ADDRESS)

        try:
            pid = os.fork()
        except OSError as e:# Error
            print >>sys.stderr, 'Unable to fork: {}'.format(e)
            sys.exit(1) 

        if pid == 0:    # Child

            try:
                client.run()
            except KeyboardInterrupt:
                sys.exit(0)

            sys.exit(0)

        else:           # Parent
            startTime = time.time()
            pid, status = os.wait()
            timeChange = time.time()-startTime
            totalTime = totalTime + timeChange

            client.logger.debug('{} | Elapsed Time: {:.2f} seconds'.format(pid, timeChange))
        #This is the end of the inner for loop, which makes all of the requests

    #The average time for all the requests is then calculated, and displayed
    averageTime = float(totalTime)/float(REQUESTS)
    client.logger.debug('{} | Average Elapsed Time: {:.2f} seconds'.format(pid, averageTime))


client.logger.debug('Process {} terminated with exit status {}'.format(pid, status))

