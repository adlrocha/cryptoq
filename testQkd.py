from nacl import utils, secret
from qkd import generateQK

# Generate Alice and Bob keys
# The symmetric key for both of them are produced by the quantum circuit

print('[*]Generating 256 bits quantum symmetric keys: without spy')
qkeyarray = generateQK(256)
print('Key error counter: ', qkeyarray['errorCounter'], 'isValid?', qkeyarray['valid'])
alice_key = qkeyarray.get('A')
bob_key = qkeyarray.get('B')
# print(alice_key)
# print(bob_key)

qkey=int(alice_key, 2).to_bytes((len(alice_key)+7) // 8, byteorder='little')
qkeyb=int(bob_key, 2).to_bytes((len(bob_key)+7) // 8, byteorder='little')
print('Alice key: '+str(qkey))
print('Bob key:   '+str(qkeyb))
print('================================================')

# Secret Box (Salsa20withPoly1305 algorithm)
# In this step both Alice and Bob should have simultaneously the symmetric key
box = secret.SecretBox(qkey)
boxb = secret.SecretBox(qkeyb)

# Maybe the nonce can also be generated by a quantum circuit (Team11)
nonce = utils.random(secret.SecretBox.NONCE_SIZE)
# print(nonce)

# Message to be encrypted and decrypted
message = b"CryptoQ"
print('[*] Message to be encrypted: ')
print(message)

# Alice would encrypt her message
encrypted = box.encrypt(message, nonce)

ctext = encrypted.ciphertext
print('[*] Encrypted message by A: ')
print(ctext)


# Bob would decrypt Alice's message
plain = boxb.decrypt(ctext, nonce)
print('[*] Plaintext decrypted by B: ')
print(plain)

print('\n***********************************************\n')


print('[*]Generating 256 bits quantum symmetric keys: with eavsdropper')
qkeyarray = generateQK(256, 0.5, 0.5)
print('Key error counter: ', qkeyarray['errorCounter'], 'isValid?', qkeyarray['valid'])
alice_key = qkeyarray.get('A')
bob_key = qkeyarray.get('B')
# print(alice_key)
# print(bob_key)

qkey=int(alice_key, 2).to_bytes((len(alice_key)+7) // 8, byteorder='little')
qkeyb=int(bob_key, 2).to_bytes((len(bob_key)+7) // 8, byteorder='little')
print('Alice key: '+str(qkey))
print('Bob key:   '+str(qkeyb))
print('================================================')


# Secret Box (Salsa20withPoly1305 algorithm)
# In this step both Alice and Bob should have simultaneously the symmetric key
box = secret.SecretBox(qkey)
boxb = secret.SecretBox(qkeyb)

# Maybe the nonce can also be generated by a quantum circuit (Team11)
nonce = utils.random(secret.SecretBox.NONCE_SIZE)
# print(nonce)

# Message to be encrypted and decrypted
message = b"CryptoQ"
print('[*] Message to be encrypted: ')
print(message)

# Alice would encrypt her message
encrypted = box.encrypt(message, nonce)

ctext = encrypted.ciphertext
print('[*] Encrypted message by A: ')
print(ctext)


# Bob would decrypt Alice's message
plain = boxb.decrypt(ctext, nonce)
print('[*] Plaintext decrypted by B: ')
print(plain)

