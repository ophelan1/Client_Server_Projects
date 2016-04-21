#!/usr/bin/env python2.7

import getopt
import logging
import os
import socket
import sys
import signal

# Constants

ADDRESS  = '0.0.0.0'
PORT     = 9999
BACKLOG  = 0
LOGLEVEL = logging.INFO
PROGRAM  = os.path.basename(sys.argv[0])
FORKING  = False
DOCROOT  = os.getcwd() + '/www/'
REQUEST  = []

# Utility Functions

def usage(exit_code=0):
    print >>sys.stderr, '''Usage: {program} [-p PORT -v]\n\nOptions:

    -h       Show this help message
    -f       Enable forking mode
    -v       Set logging to DEBUG level
    
    -d DOCROOT Set root directory (default is current directory)
    -p PORT  TCP Port to listen to (default is {port})\n'''.format(port=PORT, program=PROGRAM)
    sys.exit(exit_code)

# BaseHandler Class

class BaseHandler(object):

    def __init__(self, fd, address):
        self.logger  = logging.getLogger()        # Grab logging instance
        self.socket  = fd                         # Store socket file descriptor
        self.address = '{}:{}'.format(*address)   # Store address
        self.stream  = self.socket.makefile('w+') # Open file object from file descriptor

        self.debug('Connect')

    def debug(self, message, *args):
        message = message.format(*args)
        self.logger.debug('{} | {}'.format(self.address, message))

    def info(self, message, *args):
        message = message.format(*args)
        self.logger.info('{} | {}'.format(self.address, message))

    def warn(self, message, *args):
        message = message.format(*args)
        self.logger.warn('{} | {}'.format(self.address, message))

    def error(self, message, *args):
        message = message.format(*args)
        self.logger.error('{} | {}'.format(self.address, message))

    def exception(self, message, *args):
        message = message.format(*args)
        self.logger.exception('{} | {}'.format(self.address, message))

    def handle(self):
        self.debug('Handle')
        raise NotImplementedError

    def finish(self):
        self.debug('Finish')
        try:
            self.stream.flush()
        except socket.error as e:
            pass    # Ignore socket errors
        finally:
            self.socket.close()

# EchoHandler Class

