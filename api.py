import json
import flask
import random
import uuid
from hashlib import sha256
from utils import ElipticCurve, ElipticPoint, Prover, Verifier
from flask_cors import CORS, cross_origin


app = flask.Flask(__name__, static_folder='public')


hashes = dict()

secp256k1 = ElipticCurve(0, 7, pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - pow(2, 0), 115792089237316195423570985008687907852837564279074904382605163141518161494337)
G = ElipticPoint(55066263022277343669578718895168534326250603453777594175500187360389116729240, 32670510020758816978083085130507043184471273380659243275938904335757337482424, secp256k1)
secp256k1.add_G_point(G)
#server private key
r = 312
global drawn_number
drawn_number = None
server_prover = Prover(secp256k1, r)
client_verifier = Verifier(secp256k1)




@app.route('/shnorr')
def index():
    return flask.send_from_directory('public', 'shnorr.html')

'''
This route is used to draw a number n and prove the knowledge of the number n

Output:
{
    "R": "Point on ElipticCurve",
    "e": "Signature",
    "public_key": "Public key of the prover"
}
'''
@app.route('/api/draw')
def draw():
    n = random.randint(1, 100)
    R, e = server_prover.prove(n)
    global drawn_number
    drawn_number = n
    x = str(R.x)
    y = str(R.y)
    return flask.jsonify({
        'R.x - x coordinate of Point on ElipticCurve': str(R.x),
        'R.y - y coordinate of Point on ElipticCurve': str(R.y),
        'e - Signature': str(e),
        'public_key x coordinate': str(server_prover.public_key.x),
        'public_key y coordinate': str(server_prover.public_key.y),
    })


'''
This route is used to verify the proof of knowledge of some number n

Input:
{
    "R": "Point on ElipticCurve given by the prover",
    "e": "Signature given by the prover",
    "public_key": "Public key of the prover"
}
'''
@app.route('/api/verify', methods=['POST'])
def verify():
    
    data = flask.request.json
    Rx = int(data['Rx'])
    Ry = int(data['Ry'])
    try:
        R = ElipticPoint(int(Rx), int(Ry), secp256k1)
    except Exception as e:
        return flask.jsonify({
            'result': 'failure',
            'message': 'Invalid point',
        })
    e = int(data['e'])
    public_keyx = int(data['public_keyx'])
    public_keyy = int(data['public_keyy'])
    print(e)
    public_key = ElipticPoint(int(public_keyx), int(public_keyy), secp256k1)

    if client_verifier.verify(R, e, public_key):
        return flask.jsonify({
            'result': 'success',
            'message': 'The proof is correct',
        })
    else:
        return flask.jsonify({
            'result': 'failure',
            'message': 'The proof is incorrect',
        })
    

'''
This route is used to check if the proof is of some number n

Input:
{
    "r": "The number to be checked",
    "e" : "The signature",
    "public_keyx": "x cordinate of Public key of the prover",
    "public_keyy": "y cordinate of Public key of the prover"
}
'''    
@app.route('/api/checkifhonest', methods=['POST'])
def checkifhonest():
    data = flask.request.json
    r = int(data['r'])
    e = int(data['e'])
    public_keyx = data['public_keyx']
    public_keyy = data['public_keyy']
    try:
        public_key = ElipticPoint(int(public_keyx), int(public_keyy), secp256k1)
    except Exception as e:
        return flask.jsonify({
            'result': 'failure',
            'message': 'Invalid point (not on eliptic curve)',
        })
    if client_verifier.check(r, e, public_key):
        return flask.jsonify({
            'result': 'success',
            'message': 'The proof is correct',
        })
    else:
        return flask.jsonify({
            'result': 'failure',
            'message': 'The proof is incorrect',
        })


'''
This route is used to guess the number drawn by the server

Input:
{
    "guess": "The number guessed by the client"
}
Output:
{
    "result": "success/failure",
    "message": "You guessed the right/wrong number/no number was drawn"
}
'''
@app.route('/api/guess', methods=['POST'])
def guess():
    data = flask.request.json
    guess = data['guess']
    global drawn_number
    if drawn_number == None:
        return flask.jsonify({
            'result': 'failure',
            'message': 'No number was drawn',
        })
    if guess == drawn_number:
        return flask.jsonify({
            'result': 'success',
            'message': 'You guessed the right number',
        })
    else:
        return flask.jsonify({
            'result': 'failure',
            'message': f'You guessed the wrong number the correct number was {drawn_number}',
        }) 

# @app.route('/api/guess', methods=['POST'])
# def guess():
#     data = flask.request.json
#     hash = data['hash']
#     nonce, n = hashes[hash]

#     if sha256((nonce+data['n']).encode()).hexdigest() == hash:
#         return flask.jsonify({
#             'result': 'success',
#             'nonce': nonce,
#         })
#     else:
#         return flask.jsonify({
#             'result': 'failure',
#             'nonce': nonce,
#         })

if __name__ == '__main__':
    

    # clien_verifier = Verifier(secp256k1)
    
    # #### To prove the knowledge of some number x ####
    # x = 123456
    # #### Generate R and e ####
    # R, e = server_prover.prove(x)
    # #### To verify the proof ####
    # print(clien_verifier.verify(R, e, server_prover.public_key))
    # #### To check after reveal if the proof was of x ####
    # print(clien_verifier.check(x, R))

    app.run(debug=True)