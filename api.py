import flask
import random
import uuid
from hashlib import sha256
from utils import ElipticCurve, ElipticPoint, Prover, Verifier

app = flask.Flask(__name__, static_folder='public')

hashes = dict()

secp256k1 = ElipticCurve(0, 7, pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - pow(2, 0), 115792089237316195423570985008687907852837564279074904382605163141518161494337)
G = ElipticPoint(55066263022277343669578718895168534326250603453777594175500187360389116729240, 32670510020758816978083085130507043184471273380659243275938904335757337482424, secp256k1)
secp256k1.add_G_point(G)
#server private key
r = 312
drawn_number = None
server_prover = Prover(secp256k1, r)


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
    n = str(random.randint(1, 100))
    R, e = server_prover.prove(n)
    drawn_number = n

    return flask.jsonify({
        'R - Point on ElipticCurve': R,
        'e - Signature': e,
        'public_key': server_prover.public_key,
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
    R = data['R']
    e = data['e']
    public_key = data['public_key']

    if clien_verifier.verify(R, e, public_key):
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
    "R": "Point on ElipticCurve given by the prover",
    "n": "Number which was to be proved"
}
'''    
@app.route('/api/checkifhonest', methods=['POST'])
def checkifhonest():
    data = flask.request.json
    R = data['R']
    n = data['n']
    

    if clien_verifier.check(n, R):
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
    

    clien_verifier = Verifier(secp256k1)
    
    #### To prove the knowledge of some number x ####
    x = 123456
    #### Generate R and e ####
    R, e = server_prover.prove(x)
    #### To verify the proof ####
    print(clien_verifier.verify(R, e, server_prover.public_key))
    #### To check after reveal if the proof was of x ####
    print(clien_verifier.check(x, R))

    app.run(debug=True)