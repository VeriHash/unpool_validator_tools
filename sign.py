# References:
# https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/key_handling/keystore.py
# https://github.com/ethereum/py_ecc
# https://github.com/Chia-Network/bls-signatures/tree/main/python-bindings#creating-keys-and-signatures

# Example run:
# python sign.py ~/keys/keystore-m_12345_1234_0_0_0-1234567890.json --password "$(cat ~/keys/password.txt)"

import argparse
import getpass
import uuid

from py_ecc.bls import G2ProofOfPossession
from staking_deposit.key_handling.keystore import Keystore

from verify import verify


def sign(filename, password):

    # Load the keystore JSON, which contains the validator information.
    keystore = Keystore.from_file(filename)

    # Decrypt the keystore with the password to get the private key, used to sign a message.
    privateKey = keystore.decrypt(password)

    # Create a random message to sign. It doesn't matter what the content is, but we store
    # signatures so they need to be unique. A UUID is extremely unique.
    message = uuid.uuid4().bytes

    # Sign using BLS12-381 curve
    signature = G2ProofOfPossession.Sign(int.from_bytes(privateKey, 'big'), message)

    # Return the public key, the message, and the signature
    return keystore.pubkey, message.hex(), bytes(signature).hex()


if __name__ == '__main__':

    # Parse some command line arguments
    d = 'Extract the public and private keys from a Geth keystore file in order to create a BLS signature.'
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument('filename', help='The Geth keystore v4 file.')
    parser.add_argument('--password', default=None, help='The password used for encrypting the private keys.')
    args = parser.parse_args()

    # Get the password if it wasn't given on the CLI (will be hidden)
    password = args.password or getpass.getpass('Please enter the keystore decryption password: ')

    # Let's sign!
    publicKey, message, signature = sign(args.filename, password)

    # We need this information for the contract, and it needs to be hex encoded.
    print()
    print('Enter the following information into the mev smoothing contract:')
    print('Public Key:', publicKey)
    print('Message:', message)
    print('Signature:', signature)

    # Verify the signature. It can fail if libraries aren't the corect versions.
    isValid = verify(publicKey, message, signature)
    print()
    print(f'Is the signature valid? {isValid}')
    if not isValid:
        raise RuntimeError('Signature invalid!')
