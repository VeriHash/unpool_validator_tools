# References:
# https://github.com/Chia-Network/bls-signatures/tree/main/python-bindings#creating-keys-and-signatures

import argparse
import binascii

from py_ecc.bls import G2ProofOfPossession


if __name__ == '__main__':

    # Parse some command line arguments
    parser = argparse.ArgumentParser(description='Extract the public and private keys from a Geth '
                                                 'keystore file in order to create a BLS sigature.')
    parser.add_argument('publicKey', help='The public key of the signer.')
    parser.add_argument('message', help='The message which was signed.')
    parser.add_argument('signature', help='The signature for the message.')
    args = parser.parse_args()

    # Convert the incoming hex strings into bytes
    publicKey: bytes = binascii.a2b_hex(args.publicKey)
    message: bytes = binascii.a2b_hex(args.message)
    signature: bytes = binascii.a2b_hex(args.signature)

    print('publicKey: %s' % publicKey)
    print('message: %s' % message)
    print('signature: %s' % signature)

    # Check if the message was signed by the same owner of the public key via the signature
    isValid: bool = G2ProofOfPossession.Verify(publicKey, message, signature)

    print()
    print('Is the signature valid?', isValid)
