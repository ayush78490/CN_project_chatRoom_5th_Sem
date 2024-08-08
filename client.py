import threading
import socket
import argparse
import os
import sys
import tkinter as tk


class Send(threading.Thread):
    
    #Listning for user input from command line


    #sock the connected sock object

    #name (str) : The user


    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        # Listen for user input from commandline and send to the server
        print('{}: '.format(self.name), end='')
        sys.stdout.flush()
        message = sys.stdin.readline()[:-1]

        #if we type "QUIT" we leave the chatroom
        if message == "QUIT":
            self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('ascii'))
            self.sock.close()
            sys.exit(0)

        else:
            self.sock.sendall('{}: {} '.format(self.name, message).encode('ascii'))
    
        print('\nQutting....')
        self.sock.close()
        sys.exit(0)


class Recive(threading.Thread):
    #Listining for incomming messages
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.message = None

    def run(self):
        while True:
            message = self.sock.recv(1024).decode('ascii')

            if message:
                if self.message:
                    self.message.insert(tk.END, message)
                    print('Hi')
                    print('\r{}\n{}: '.format(message,self.name), end='')
                else:
                    print('\r{}\n{}: '.format(message,self.name), end='')

            else:
                print('\n No. we have lost connection to the server')
                print('\nQutting....')
                self.sock.close()
                sys.exit(0)



class Client:
    #Manage the client server connection and integration of GUI

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None


    def start(self):
        print('Trying to connect to {}:{}....'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Succefully connected to {}:{}: '.format(self.host, self.port))

        print()
        self.name = input('Your name: ')
        print()

        print('Welcome, {}! Getting ready to send and recive messages...'.format(self.name, self.port))

        #Create send and recive threads 
        send = Send(self.sock, self.name)
        recive = Recive(self.sock, self.name)

        #Start send and recive Thread
        send.start()
        recive.start()

        self.sock.sendall('server: {} has joined the chat. say whatsup!'.format(self.name).encode('ascii'))
        print("\r Ready! Leave the chatRoom anytime by typing 'QUIT'\n")
        print('{}: '.format(self.name, end= ''))
        return recive

    def send(self, textInput):
        #Send text input data from GUI
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, '{}: {}'.format(self.name, message))

        #Type QUIT to leave the chat
        if message == "QUIT":
            self.sock.sendall('Server: {} has left the chat. '.format(self.name).encode('ascii'))
            print('\nQutting....')
            self.sock.close()
            sys.exit(0)

            #SEND message for broadcasting
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

def main(host, port):
    #initilize and run our GUI app
    client = Client(host, port)
    recive = client.start()

    window = tk.Tk()
    window.title("ChatRoom")

    fromMessage = tk.Frame(master=window)
    scrollbar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    client.messages = messages
    recive.messages = messages

    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry =tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "wirte your message here.")

    btnSend = tk.Button(
        master=window,
        text='Send',
        command=lambda: client.send(textInput)
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, padx=10, sticky="ew")

    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=1)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument('host', help='Interface the server linsten at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')

    args = parser.parse_args()

    main(args.host, args.p)

        
