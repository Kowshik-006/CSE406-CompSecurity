import socket
import random
import importlib

ecdh = importlib.import_module("2005006_ecdh")
aes = importlib.import_module("2005006_aes")

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
        
        while True:
            try:
                # Receive encrypted message
                ciphertext_hex = conn.recv(1024).decode()
                print("\nReceived Ciphered Text from Alice")
                ciphertext = bytes.fromhex(ciphertext_hex).decode('utf-8', errors='ignore')
                aes.print_string(ciphertext_hex, "hex", False)
                aes.print_string(ciphertext, "ascii", False)
                
                # Initialize AES with shared key
                aes.round_keys.clear()
                aes.round_keys.append(aes.BitVector(hexstring=shared_key_hex))
                aes.key_expansion(shared_key_hex, 1)
                
                # Decrypt message
                iv = aes.BitVector(hexstring=ciphertext_hex[:32])
                ciphertext_hex = ciphertext_hex[32:]
                deciphertext_hex = ""
                
                for i in range(0, len(ciphertext_hex), 32):
                    ciphertext_chunk = aes.BitVector(hexstring=ciphertext_hex[i:i+32])
                    deciphertext_chunk = aes.get_plaintext(ciphertext_chunk)
                    deciphertext_chunk = deciphertext_chunk ^ iv
                    deciphertext_hex += deciphertext_chunk.get_bitvector_in_hex()
                    iv = ciphertext_chunk.deep_copy()

                deciphertext = bytes.fromhex(deciphertext_hex).decode('utf-8', errors='ignore')
                print("\nDeciphered Text:")
                print("Before Unpadding:")
                aes.print_string(deciphertext_hex, "hex", False)
                aes.print_string(deciphertext, "ascii", False)
                
                # Remove padding
                padding = int(deciphertext_hex[-2:], 16)
                deciphertext_hex = deciphertext_hex[:-2*padding]
                deciphertext = bytes.fromhex(deciphertext_hex).decode('utf-8', errors='ignore')
                print("\nAfter Unpadding:")
                aes.print_string(deciphertext_hex, "hex", False)
                aes.print_string(deciphertext, "ascii", False)
                print()

                continue_communication = conn.recv(1024).decode()
                if continue_communication == 'n' or continue_communication == 'N':
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