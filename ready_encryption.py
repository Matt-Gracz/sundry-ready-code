import base64

# Load key in
#key = 

# Encryption function
def simple_encrypt(password):
    # Convert the password to bytes
    password_bytes = password.encode('utf-8')
    
    # Apply a basic transformation using the key
    transformed_bytes = bytearray([b + key for b in password_bytes])
    
    # Encode using base64
    encrypted_password = base64.b64encode(transformed_bytes).decode('utf-8')
    
    return encrypted_password

# Decryption function
def simple_decrypt(encrypted_password):
    # Decode the encrypted password using base64
    encrypted_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
    
    # Reverse the transformation using the key
    transformed_bytes = bytearray([b - key for b in encrypted_bytes])
    
    # Convert the bytes back to string
    decrypted_password = transformed_bytes.decode('utf-8')
    
    return decrypted_password

# Test the functions
def test_encryption():
  test_password = "mySecurePassword"
  encrypted_password = simple_encrypt(test_password)
  decrypted_password = simple_decrypt(encrypted_password)
  
  print(f'plain text: {test_password}, encrypted: {encrypted_password}, decrypted: {decrypted_password})
