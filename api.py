import flask
import random
import uuid
from hashlib import sha256
from utils import ElipticCurve, ElipticPoint, Prover, Verifier

app = flask.Flask(__name__, static_folder='public')

hashes = dict()

@app.route('/api/draw', methods=['POST'])
def draw():
    n = str(random.randint(1, 10))
    nonce = str(uuid.uuid4())
    hash = sha256((nonce+n).encode()).hexdigest()
    hashes[hash] = (nonce, n)

    return flask.jsonify({
        'hash': hash,
    })

@app.route('/api/guess', methods=['POST'])
def guess():
    data = flask.request.json
    hash = data['hash']
    nonce, n = hashes[hash]

    if sha256((nonce+data['n']).encode()).hexdigest() == hash:
        return flask.jsonify({
            'result': 'success',
            'nonce': nonce,
        })
    else:
        return flask.jsonify({
            'result': 'failure',
            'nonce': nonce,
        })

if __name__ == '__main__':
    secp256k1 = ElipticCurve(0, 7, pow(2, 256) - pow(2, 32) - pow(2, 9) - pow(2, 8) - pow(2, 7) - pow(2, 6) - pow(2, 4) - pow(2, 0), 115792089237316195423570985008687907852837564279074904382605163141518161494337)
    G = ElipticPoint(55066263022277343669578718895168534326250603453777594175500187360389116729240, 32670510020758816978083085130507043184471273380659243275938904335757337482424, secp256k1)
    secp256k1.add_G_point(G)
    #server private key
    r = 312

    server_prover = Prover(secp256k1, r)

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