import argparse
import getpass
import json

from staking_deposit.key_handling.keystore import Keystore


def extract_private_key_from_keystore(content, password):
    keystore = Keystore.from_json(json.loads(content))
    privateKey = keystore.decrypt(password).hex()
    publicKey = keystore.pubkey
    return privateKey, publicKey


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract a private key from a EIP-2335 Keystore file')
    parser.add_argument('keystoreContent', help='The Geth keystore v4 file.')
    parser.add_argument('--keystorePassword', default=None, help='The password used for encrypting the private keys.')
    args = parser.parse_args()

    # Get the password if it wasn't given on the CLI (will be hidden)
    ksPassword = args.keystorePassword or getpass.getpass('Please enter the keystore decryption password: ')
    privateKey, publicKey = extract_private_key_from_keystore(args.keystoreContent, ksPassword)

    print()
    print('DANGER!!! NEVER GIVE OUT YOUR PRIVATE KEY!')
    print(f'Private Key: {privateKey}')
    print(f'Public Key: {publicKey}')
