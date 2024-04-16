let rndn = undefined;
let servern = undefined;
const result = document.getElementById('result');

async function sha256(str) {
  const buffer = new TextEncoder('utf-8').encode(str);
  return crypto.subtle.digest('SHA-256', buffer).then((hash) => {
    return Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
  });
}

function lcg(seed) {
  res = (seed * 1103515245 + 12345) & 0x7fffffff;
  return res % 2;
}


document.getElementById('generate').addEventListener('click', async () => {
  const n = parseInt(Math.random() * 1000000, 10);
  document.getElementById('n').value = n;
  document.getElementById('nhashed').value = await sha256(n.toString());
});

document.getElementById('send').addEventListener('click', () => {
  fetch('/api/coinflip/commit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ hash: document.getElementById('nhashed').value }),
  })
    .then((response) => response.json())
    .then((data) => {
      if(data) {
        document.getElementById('servernhashed').value = data.hash;
      }
    });
});

document.getElementById('reveal').addEventListener('click', () => {
  const n = parseInt(document.getElementById('n').value, 10);
  fetch('/api/coinflip/reveal', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ n: n, hash: document.getElementById('servernhashed').value }),
  })
    .then((response) => response.json())
    .then((data) => {
      if(data) {
        servern = data.n;
        document.getElementById('servern').value = data.servern;
        document.getElementById('server-result').value = data.rnd;
      }
    });
});

document.getElementById('verify').addEventListener('click', () => {
  const n = parseInt(document.getElementById('n').value, 10);
  const servern = parseInt(document.getElementById('servern').value, 10);
  const seed = n ^ servern;

  document.getElementById('client-result').value = lcg(seed);
});