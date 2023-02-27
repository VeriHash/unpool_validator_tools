# References:
# https://github.com/Chia-Network/bls-signatures/tree/main/python-bindings#creating-keys-and-signatures

import argparse
import binascii

from py_ecc.bls import G2ProofOfPossession


def verify(validatorPublicKey, message, signature):

    # Check if the message was signed by the same owner of the public key via the signature
    return G2ProofOfPossession.Verify(
        binascii.a2b_hex(validatorPublicKey),
        binascii.a2b_hex(message),
        binascii.a2b_hex(signature),
    )


def main(validatorPublicKey, message, signature):

    # Verify the signature. It can fail if libraries aren't the corect versions.
    isValid = verify(validatorPublicKey, message, signature)
    print()
    print(f'Is the signature valid? {isValid}')
    if not isValid:
        raise RuntimeError('Signature invalid!')


def add_verify_args(parser):
    parser.add_argument('validatorPublicKey', help='The public key of the signer.')
    parser.add_argument('message', help='The message which was signed.')
    parser.add_argument('signature', help='The signature for the message.')
    return parser


if __name__ == '__main__':

    # Parse some command line arguments
    parser = argparse.ArgumentParser(description='Verify a BLS12-381 signed message')
    parser = add_verify_args(parser)
    args = parser.parse_args()

    main(args.validatorPublicKey, args.message, args.signature)
