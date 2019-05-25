from nacl import utils, secret
from mim import generateQK
import base64

# Generate Alice and Bob keys
# The symmetric key for both of them are produced by the quantum circuit
"""
qkeyarray = generateQK(256)

alice_key = qkeyarray.get('A')
bob_key = qkeyarray.get('B')
print(alice_key)
print(bob_key)

qkey=int(alice_key, 2).to_bytes((len(alice_key)+7) // 8, byteorder='little')
qkeyb=int(bob_key, 2).to_bytes((len(bob_key)+7) // 8, byteorder='little')
print('Alice key: '+str(qkey))
print('Bob key:   '+str(qkeyb))
"""

def encrypt(message, qkey,nonce):
    print("Encryption")
    box = secret.SecretBox(base64.decodebytes(bytes(qkey,encoding='utf-8')))
    encrypted = box.encrypt(bytes(message, encoding="utf-8"),nonce)
    ctext = encrypted.ciphertext
    return ctext


def decrypt(ctext, qkey, nonce):
    print("Decryption")
    box = secret.SecretBox(base64.decodebytes(bytes(qkey,encoding='utf-8')))
    print(type(ctext))
    plain = box.decrypt(bytes(ctext,encoding='utf-8'),nonce)
    return plain

"""
qkeyarray = generateQK(256)

alice_key = qkeyarray.get('A')
bob_key = qkeyarray.get('B')
print(alice_key)
print(bob_key)

qkey=int(alice_key, 2).to_bytes((len(alice_key)+7) // 8, byteorder='little')
qkeyb=int(bob_key, 2).to_bytes((len(bob_key)+7) // 8, byteorder='little')
print('Alice key: '+str(qkey))
print('Bob key:   '+str(qkeyb))

b64qkey = base64.encodebytes(qkey).decode('utf-8')

qkey = base64.decodebytes(bytes(b64qkey,encoding='utf-8'))

box = secret.SecretBox(qkey)

nonce = utils.random(secret.SecretBox.NONCE_SIZE)
nonce = base64.encodebytes(nonce).decode("utf-8")
print(nonce)
nonce = base64.decodebytes(bytes(nonce,encoding='utf-8'))

message = b"CryptoQ"
# Alice would encrypt her message
encrypted = box.encrypt(message, nonce)
print("-------------------------------")
ctext = encrypt('hola',b64qkey,nonce)
print(ctext)
print("-------------------------------")
plain = decrypt(ctext, b64qkey, nonce)
print(plain)
"""