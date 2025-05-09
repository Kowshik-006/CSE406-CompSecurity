import random
import math
import time
from sympy import randprime

P = 0
a = 0
b = 0
G = (0,0)


def generate_random_prime(bitsize):
    lower_bound = 1 << (bitsize - 1)
    upper_bound = (1 << bitsize) - 1
    return randprime(lower_bound, upper_bound)

def generate_curve():
    while True:
        a = random.randrange(0, P)
        b = random.randrange(0, P)
        if (4 * a**3 + 27 * b**2) % P != 0:
            return a, b        

def legendre_symbol(a, p):
    return pow(a, (p - 1) // 2, p)

def tonelli_shanks(n, p):
    # r^2 = n mod p
    # We need to find r

    # Step 1: p - 1 = q * 2^s, where q is odd. Find q and s
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    
    # Step 2: Find z which is a quadratic non-residue mod p
    z = 2
    # -1 mod p = p - 1
    # We need to find z such that legendre_symbol(z, p) == p - 1
    while legendre_symbol(z, p) != p-1:
        z += 1
    
    # Step 3: Initialize variables
    M = s
    c = pow(z, q, p) # c = z^q mod p
    t = pow(n, q, p) # t = n^q mod p
    R = pow(n, (q + 1) // 2, p) # R = n^((q + 1)/2) mod p

    while True:
        if t == 0:
            return 0
        if t == 1:
            return R
        # Find the least i such that 0 < i < M and t^(2^i) = 1 mod p
        i = 1
        temp = pow(t, 2, p)
        while temp != 1:
            i += 1
            if i == M:
                raise Exception("Tonelli-Shanks failed")
            temp = pow(temp, 2, p)
        
        # Step 4: Update variables
        b = pow(c, 2**(M - i - 1), p) # b = c^(2^(M - i - 1)) mod p
        M = i
        c = pow(b, 2, p) # c = b^2 mod p
        t = (t * c) % p  # t = t*b^2 mod p
        R = (R * b) % p  # R = R*b mod p

def get_generator_point():
    while True:
        x = random.randrange(0, P)
        y_squared = (x**3 + a * x + b) % P
        # When legendre_symbol(y_squared, P) == 1, y_squared is a quadratic residue mod P
        # Then there exists a y such that y^2 = y_squared mod P
        if legendre_symbol(y_squared, P) == 1:
            y = tonelli_shanks(y_squared, P)
            return (x, y)


def point_add(point1, point2):
    if point1 == None:
        return point2
    if point2 == None: 
        return point1
    
    x1, y1 = point1
    x2, y2 = point2
    
    if x1 == x2 and y1 == y2:
        # Point Double
        s = ((3 * x1**2 + a) * pow(2 * y1, -1, P)) % P
    else:
        if x1 == x2:
            return None
        # Point Add
        s = ((y2 - y1) * pow(x2 - x1, -1, P)) % P
    
    x3 = (s**2 - x1 - x2) % P
    y3 = (s * (x1 - x3) - y1) % P

    return (x3, y3)



def scalar_mult(scalar, point):
    if scalar == 0 or point == None:
        return None
    if scalar == 1:
        return point
    
    shift = int(math.log2(scalar))
    mask = 1 << shift
    # Ignoring the MSB
    mask >>= 1
    result = point
    while mask:
        # Double
        result = point_add(result, result) 
        if scalar & mask:
            # Add
            result = point_add(result, point)
        mask >>= 1

    return result
    

def init(bitlength=128):
    global P, a, b, G
    P = generate_random_prime(128)
    a, b = generate_curve()
    G = get_generator_point()

def main():
    bitlengths = [128, 192, 256]
    print(f"{'K':^8}{'A(ms)':^20}{'B(ms)':^20}{'Shared Key R(ms)':^20}")
    print("-"*70)
    for bitlength in bitlengths:
        init(bitlength)
        a_time = 0
        b_time = 0
        shared_key_time = 0
        iterations = 5
        for _ in range(iterations):
            # Alice
            a_private = random.randrange(1, P)
            before_a_public_time = time.perf_counter()
            a_public = scalar_mult(a_private, G)
            time_taken_a_public = (time.perf_counter() - before_a_public_time)*1000
            # Bob
            b_private = random.randrange(1, P)
            before_b_public_time = time.perf_counter()
            b_public = scalar_mult(b_private, G)
            time_taken_b_public = (time.perf_counter() - before_b_public_time)*1000

            before_shared_key_time = time.perf_counter()
            alice_shared_secret = scalar_mult(a_private, b_public)
            bob_shared_secret = scalar_mult(b_private, a_public)
            time_taken_shared_key = (time.perf_counter() - before_shared_key_time)*1000

            if alice_shared_secret == bob_shared_secret:
                a_time += time_taken_a_public
                b_time += time_taken_b_public
                shared_key_time += time_taken_shared_key
            else:
                raise Exception("Shared secrets do not match!")
        print(f"{bitlength:^8}{a_time/iterations:^20.2f}{b_time/iterations:^20.2f}{shared_key_time/iterations:^20.2f}")
        

if __name__ == "__main__":
    main()


