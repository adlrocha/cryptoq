#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from nacl import utils, secret
import tkinter
from requests import get,post
import cipher
import base64
import json

clients = {}
addresses = {}

BUFSIZ = 1024

connected = False


def receive():
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except OSError:
            break


def send():  # event is passed by binders.
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    r = post('http://127.0.0.1:5000/qkuser/A', json={"receiver":"B"})
    print(r.json())
    data = r.json()
    print("Symmetric key retrieved for B: "+data['status'])
    qkey = data['status']
    nonce = utils.random(secret.SecretBox.NONCE_SIZE)

    print("Nonce")
    print(nonce)
    print("Message")
    print(msg)
    ctext = cipher.encrypt(msg, qkey, nonce)
    print("Ciphertext")
    print(ctext)
    print("Qkey")
    print(qkey)

    texttosend = str(ctext)+"###"+base64.encodebytes(nonce).decode("utf-8")
    client_socket.send(bytes(texttosend, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        top.quit()


def on_closing():
    top.destroy()


top = tkinter.Tk()
top.title("CryptoChat")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()
host = tkinter.StringVar()
host.set("localhost")
port = tkinter.StringVar()
port.set("33001")
my_msg.set("A")
scrollbar = tkinter.Scrollbar(messages_frame)

msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

HOST = 'localhost'
PORT = 33001
BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()


