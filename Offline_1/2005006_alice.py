import socket
import random
import importlib

ecdh = importlib.import_module("2005006_ecdh")
aes = importlib.import_module("2005006_aes")

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
        while continue_communication == 'y' or continue_communication == 'Y':
            try:
                plaintext = input("\nPlaintext:\nIn ASCII: ")
                plaintext_hex = plaintext.encode('utf-8').hex()
                aes.print_string(plaintext_hex, "hex", False)
                
                # Initialize AES with shared key
                aes.round_keys.clear()
                aes.round_keys.append(aes.BitVector(hexstring=shared_key_hex))
                aes.key_expansion(shared_key_hex, 1)
                
                # Encryption
                padding = 16 - (len(plaintext) % 16)
                
                for i in range(padding):
                    plaintext += chr(padding)
                plaintext_hex = plaintext.encode('utf-8').hex()
                
                aes.print_string(plaintext, "ascii", True)
                aes.print_string(plaintext_hex, "hex", True)
                print()
                
                iv = aes.generate_random_iv()
                original_iv = iv.deep_copy()
                ciphertext_hex = original_iv.get_bitvector_in_hex()
                
                for i in range(0, len(plaintext_hex), 32):
                    plaintext_chunk = aes.BitVector(hexstring=plaintext_hex[i:i+32])
                    plaintext_chunk = plaintext_chunk ^ iv
                    ciphertext_chunk = aes.get_ciphertext(plaintext_chunk)
                    ciphertext_hex += ciphertext_chunk.get_bitvector_in_hex()
                    iv = ciphertext_chunk.deep_copy()

                ciphertext = bytes.fromhex(ciphertext_hex).decode('utf-8', errors='ignore')

                print("Sending Ciphered Text to Bob:")
                aes.print_string(ciphertext_hex, "hex", False)
                aes.print_string(ciphertext, "ascii", False)
                print()
                s.send(ciphertext_hex.encode())

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