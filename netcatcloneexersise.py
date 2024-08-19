# some of the imports being used for this
import argparse
import socket
import subprocess  # learn this first and what it does
import shlex
import sys
import threading


# execute shell commands
# captures the output of the command and returns as strings
def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     shell=True)
    return output


# set to initialize the parser
parser = argparse.ArgumentParser(description="a simple netcat clone")

# set the commands to use
parser.add_argument('-c', '--command', help="command shell", action='store_true')
parser.add_argument('-e', '--execute', help="-execute command")
parser.add_argument('-p', '--port', help="specified port", type=int)
parser.add_argument('-u', '--upload', help="upload file")
parser.add_argument('-l', '--listen', help="start a listener", action='store_true')
parser.add_argument('-t', '--target', help="Target ip ", type=str)

# pass args
args = parser.parse_args()


# if true set buffer to an empty string


# buffer is passed as bytes
# will create the net cat class

# creating the net cat class that
# takes args from stdin and buffer(which is  optional)
class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # his line of code allows the socket to reuse a local address (port)
        # that might still be in use by a previous connection.
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        # if the listen argument is provided
        # call the listen method
        if self.args.listen:
            self.listen()
        # if no args is found call the send method
        else:
            self.send()

    def send(self):
        # connect to the provided ip and port
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)  # if buffer is provided send

        try:
            while True:
                recv_len = 1
                response = ''
                # receive data
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    # if any response is provided
                    # add to the buffer and encoded
                    buffer ='Hello there'
                    print(buffer)
                    self.socket.send(buffer.encode())
        # terminate the connection
        except KeyboardInterrupt as key:
            print(f"terminated {key}")
            self.socket.close()
            sys.exit()

    # creating the function that listen for
    # client connection
    # server connection
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        # set the number of connection you handle
        try:
            self.socket.listen(5)
            print(f"listening for connection on {self.args.target}:{self.args.port}")
            # use threading to allows you to handle listens simultaneously
            while True:
                client_socket, addr = self.socket.accept()
                print(f'accepted connection from{addr}')
                client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt as k:
            print(f'progam has been killed{k}')
            self.socket.close()
            sys.exit()

    # handles the functions of most of the args passed in
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode(), )

        elif self.args.upload:
            file_buffer = b' '
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                    print(len(file_buffer))
                else:
                    break
                # write the content of the file buffer to a file
                # and send it
            with open(self.args.upload, 'wb') as file:
                file.write(file_buffer)
                message = f'file saved {self.args.upload}'
                client_socket.send(message.encode())
            # handles the command line
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'Remote_Command: #>')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                        response = execute(cmd_buffer.decode())
                        # clears the buffer
                        if response:
                            client_socket.send(response.encode())
                            cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if args.listen:
    buffer = ''
else:
    buffer = sys.stdin.read()  # if not read from standard input into the buffer

nc = NetCat(args, buffer.encode())
nc.run()

# the program operates weirdly in a sense that when a command is executed with the -c flag
# the terminal which it shows up on prints multiple lines of Remote command and i really don't know why
# despite clearing the buffer
# also do not how to handle stdout with the command as well say i use netstat or ipconfig it doesn't show anything
# haven't tested the upload yet
# the execute command works it just prints the output of the command in the terminal but in a rather scattered way
