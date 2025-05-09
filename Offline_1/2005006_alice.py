import socket
import random
import importlib
import os
import struct

ecdh = importlib.import_module("2005006_ecdh")
aes = importlib.import_module("2005006_aes")

def send_file(sock, file_path, file_name):
    try:
        sock.send(struct.pack('!I', len(file_name)))
        sock.send(file_name.encode())
        
        # Get file size
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size}")
        
        # Send file size first (8 bytes)
        sock.send(struct.pack('!Q', file_size))
        
        # Send file in chunks
        with open(file_path, 'rb') as file:
            bytes_sent = 0
            while True:
                data = file.read(8192)  # Read in 8KB chunks
                if not data:
                    break
                sock.send(data)
                bytes_sent += len(data)
        
        print("\nFile sent successfully!")
        return True
    except Exception as e:
        print(f"\nError sending file: {e}")
        return False


def main():
    # Create socket
    s = socket.socket()
    port = 5006
    
    print("Waiting for Bob to connect...")
    s.connect(('127.0.0.1', port))
    print("Connected to Bob")
    
    # Initialize ECDH parameters
    ecdh.init(128)
    
    a_private = random.randrange(1, ecdh.P)
    a_public = ecdh.scalar_mult(a_private, ecdh.G)

    # Send ECDH parameters to Bob
    params = f"{ecdh.a},{ecdh.b},{ecdh.G[0]},{ecdh.G[1]},{ecdh.P},{a_public[0]},{a_public[1]}"
    s.send(params.encode())

    # Receive Bob's public key
    b_public_str = s.recv(1024).decode()

    b_public_x, b_public_y = map(int, b_public_str.split(','))
    b_public = (b_public_x, b_public_y)

    # Calculate shared secret
    shared_secret = ecdh.scalar_mult(a_private, b_public)
    # Remove '0x' prefix
    # Pad with zeros on the left if less than 32 hex chars, or take first 32 if longer
    shared_key_hex = hex(shared_secret[0])[2:]  
    shared_key_hex = shared_key_hex.zfill(32)[:32]

    # Send ready signal
    s.send("READY".encode())
    ready_response = s.recv(1024).decode()
    
    if ready_response == "READY":
        continue_communication = 'y'
        
        # Initialize AES with shared key
        aes.round_keys.clear()
        aes.round_keys.append(aes.BitVector(hexstring=shared_key_hex))
        aes.key_expansion(shared_key_hex, 1)

        while continue_communication.lower() == 'y':
            try:
                print("\nChoose operation:")
                print("1. Encrypt/Decrypt plaintext")
                print("2. Encrypt/Decrypt file")
                choice = input("Enter your choice (1 or 2): ")
                s.send(choice.encode())
                if choice == "1":
                    plaintext = input("\nPlaintext:\nIn ASCII: ")
                    plaintext_hex = plaintext.encode('utf-8').hex()
                    aes.print_string(plaintext_hex, "hex", False)
                    
                    # Encryption
                    ciphertext_hex = aes.encrypt_data(plaintext, False)

                    ciphertext = bytes.fromhex(ciphertext_hex).decode('utf-8', errors='ignore')
                    
                    print("\nSending Ciphered Text to Bob:")
                    aes.print_string(ciphertext_hex, "hex", False)
                    aes.print_string(ciphertext, "ascii", False)
                    print()
                    s.send(ciphertext_hex.encode())

                elif choice == "2":
                    file_path = input("Enter file path to encrypt: ")
                    if not os.path.exists(file_path):
                        print("File does not exist!")
                        continue

                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                    
                    print("Encrypting file...")
                    # Encryption
                    ciphertext_hex = aes.encrypt_data(file_content, True)
                    file_name = os.path.basename(file_path)
                    encrypted_file_path = "encrypted_" + file_name
                    with open(encrypted_file_path, 'wb') as file:
                        file.write(bytes.fromhex(ciphertext_hex))

                    print(f"Encrypted file saved as: {encrypted_file_path}")
                    
                    # Send the encrypted file
                    print("\nSending encrypted file to Bob...")
                    if send_file(s, encrypted_file_path, file_name):
                        print("File transfer completed!")
                    else:
                        print("File transfer failed!")

                continue_communication = input("Continue communication? (y/n): ")
                s.send(continue_communication.encode())
                
            except ConnectionAbortedError:
                print("Connection was aborted by Bob")
                break
            except ConnectionResetError:
                print("Connection was reset by Bob")
                break
            except BrokenPipeError:
                print("Connection was broken (Bob might have closed)")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    print("Closing connection with Bob")
    s.close()

if __name__ == "__main__":
    main()     