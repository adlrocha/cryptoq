#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from requests import post
import cipher
import base64

clients = {}
addresses = {}

HOST = ''
PORT = 33001
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

client_socket = ""


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    clients[client] = name
    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            print("Message received")
            print(msg)
            nonce = str(msg).split("###")[1]
            msg = str(msg).split("###")[0]

            # Decoding using key
            r = post('http://127.0.0.1:5000/qkuser/B', json={"receiver": "A"})
            print(r.json())
            data = r.json()
            print("Symmetric key retrieved for A: " + data['status'])
            qkey = data['status']

            nonce = base64.decodebytes(bytes(nonce[:-3],encoding='utf-8'))

            print("Nonce")
            print(nonce)
            print("Ciphertext")
            msg = msg.replace("\\\\","\\")
            msg = msg[2:]
            print(msg)

            print("Qkey")
            print(qkey)

            # TODO: No termino de hacer que funcione el descifrar
            # por el tipo de dato y el nonce

            msg = cipher.decrypt(msg, qkey, nonce)

            # Sending encrypted confirmation
            client.send(bytes(msg.decode("utf8"), "utf8"))
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            print("quit")
            break


#r = post('http://127.0.0.1:5000/qkfactory', json={"hello": "world"})
#print(r.json())
#print("Symmetric key generated for A and B")

SERVER.listen(5)
print(HOST+":"+str(PORT))
print("Waiting for connection...")
ACCEPT_THREAD = Thread(target=accept_incoming_connections)
ACCEPT_THREAD.start()
ACCEPT_THREAD.join()
SERVER.close()



