#!/usr/bin/python

import select
import socket
import sys
import checkArgumentInput
import notify as notify

__author__ = 'Athanasios Garyfalos'
__editor__ = 'H. Kamran'

# telnet program example
BUFFER_RCV = 256

def initialization(client_socket, user_nickname):
    rcv_data = client_socket.recv(BUFFER_RCV)
    rcv_data = rcv_data.rstrip('\r\n')

    if 'Hello version' not in rcv_data:
        sys.stdout.write('User connection is terminated, Server is not configured for this client!\n')
        sys.stdout.flush()
        client_socket.close()
        sys.exit(1)
    else:
        client_socket.send('NICK ' + user_nickname)
        rcv_data = client_socket.recv(BUFFER_RCV)
        rcv_data = rcv_data.rstrip('\r\n')

        if 'ERROR' in rcv_data:
            sys.stdout.write(rcv_data + '\n')
            sys.stdout.flush()
            client_socket.close()
            sys.exit(1)
        else:
            return


def prompt():
    sys.stdout.write('<' + nickName + '> ')
    sys.stdout.flush()


# main function
if __name__ == '__main__':
    argsValidation = checkArgumentInput.ArgumentLookupError()

    try:
        host, port, nickName = argsValidation.validate_argument_input(sys.argv)
    except ValueError as exception:
        print exception.message

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)

    # connect to remote host
    # noinspection PyBroadException
    try:
        s.connect((host, port))
    except:
        sys.stdout.write('Unable to connect\n')
        sys.stdout.flush()
        sys.exit(1)
    
    print "Hello " + nickName
    
    initialization(s, nickName)
    sys.stdout.write('Connected to remote host. Start sending messages\n')
    sys.stdout.flush()
    prompt()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list,
                                                                   [],
                                                                   [])

        for sock in read_sockets:
            # incoming message from remote server
            if sock == s:
                data = sock.recv(BUFFER_RCV)
                data = data.rstrip('\r\n')
                if 'ERROR' in data:
                    sys.stdout.write(data)
                    sys.stdout.flush()
                    sys.exit(1)
                else:
                    sys.stdout.write(data + '\n')
                    sys.stdout.flush()
                    prompt()

            # user entered a message
            else:
                msg = sys.stdin.readline()
                msg = msg.rstrip('\r\n')
                if len(msg) == 0:
                    sys.stdout.write('Please enter a non-empty message.\n')
                    sys.stdout.flush()
                    prompt()
                elif '/exit' in msg or '/quit' in msg:
                    sys.stdout.write('Logging you out of the chat, ' + nickName + '...\n')
                    sys.stdout.flush()
                    msg = 'MSG ' + msg
                    s.send(msg)
                    notify.notify("Client Chat", "", "You are now logged out of the chat, " + nickName + "...", sound=False)
                    s.close()
                    sys.exit(0)
                else:
                    msg = 'MSG ' + msg + '\n'
                    s.send(msg)
                    prompt()
