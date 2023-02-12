import json

from web3 import Web3

BENEFICIARY_WALLET = '0x5b0DF4Ab7905F7e5098865900819188fA153dD0D'
privateKey = ''

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545/'))
proxyContractAddress = '0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231'
proxyContractABI = json.load(open('/home/dgleason/git/mev_sharing/oracle/ganache/abis/proxy.json'))
proxyContract = w3.eth.contract(address=w3.toChecksumAddress(proxyContractAddress),
                                abi=proxyContractABI)

# Generate a bunch of signature transactions
transactions = []
validators = json.load(open('validators.json'))
for i, (filename, data) in enumerate(validators.items()):
    print('generating transaction', i, filename)
    publicKey, _, message, signature = data

    transaction = proxyContract.functions.add_validator(publicKey, message, signature, True)

    # Create the transaction using the public key with a new nonce for each one
    txArgs = {
        'from': BENEFICIARY_WALLET,
        'nonce': w3.eth.get_transaction_count(BENEFICIARY_WALLET),
    }
    txConstruct = transaction.buildTransaction(txArgs)

    # Sign the transaction with the admin's private key
    txCreate = w3.eth.account.sign_transaction(txConstruct, privateKey)

    # Send the transaction to our web3 endpoint
    print(i, 'sending tx')
    txHash = w3.eth.send_raw_transaction(txCreate.rawTransaction)

    # Wait for the receipt
    print(i, 'waiting on tx receipt for:', transaction)
    txReceipt = w3.eth.wait_for_transaction_receipt(txHash)
