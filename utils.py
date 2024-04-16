
from hashlib import sha3_256


class ElipticPoint:
    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve
        self.check_if_on_curve()

    def check_if_on_curve(self):
        if (self.y*self.y) % self.curve.p != ( pow(self.x, 3, self.curve.p) + self.curve.a*self.x + self.curve.b ) % self.curve.p:
            raise Exception("Point not on curve")
        
    def add_point(self, Q):
        x1, y1 = self.x, self.y
        x2, y2 = Q.x, Q.y
        if x1 == x2 and y1 == y2:
            beta = (3*x1*x2 + self.curve.a) * pow(2*y1, -1, self.curve.p)
        else:
            beta = (y2 - y1) * pow(x2 - x1, -1, self.curve.p)
        x3 = (beta*beta - x1 - x2) % self.curve.p
        y3 = (beta * (x1 - x3) - y1) % self.curve.p
        return ElipticPoint(x3, y3, self.curve)
    
    def multiply_point(self, k):
        target_point = self
        k_binary = bin(k)[2:]
        for i in range(1, len(k_binary)):
            current_bit = k_binary[i: i+1]
            target_point = target_point.add_point(target_point)
            if current_bit == "1":
                target_point = target_point.add_point(self)
        return target_point
    
    def __str__(self):
        return f"{self.x} {self.y}"

class ElipticCurve:
    def __init__(self, a, b, p, order):
        self.a = a
        self.b = b
        self.p = p
        self.order = order
    def add_G_point(self, G):
        self.G = G

"""
The Prover Class is used to prove the knowledge of a number.

:param curve: the elliptic curve
:param secret: the secret key of the prover
"""
class Prover:
    def __init__(self, curve, secret):
        self.curve = curve
        self.secret = secret
        self.public_key = curve.G.multiply_point(secret)
    """
    The prove function is used to prove the knowledge of a number.
    
    :param number: the number to be proved

    :return: the point R and the integer e
    """
    def prove(self, number):
        R = self.curve.G.multiply_point(number)
        c = sha3_256((str(self.curve.G)+str(self.public_key)+str(R)).encode('utf-8')).hexdigest()
        c = int(c, 16)
        e = (number + self.secret*c) % self.curve.order
        return R, e, c


"""
The verifier Class is used to verify the proof of knowledge of the prover.

:param curve: the elliptic curve
"""
class Verifier:
    def __init__(self, curve):
        self.curve = curve

    """
    The verify function is used to verify the proof of knowledge of the prover.

    :param R: the point R
    :param e: the integer e
    :param public_key: the public key of the prover

    :return: True if the proof is correct, False otherwise
    """
    def verify(self, R, e, public_key):
        c = sha3_256((str(self.curve.G)+str(public_key)+str(R)).encode('utf-8')).hexdigest()
        c = int(c, 16)
        ##### Check if eG = R + cX #####
        lhs = self.curve.G.multiply_point(e)
        rhs = public_key.multiply_point(c)
        rhs = rhs.add_point(R)
        if lhs.x == rhs.x and lhs.y == rhs.y:
            return True
        return False
    """
    The check function is used to check after reveal if the proof of knowledge of the prover is correct.

    :param r: the integer r which were to be proved
    :param R_obtained: the point R obtained from prover

    :return: True if the proof is correct, False otherwise
    """
    def check(self, r, e, public_key, ):
        _R = self.curve.G.multiply_point(r)

        c = sha3_256((str(self.curve.G)+str(public_key)+str(_R)).encode('utf-8')).hexdigest()
        c = int(c, 16)
        ##### Check if eG = R + cX #####
        lhs = self.curve.G.multiply_point(e)
        rhs = public_key.multiply_point(c)
        rhs = rhs.add_point(_R)
        if lhs.x == rhs.x and lhs.y == rhs.y:
            return True
        return False

        


if __name__ == "__main__":
    secp256k1 = ElipticCurve(0, 7, pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - pow(2, 0), 115792089237316195423570985008687907852837564279074904382605163141518161494337)
    G = ElipticPoint(55066263022277343669578718895168534326250603453777594175500187360389116729240, 32670510020758816978083085130507043184471273380659243275938904335757337482424, secp256k1)
    secp256k1.add_G_point(G)
    r = 312
    Alice = Prover(secp256k1, r)
    Bob = Verifier(secp256k1)
    R, e, c = Alice.prove(12736871263781628)
    if Bob.verify(R, e, Alice.public_key):
        print("Success")
    else:
        print("Failure")
    if Bob.check(12736871263781628, e, Alice.public_key):
        print("Success")
    else:
        print("Failure")