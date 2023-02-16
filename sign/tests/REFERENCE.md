These test examples use the keystore examples from:
https://eips.ethereum.org/EIPS/eip-2335

Here is the Python code I used for signing and verification:

```bash
ipython -i sign.py
```

```python
import binascii

v4_password = open('tests/v4_password.txt').read()

pk, _, msg, sig = sign('v4_scrypt.json', v4_password)

publicKey: bytes = binascii.a2b_hex(pk)
message: bytes = binascii.a2b_hex(msg)
signature: bytes = binascii.a2b_hex(sig)

G2ProofOfPossession.Verify(publicKey, message, signature)
> True

pk, _, msg, sig = sign('tests/v4_pbkdf2.json', v4_password)

publicKey: bytes = binascii.a2b_hex(pk)
message: bytes = binascii.a2b_hex(msg)
signature: bytes = binascii.a2b_hex(sig)

G2ProofOfPossession.Verify(publicKey, message, signature)
> True
```
