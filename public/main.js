let correctN = undefined;
let nonce = undefined;
const resultPrompt = document.getElementById('result');

async function sha256(str) {
  const buffer = new TextEncoder('utf-8').encode(str);
  return crypto.subtle.digest('SHA-256', buffer).then((hash) => {
    return Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
  });
}

function verify(nonce, n) {
  sha256(nonce + n).then((hash) => {
    document.getElementById('verify-result').innerText = hash;
  });
}
function toggleSuccess() {
  resultPrompt.style.color = 'green';
  resultPrompt.innerText = 'Correct answer. n = ' + correctN + ', nonce = ' + nonce;
}
function toggleFailure(msg) {
  resultPrompt.style.color = 'red';
  resultPrompt.innerText = msg !== undefined ? msg : 'Incorrect answer. n = ' + correctN + ', nonce = ' + nonce;
}
function resetPrompt() {
  resultPrompt.style.color = 'black';
  resultPrompt.innerText = '';

}

document.getElementById('draw').addEventListener('click', () => {
  fetch('/api/hash/draw')
    .then((response) => response.json())
    .then((data) => {
      if(data.hash) {
        resetPrompt();
        document.getElementById('hash').value = data.hash;
      }
    })
});

document.getElementById('guess').addEventListener('click', () => {
  fetch('/api/hash/guess', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ hash: document.getElementById('hash').value, n: document.getElementById('n').value }),
  })
    .then((response) => response.json())
    .then((data) => {
      if(data.result === 'success') {
        correctN = data.n;
        nonce = data.nonce;
        toggleSuccess();
      } else {
        correctN = data.n;
        nonce = data.nonce;
        toggleFailure(data.message);
      }
    })
});

document.getElementById('verify').addEventListener('click', () => {
  verify(nonce, correctN);
});