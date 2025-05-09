import socket
import random
import importlib
import os
import struct

ecdh = importlib.import_module("2005006_ecdh")
aes = importlib.import_module("2005006_aes")

def receive_file(sock, file_path):
    try:
        # Receive file size first
        file_size_data = sock.recv(8)
        file_size = struct.unpack('!Q', file_size_data)[0]
        
        print(f"File size: {file_size}")
        # Receive file in chunks
        received_size = 0
        with open(file_path, 'wb') as file:
            while received_size < file_size:
                data = sock.recv(min(8192, file_size - received_size))
                if not data:
                    break
                file.write(data)
                received_size += len(data)
        
        print("\nFile received successfully!")
        return True
    except Exception as e:
        print(f"\nError receiving file: {e}")
        return False

def main():
    # Create socket
    s = socket.socket()
    port = 5006
    s.bind(('127.0.0.1', port))
    s.listen(1)
    print("Waiting for Alice to connect...")
    
    # Accept connection from Alice
    conn, addr = s.accept()
    print("Connected to Alice")

    # Receive ECDH parameters from Alice
    params = conn.recv(1024).decode()
    a, b, x_g, y_g, P, a_public_x, a_public_y = map(int, params.split(','))
    G = (x_g, y_g)
    ecdh.a = a
    ecdh.b = b
    ecdh.G = G
    ecdh.P = P
    a_public = (a_public_x, a_public_y)

    b_private = random.randrange(1, P)
    b_public = ecdh.scalar_mult(b_private, G)

    # Send Bob's public key to Alice
    b_public_str = f"{b_public[0]},{b_public[1]}"
    conn.send(b_public_str.encode())

    # Calculate shared secret
    shared_secret = ecdh.scalar_mult(b_private, a_public)
    
    # Remove '0x' prefix
    # Pad with zeros if less than 32 hex chars, or take first 32 if longer
    shared_key_hex = hex(shared_secret[0])[2:]  
    shared_key_hex = shared_key_hex.zfill(32)[:32]

    # Wait for ready signal and respond
    ready_signal = conn.recv(1024).decode()
    if ready_signal == "READY":
        conn.send("READY".encode())
        # Initialize AES with shared key
        aes.round_keys.clear()
        aes.round_keys.append(aes.BitVector(hexstring=shared_key_hex))
        aes.key_expansion(shared_key_hex, 1)
        
        while True:
            try:
                choice = conn.recv(1).decode()
                if choice == "1":
                    print("\nReceiving encrypted message from Alice...")
                    # Receive encrypted message
                    ciphertext_hex = conn.recv(1024).decode()
                    print("Received Ciphered Text from Alice\n")
                    
                    # Decryption
                    deciphertext_hex = aes.decrypt_data(ciphertext_hex, False)
                    
                    print("After Unpadding:")
                    aes.print_string(bytes.fromhex(deciphertext_hex).decode('utf-8', errors='ignore'), "ascii", False)
                    aes.print_string(deciphertext_hex, "hex", False)
                    print()

                elif choice == "2":
                    # Receive encrypted file
                    print("\nReceiving encrypted file from Alice...")

                    name_length = struct.unpack('!I', conn.recv(4))[0]
                    file_name = conn.recv(name_length).decode()

                    encrypted_file_path = "received_encrypted_" + file_name
                    if receive_file(conn, encrypted_file_path):
                        print(f"File received and saved as: {encrypted_file_path}")
                        print("Decrypting file...")
                        # Read the encrypted file
                        with open(encrypted_file_path, 'rb') as file:
                            encrypted_content = file.read()
                        
                        # Decrypt the file
                        decrypted_content = aes.decrypt_data(encrypted_content.hex(), True)
                        
                        # Save the decrypted file
                        decrypted_file_path = "decrypted_" + file_name
                        with open(decrypted_file_path, 'wb') as file:
                            file.write(bytes.fromhex(decrypted_content))
                        
                        print(f"File decrypted and saved as: {decrypted_file_path}")
                    else:
                        print("Failed to receive file!")

                continue_communication = conn.recv(1).decode()
                if continue_communication.lower() == 'n':
                    break
                    
            except ConnectionAbortedError:
                print("Connection was aborted by Alice")
                break
            except ConnectionResetError:
                print("Connection was reset by Alice")
                break
            except BrokenPipeError:
                print("Connection was broken (Alice might have closed)")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

    print("Closing connection with Alice and the socket")
    conn.close()
    s.close()

if __name__ == "__main__":
    main() 