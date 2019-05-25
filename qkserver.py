#!/usr/bin/python3
from flask import Flask, request
from flask_restful import Resource, Api
from mim import generateQK
from json import dumps
import base64

app = Flask(__name__)
api = Api(app)

map = {}


class QKServerKeyFactory(Resource):
    def get(self):
        print(map)
        return dumps(map)

    def post(self):

        print(request.json)
        #sender = request.json['sender']
        #receiver = request.json['receiver']

        try:
            qkeyarray = generateQK(256)

            alice_key = qkeyarray.get('A')
            bob_key = qkeyarray.get('B')
            print(alice_key)
            print(bob_key)

            qkey = int(alice_key, 2).to_bytes((len(alice_key) + 7) // 8, byteorder='little')
            qkeyb = int(bob_key, 2).to_bytes((len(bob_key) + 7) // 8, byteorder='little')
            print(qkey)
            print(qkeyb)

            b64qkey = base64.encodebytes(qkey).decode('utf-8')
            b64qkeyb = base64.encodebytes(qkeyb).decode('utf-8')

            print(b64qkey)
            print(b64qkeyb)

            map['A']={"B":b64qkey}
            map['B']={"A":b64qkeyb}

            print(map)

            return {'status': 'success'}
        except:
            return {'status':'failed'}


class QKServerUserKeyService(Resource):
    def get(self, user_id):
        return {'status': 'success'}

    def post(self, user_id):
        print(request.json)

        dicc = map.get(user_id)
        print(dicc)
        receiver = request.json['receiver']

        key = dicc.get(receiver)

        return {'status': key}


api.add_resource(QKServerKeyFactory, '/qkfactory')
api.add_resource(QKServerUserKeyService, '/qkuser/<user_id>')

if __name__ == '__main__':
    app.run()