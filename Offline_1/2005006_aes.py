import importlib
import os
import time

BitVector = importlib.import_module("BitVector").BitVector

round_keys = []

AES_modulus = BitVector(bitstring='100011011')

Sbox = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

InvSbox = (
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
)

Mixer = [
    [BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03")],
    [BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02")]
]

InvMixer = [
    [BitVector(hexstring="0E"), BitVector(hexstring="0B"), BitVector(hexstring="0D"), BitVector(hexstring="09")],
    [BitVector(hexstring="09"), BitVector(hexstring="0E"), BitVector(hexstring="0B"), BitVector(hexstring="0D")],
    [BitVector(hexstring="0D"), BitVector(hexstring="09"), BitVector(hexstring="0E"), BitVector(hexstring="0B")],
    [BitVector(hexstring="0B"), BitVector(hexstring="0D"), BitVector(hexstring="09"), BitVector(hexstring="0E")]
]

Rcon = [
        BitVector(hexstring="01000000"),
        BitVector(hexstring="02000000"),
        BitVector(hexstring="04000000"),
        BitVector(hexstring="08000000"),
        BitVector(hexstring="10000000"),
        BitVector(hexstring="20000000"),
        BitVector(hexstring="40000000"),
        BitVector(hexstring="80000000"),
        BitVector(hexstring="1B000000"),
        BitVector(hexstring="36000000")
]

def generate_random_iv():
    random_bytes = os.urandom(16)
    iv = BitVector(rawbytes=random_bytes)
    return iv


def g(bv, round_num):
    bv = bv << 8
    for i in range(0,32,8):
        row = bv[i : i+4].intValue()
        col = bv[i+4 : i+8].intValue()
        value = Sbox[row * 16 + col]
        bv[i : i+8] = BitVector(intVal=value, size=8)
    bv = bv ^ Rcon[round_num - 1]
    return bv

def key_expansion(key_hex, round_num, w=None):
    if w is None:
        w = []
        for i in range(0,32,8):
            w.append(BitVector(hexstring=key_hex[i : i+8]))

    if round_num == 11:
        return

    bv = g(w[-1].deep_copy(), round_num)

    # Generate the next 4 words
    for i in range(4):
        if i == 0:
            w.append(w[-4] ^ bv) 
        else:
            w.append(w[-1] ^ w[-4])

    # Combine the 4 words to form the round key
    round_key = w[-4] + w[-3] + w[-2] + w[-1]
    round_keys.append(round_key)

    key_expansion(key_hex, round_num + 1, w)


def get_ciphertext(plaintext_bv):
    ciphertext_bv  = plaintext_bv ^ round_keys[0]

    for i in range(1, 11):
        # SubBytes
        for j in range(0,128,8):
            row = ciphertext_bv[j : j+4].intValue()
            col = ciphertext_bv[j+4 : j+8].intValue()
            value = Sbox[row * 16 + col]
            ciphertext_bv[j : j+8] = BitVector(intVal=value, size=8)

        # ShiftRows
        rows = []
        for j in range(4):
            row = BitVector(size=0)
            for k in range(4):
                index = j*8 + k*32
                row += ciphertext_bv[index : index+8]
            rows.append(row)

        rows[1] = rows[1] << 8
        rows[2] = rows[2] << 16
        rows[3] = rows[3] << 24

        ciphertext_bv = BitVector(size=0)

        for j in range(0,32,8):
            for k in range(4):
                ciphertext_bv += rows[k][j : j+8]

        if i != 10:
            # MixColumns
            rows = []

            for j in range(4):
                row = BitVector(size=0)
                for k in range(4):
                    temp = BitVector(size=8)
                    for l in range(4):
                        index = k*32 + l*8
                        temp = temp ^ Mixer[j][l].gf_multiply_modular(ciphertext_bv[index : index + 8], AES_modulus, 8)
                    row += temp
                rows.append(row)

            ciphertext_bv = BitVector(size=0)
            for j in range(0,32,8):
                for k in range(4):
                    ciphertext_bv += rows[k][j : j+8]

        # AddRoundKey
        ciphertext_bv = ciphertext_bv ^ round_keys[i]

    return ciphertext_bv

def get_plaintext(ciphertext_bv):
    plaintext_bv = ciphertext_bv ^ round_keys[10]
    for i in range(9, -1, -1):
        # InvShiftRows
        rows = []
        for j in range(4):
            row = BitVector(size=0)
            for k in range(4):
                index = j*8 + k*32
                row += plaintext_bv[index : index+8]
            rows.append(row)

        rows[1] = rows[1] >> 8
        rows[2] = rows[2] >> 16
        rows[3] = rows[3] >> 24

        plaintext_bv = BitVector(size=0)

        for j in range(0,32,8):
            for k in range(4):
                plaintext_bv += rows[k][j : j+8]

        # InvSubBytes
        for j in range(0,128,8):
            row = plaintext_bv[j : j+4].intValue()
            col = plaintext_bv[j+4 : j+8].intValue()
            value = InvSbox[row * 16 + col]
            plaintext_bv[j : j+8] = BitVector(intVal=value, size=8)

        # InvAddRoundKey
        plaintext_bv = plaintext_bv ^ round_keys[i]

        if i != 0:
            # InvMixColumns
            rows = []
            for j in range(4):
                row = BitVector(size=0)
                for k in range(4):
                    temp = BitVector(size=8)
                    for l in range(4):
                        index = k*32 + l*8
                        temp = temp ^ InvMixer[j][l].gf_multiply_modular(plaintext_bv[index : index + 8], AES_modulus, 8)
                    row += temp
                rows.append(row)

            plaintext_bv = BitVector(size=0)
            for j in range(0,32,8):
                for k in range(4):
                    plaintext_bv += rows[k][j : j+8]

    return plaintext_bv
        
def print_string(string, type, padded):
    if(type == "hex"):
        if padded:
            print("In HEX (After Padding):", end=" ")
        else:
            print("In HEX:", end=" ")
        for i in range(len(string) // 2):
            print(string[i*2 : i*2+2], end=" ")
    elif(type == "ascii"):
        if padded:
            print("In ASCII (After Padding):", end=" ")
        else:
            print("In ASCII:", end=" ")
        for i in range(len(string)):
            print(string[i], end="")

    print()

def encrypt_data(data, is_file=False):    
    # Calculate padding
    padding = 16 - (len(data) % 16)
    if is_file:
        for _ in range(padding):
            data += bytes([padding])
        # For file, data is already in bytes
        data_hex = data.hex()
    else:
        for _ in range(padding):
            data += chr(padding)
        data_hex = data.encode('utf-8').hex()
        print_string(data, "ascii", True)
        print_string(data_hex, "hex", True)
    

    # Encryption
    iv = generate_random_iv()
    original_iv = iv.deep_copy()
    ciphertext_hex = original_iv.get_bitvector_in_hex()
    for i in range(0, len(data_hex), 32):
        data_chunk = BitVector(hexstring=data_hex[i:i+32])
        data_chunk = data_chunk ^ iv
        ciphertext_chunk = get_ciphertext(data_chunk)
        ciphertext_hex += ciphertext_chunk.get_bitvector_in_hex()
        iv = ciphertext_chunk.deep_copy()
    
    return ciphertext_hex

def decrypt_data(ciphertext_hex, is_file=False):
    # Decrypt message
    iv = BitVector(hexstring=ciphertext_hex[:32])
    ciphertext_hex = ciphertext_hex[32:]
    deciphertext_hex = ""
    
    for i in range(0, len(ciphertext_hex), 32):
        ciphertext_chunk = BitVector(hexstring=ciphertext_hex[i:i+32])
        deciphertext_chunk = get_plaintext(ciphertext_chunk)
        deciphertext_chunk = deciphertext_chunk ^ iv
        deciphertext_hex += deciphertext_chunk.get_bitvector_in_hex()
        iv = ciphertext_chunk.deep_copy()
    
    if not is_file:
        print("Deciphered Text:")
        print("Before Unpadding:")
        print_string(deciphertext_hex, "hex", False)
        print_string(bytes.fromhex(deciphertext_hex).decode('utf-8', errors='ignore'), "ascii", False)
    
    # Remove padding
    padding = int(deciphertext_hex[-2:], 16)
    deciphertext_hex = deciphertext_hex[:-2*padding]
    
    return deciphertext_hex

def main():
    key = input("Key:\nIn ASCII: ")
    
    if(len(key) != 16):
        print("Key must be 16 characters long")
        exit(1)

    key_hex = key.encode('utf-8').hex()
    print_string(key_hex, "hex", False)
    print()

    before_key_expansion_time = time.perf_counter()
    round_keys.append(BitVector(hexstring=key_hex))
    key_expansion(key_hex, 1)
    time_taken_key_expansion = (time.perf_counter() - before_key_expansion_time) * 1000

    print("\nChoose operation:")
    print("1. Encrypt/Decrypt plaintext")
    print("2. Encrypt/Decrypt file")
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        plaintext = input("\nPlaintext:\nIn ASCII: ")
        plaintext_hex = plaintext.encode('utf-8').hex()
        print_string(plaintext_hex, "hex", False)
        
        # Encryption
        before_encryption_time = time.perf_counter()
        ciphertext_hex = encrypt_data(plaintext, False)
        time_taken_encryption = (time.perf_counter() - before_encryption_time) * 1000

        ciphertext = bytes.fromhex(ciphertext_hex).decode('utf-8', errors='ignore')
        print("\nCiphered Text:")
        print_string(ciphertext_hex, "hex", False)
        print_string(ciphertext, "ascii", False)
        
        # Decryption
        before_decryption_time = time.perf_counter()
        deciphertext_hex = decrypt_data(ciphertext_hex, False)
        time_taken_decryption = (time.perf_counter() - before_decryption_time) * 1000
        
        print("After Unpadding:")
        print_string(bytes.fromhex(deciphertext_hex).decode('utf-8', errors='ignore'), "ascii", False)
        print_string(deciphertext_hex, "hex", False)
        print()

    elif choice == "2":
    
        file_path = input("Enter file path to encrypt: ")
        if not os.path.exists(file_path):
            print("File does not exist!")
            exit(1)

        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        # Encryption
        before_encryption_time = time.perf_counter()
        ciphertext_hex = encrypt_data(file_content, True)
        time_taken_encryption = (time.perf_counter() - before_encryption_time) * 1000

        encrypted_file_path = "encrypted_" + file_path
        with open(encrypted_file_path, 'wb') as file:
            file.write(bytes.fromhex(ciphertext_hex))

        print(f"Encrypted file saved as: {encrypted_file_path}")
        
        # Decryption
        before_decryption_time = time.perf_counter()
        deciphertext_hex = decrypt_data(ciphertext_hex, True)
        time_taken_decryption = (time.perf_counter() - before_decryption_time) * 1000
        
        # Save decrypted file
        decrypted_file_path = "decrypted_" + file_path

        with open(decrypted_file_path, 'wb') as file:
            file.write(bytes.fromhex(deciphertext_hex))
        print(f"Decrypted file saved as: {decrypted_file_path}")

    else:
        print("Invalid choice!")
        exit(1)

    # Print time taken
    print("\nExecution Time Details:")
    print("Key Schedule Time: ", time_taken_key_expansion, "ms")
    print("Encryption Time: ", time_taken_encryption, "ms") 
    print("Decryption Time: ", time_taken_decryption, "ms")

if __name__ == "__main__":
    main()