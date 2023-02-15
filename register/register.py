# Example run:
# python sign.py ~/keys/keystore-m_12345_1234_0_0_0-1234567890.json --password "$(cat ~/keys/password.txt)"

import argparse
import getpass
import json

from web3 import Web3


def register(endpoint, proxyContractAddress, proxyContractABI, publicKey, message, signature,
             beneficiaryWalletAddress, beneficiaryWalletPrivateKey, ofacEnabled):

    # Make a connection to the JSON RPC endpoint so we can interact with the Ethereum chain
    w3 = Web3(Web3.HTTPProvider(endpoint))

    # We need to create a contract object so we can register the validator
    proxyContract = w3.eth.contract(address=w3.toChecksumAddress(proxyContractAddress),
                                    abi=proxyContractABI)

    # Create the function call
    fnCall = proxyContract.functions.add_validator(publicKey, message, signature, ofacEnabled)

    # Create the transaction using the public key with a new nonce for each one
    txArgs = {
        'from': beneficiaryWalletAddress,
        'nonce': w3.eth.get_transaction_count(beneficiaryWalletAddress),
    }
    txConstruct = fnCall.buildTransaction(txArgs)

    # Sign the transaction with the admin's private key
    txCreate = w3.eth.account.sign_transaction(txConstruct, beneficiaryWalletPrivateKey)

    # Send the transaction to our web3 endpoint
    txHash = w3.eth.send_raw_transaction(txCreate.rawTransaction)

    # Wait for the receipt
    return w3.eth.wait_for_transaction_receipt(txHash)


if __name__ == '__main__':

    # Parse some command line arguments
    parser = argparse.ArgumentParser(description="Queue a validator for registration with Unpool.fi's MEV smoothing contracts")
    parser.add_argument('endpoint', help='The Execution Layer JSON RPC endpoint')
    parser.add_argument('proxyContractAddress', help='The address of the proxy contract used for registration')
    parser.add_argument('proxyContractABIFilename', help='The filename of the JSON-formatted ABI of the proxy contract')
    parser.add_argument('publicKey', help="The validator's public key")
    parser.add_argument('message', help='The message signed by the validator, from `sign.py`')
    parser.add_argument('signature', help='The signature used to sign the message, from `sign.py`')
    parser.add_argument('beneficiaryWalletAddress', help='The wallet allowed to withdraw your balance')
    parser.add_argument('--beneficiaryWalletPrivateKey', default=None, help='The private key of the beneficiary wallet')
    parser.add_argument('--ofacEnabled', default=None, help='Set to true if you fall under OFAC jurisdiction. Otherwise set false')
    args = parser.parse_args()

    # Get the beneficiary wallet's private key if it wasn't given on the CLI (will be hidden)
    msg = ("Please enter the beneficary wallet's private key. (Caution, please understand the source "
           "code of this script and know what it is doing with your private key. It is used to sign "
           "the registration transaction, but you should verify that statement. Anyone with your "
           "private key can steal your crypto!): ")
    beneficiaryWalletPrivateKey = args.beneficiaryWalletPrivateKey or getpass.getpass(msg)

    # Get the OFAC jurisdiction status if it wasn't given on the CLI or a bad value was used
    if args.ofacEnabled is None or !bool(args.ofacEnabled):
      while True:
        try:
          msg = ("Do you fall under OFAC jurisdiction? (true or false): ")
          ofacEnaled = bool(input(msg))
        except ValueError:
          print("true or false not given")
          continue
        else:
          break

    # Load the proxy contract's JSON ABI
    proxyContractABI = json.load(open(args.proxyContractABIFilename))

    # Register!
    print()
    print('Sending transactions to register validator...')
    receipt = register(args.endpoint, args.proxyContractAddress, proxyContractABI,
                       args.publicKey, args.message, args.signature,
                       args.beneficiaryWalletAddress, beneficiaryWalletPrivateKey, ofacEnabled)
    print(f'Transaction Hash: {receipt.transactionHash.hex()}')