class HTTPHandler(BaseHandler):
    def handle(self):

        self._parse_request()

        if os.environ['REQUEST_URI'] == '/favicon.ico':
            return

        print "\n1.The Requested URI is:", os.environ['REQUEST_URI']
        
        self.uripath = os.path.normpath(DOCROOT + os.environ['REQUEST_URI'])
        print "2. Path: ", self.uripath

        if not os.path.exists(self.uripath):
            print "3. PATH does not exist"
            self._handle_404error()

        elif os.path.isfile(self.uripath) and os.access(self.uripath, os.X_OK):
            print "3. It is an executable SCRIPT!"
            self._handle_script()

        elif os.path.isfile(self.uripath) and os.access(self.uripath, os.R_OK):
            print "3. It is a readable FILE!"
            self._handle_file()

        elif os.path.isdir(self.uripath) and os.access(self.uripath, os.R_OK):
            print "3. It is a readable DIRECTORY!"
            self._handle_dir()

        else:
            print "3. Error, not a standard file-type"



    def _parse_request(self):
        try:
            data = self.stream.readline().rstrip()
            if data:

                REQUEST = data.split()
                os.environ['REQUEST_METHOD'] = REQUEST[0]

                tmp    = REQUEST[1].split('?')
                os.environ['REQUEST_URI'] = tmp[0]
                if len(tmp) > 1:
                    os.environ['QUERY_STRING'] = tmp[1]
                else: 
                    os.environ['QUERY_STRING'] = ''


                self.stream.flush()
                data = self.stream.readline().rstrip()

            while data:
                line = data
                KEYinit = line.split(': ')
                keyFinal = 'HTTP_' + ('_'.join(KEYinit[0].split('-'))).upper()
                os.environ[keyFinal] = KEYinit[1]


                self.stream.flush()
                data = self.stream.readline().rstrip()

            # Print The envionrment
            '''print "Content-Type: text/plain\n\n"
            for key in os.environ.keys():
                print "%30s %s \n" % (key,os.environ[key])'''


        except socket.error:
            pass    # Ignore socket errors

    def _handle_404error(self):
        self.stream.write('''<!DOCTYPE html><html lang="en"><head><title>404 Error</title></head><body><div class="container"><div class="page-header"><h2>404 Error</h2></div><div class="thumbnail">
            <img src="http://files.sharenator.com/fun_with404_errors_60_uphaa_com-s450x322-82555.jpg" class="img-responsive">
            </div></div></body></html>''')
        self.stream.flush()

    def _handle_script(self):
        for line in os.popen(self.uripath):
            self.stream.write(line)
        self.stream.flush() 


    def _handle_file(self):

        for line in open(self.uripath):
            self.stream.write(line)
        self.stream.flush()

    def _handle_dir(self):

        dirs = sorted(os.listdir(self.uripath))
        print "The Directories are:", dirs, type(dirs)
        self.stream.write('''<!DOCTYPE html><html lang="en"><head><title>{path}</title></head><body><div class="container">
                            <div class="page-header"><h2>Directory Listing: {path}</h2></div><table class="table table-striped">
                            <thead><th>Type</th><th>Name</th><th>Size</th></thead><tbody>'''.format( path = os.environ['REQUEST_URI']))

        while len(dirs) > 0:
            print "FILE:", dirs[0]

            if os.environ['REQUEST_URI'] != '/':
                filePath = str(os.environ['REQUEST_URI']) + '/' +str(dirs[0])
            else:
                filePath = str(os.environ['REQUEST_URI']) + str(dirs[0])

            print "PATH:", filePath
            print "self.uripath:", self.uripath
            print "os.environ['REQUEST_URI']:", os.environ['REQUEST_URI']
            if not os.path.isdir(self.uripath + '/' + dirs[0]):
                fileSize = str(os.path.getsize(self.uripath + '/' + dirs[0])) + ' Bytes'
                fileType = 'file'

            else:
                fileSize = '-'
                fileType = 'dir'

            self.stream.write('''<tr><td>{type}</td><td><a href="{path}">{name}</a></td><td>{size}</td></tr>'''.format(type = fileType, path = filePath, name = dirs[0], size = fileSize))
            del dirs[0]

        self.stream.write('''</tbody></table></div></body></html>''')


# TCPServer Class

class TCPServer(object):

    def __init__(self, address=ADDRESS, port=PORT, handler=HTTPHandler):
        self.logger  = logging.getLogger()                              # Grab logging instance
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Allocate TCP socket
        self.address = address                                          # Store address to listen on
        self.port    = port                                             # Store port to lisen on
        self.handler = handler                                          # Store handler for incoming connections

    def run(self):
        try:
            # Bind socket to address and port and then listen
            self.socket.bind((self.address, self.port))
            self.socket.listen(BACKLOG)
        except socket.error as e:
            self.logger.error('Could not listen on {}:{}: {}'.format(self.address, self.port, e))
            sys.exit(1)

        self.logger.info('Listening on {}:{}...'.format(self.address, self.port))

        while True:
            # Accept incoming connection
            client, address = self.socket.accept()
            os.environ['REMOTE_ADDR'] = address[0]
            os.environ['REMOTE_HOST'] = address[0]
            os.environ['REMOTE_PORT'] = str(address[1])
            self.logger.debug('Accepted connection from {}:{}'.format(*address))

            # Instantiate handler, handle connection, finish connection
            try:
                handler = self.handler(client, address)
                handler.handle()
            except Exception as e:
                handler.exception('Exception: {}', e)
            finally:
                handler.finish()

# Main Execution

if __name__ == '__main__':
    # Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hfvp:d:")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == '-p':
            PORT = int(value)
        elif option == '-v':
            LOGLEVEL = logging.DEBUG
        elif option == '-d':
            DOCROOT = value
        elif option == '-f':
            FORKING = True
        else:
            usage(1)

    # Set logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    # Instantiate and run server
    server = TCPServer(port=PORT)

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)

