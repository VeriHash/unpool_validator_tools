import argparse

from web3 import Web3


def broadcast(w3, signedTx):

    # Send the transaction to our web3 endpoint
    txHash = w3.eth.send_raw_transaction(signedTx)

    # Wait for the receipt
    return w3.eth.wait_for_transaction_receipt(txHash)


if __name__ == '__main__':

    # Parse some command line arguments
    parser = argparse.ArgumentParser(description='Broadcast a signed transaction')
    parser.add_argument('endpoint', help='The Execution Layer JSON RPC endpoint')
    parser.add_argument('signedTx', help='The raw signed transaction')
    args = parser.parse_args()

    # Create the web3 endpoint
    w3 = Web3(Web3.HTTPProvider(args.endpoint))

    # Send the transaction
    print()
    print('Sending validator registration transaction...')
    receipt = broadcast(w3, args.signedTx)
    print(f'Transaction Hash: {receipt.transactionHash.hex()}')
