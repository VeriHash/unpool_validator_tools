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

from verify import main as verify_main


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


def main(keystoreFilename, keystorePassword):

    # Get the password if it wasn't given on the CLI (will be hidden)
    ksPassword = keystorePassword or getpass.getpass('Please enter the keystore decryption password: ')

    # Let's sign!
    validatorPublicKey, message, signature = sign(keystoreFilename, ksPassword)

    # We need this information for the contract, and it needs to be hex encoded.
    print()
    print('Enter the following information into the mev smoothing contract:')
    print('Validator Public Key:', validatorPublicKey)
    print('Message:', message)
    print('Signature:', signature)

    return validatorPublicKey, message, signature


def add_sign_args(parser):
    parser.add_argument('keystoreFilename', help='The Geth keystore v4 file.')
    parser.add_argument('--keystorePassword', default=None, help='The password used for encrypting the private keys.')
    return parser


if __name__ == '__main__':

    # Parse some command line arguments
    d = 'Extract the public and private keys from a Geth keystore file in order to create a BLS signature.'
    parser = argparse.ArgumentParser(description=d)
    parser = add_sign_args(parser)
    args = parser.parse_args()

    validatorPublicKey, message, signature = main(args.keystoreFilename, args.keystorePassword)

    # Verify the signature. It can fail if libraries aren't the corect versions.
    verify_main(validatorPublicKey, message, signature)
