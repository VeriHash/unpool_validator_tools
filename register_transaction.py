import argparse
import getpass
import json
import warnings
import requests

from distutils.util import strtobool

from web3 import Web3

from verify import verify

# CONSTANTS
DEFAULT_GAS = 150000  # What I've seen for this transaction on Goerli
DEFAULT_MAX_FEE_PER_GAS = 10
DEFAULT_MAX_PRIORITY_FEE_PER_GAS = 0.1
CONTRACT_ADDRESS = '0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231'
CONTRACT_ABI_URL = 'https://unpool.fi/contracts/proxy_abi.json'
CHAIN_IDS = {
    'mainnet': 1,
    'goerli': 5,
}


# Turn off the deprecation warnings that I have no control over anyway - part 1
def warn(*args, **kwargs):
    pass


# Turn off the deprecation warnings that I have no control over anyway - part 2
warnings.warn = warn


def create_tx_online(w3, contract, validatorPublicKey, message, signature, isOfac,
                     beneficiaryWalletAddress):

    # Create a regular function call
    fnCall = contract.functions.add_validator(validatorPublicKey, message, signature, isOfac)

    # Since we are online we can build the transaction which will estimate gas.
    txArgs = {
        'from': beneficiaryWalletAddress,
        'nonce': w3.eth.get_transaction_count(beneficiaryWalletAddress),
    }
    return fnCall.buildTransaction(txArgs)


def create_tx_offline(w3, contract, validatorPublicKey, message, signature, isOfac, chain, nonce,
                      gas=DEFAULT_GAS, maxFeePerGas=DEFAULT_MAX_FEE_PER_GAS,
                      maxPriorityFeePerGas=DEFAULT_MAX_PRIORITY_FEE_PER_GAS):

    # Since we are offline we need to manually generate the txConstruct. We need data.
    data = contract.encodeABI(fn_name='add_validator',
                              args=[validatorPublicKey, message, signature, isOfac])

    # We manually create the transaction args, usually produced by fnCall.buildTransaction
    return {
        'value': 0,
        'gas': gas,
        'maxPriorityFeePerGas': w3.toWei(maxPriorityFeePerGas, 'gwei'),
        'maxFeePerGas': w3.toWei(maxFeePerGas, 'gwei'),
        'to': contract.address,
        'data': data,
        'nonce': nonce,
        'chainId': CHAIN_IDS[chain.lower()],
    }


def load_contract(w3, abi, address=CONTRACT_ADDRESS):
    return w3.eth.contract(address=w3.toChecksumAddress(address), abi=abi)


def create_signed_transaction(w3, tx, beneficiaryWalletPrivateKey):

    signed = w3.eth.account.sign_transaction(tx, beneficiaryWalletPrivateKey)
    return signed.rawTransaction.hex()


if __name__ == '__main__':

    # Parse some command line arguments
    d = """
    Create a signed transaction for registering a validator with Unpool.fi's MEV smoothing contracts.
    There are two modes of operation: online and offline.
    
    Some users choose to generate transactions offline and broadcast them with an external service
    such as Etherscan.
    
    When running offline, there are more required command line arguments. We calculate many arguments
    for you, such as gas fees and the signing wallet's nonce, when running online.
    """

    parser = argparse.ArgumentParser(description=d)
    parser.add_argument('validatorPublicKey', help="The validator's public key.")
    parser.add_argument('message', help='The message signed by the validator, from `sign.py`.')
    parser.add_argument('signature', help='The signature used to sign the message, from `sign.py`.')
    parser.add_argument('ofacEnabled', default='f', type=lambda x: bool(strtobool(x)),
                        choices=[True, False, 'y', 'yes', 't', 'true', 'on', '1', 'n', 'no', 'f', 'false', 'off', '0'],
                        help='Specify if you fall under OFAC jurisdiction.')
    parser.add_argument('beneficiaryWalletAddress', help='The wallet allowed to withdraw your balance')
    # Required for both, but we can enter it as part of script interaction if we want
    parser.add_argument('--beneficiaryWalletPrivateKey', default=None, help='The private key of the beneficiary wallet')
    # If the endpoint is not specified, the script will go into offline mode and more parameters are required
    parser.add_argument('--endpoint', help='The Execution Layer JSON RPC endpoint. If not specified, will use offline mode.')
    # The following are required for offline execution
    parser.add_argument('--chain', default='goerli', choices=CHAIN_IDS.keys(), help='The Ethereum chain to use.')

    h = 'In offline mode, specify the current "nonce" of the `beneficiaryWalletAddress`.'
    parser.add_argument('--nonce', type=int, help=h)

    h = 'The filename of the JSON-formatted ABI for the Proxy contract. If not specified, this script will download the ABI from unpool.fi.'
    parser.add_argument('--proxyContractAbiFilename', help=h)
    # If the Proxy Contract ABI JSON filename is specified, we read from disk. Otherwise, download it.

    h = 'When offline, specify the amount of gas to spend on the transaction (in Gwei).'
    parser.add_argument('--gas', type=float, default=DEFAULT_GAS, help=h)

    h = 'When offline, specify the maximum fee per gas to spend on the transaction (in Gwei).'
    parser.add_argument('--maxFeePerGas', type=float, default=DEFAULT_MAX_FEE_PER_GAS, help=h)

    h = 'When offline, specify the priority fee per gas to spend on the transaction (in Gwei).'
    parser.add_argument('--maxPriorityFeePerGas', type=float, default=DEFAULT_MAX_PRIORITY_FEE_PER_GAS, help=h)

    # Parse the arguments
    args = parser.parse_args()

    # We require the nonce when in offline mode. The other arguments have defaults.
    if args.endpoint is None and args.nonce is None:
        raise RuntimeError(('You are in offline mode. You need to specify the Nonce '
                            'of the beneficiary wallet address via `--nonce <nonce>`'))

    # Verify the signature. It can fail if libraries aren't the corect versions.
    isValid = verify(args.validatorPublicKey, args.message, args.signature)
    print()
    print(f'Is the signature valid? {isValid}')
    if not isValid:
        raise RuntimeError('Signature invalid!')

    # Load the contract ABI from disk or download it from unpool.fi
    if args.proxyContractAbiFilename is None:
        proxyContractAbi = requests.get(CONTRACT_ABI_URL).json()
    else:
        proxyContractAbi = json.load(open(args.proxyContractAbiFilename))

    # Parse the endpoint - we require different things here
    if args.endpoint is None:

        # OFFLINE MODE
        print()
        print('You have not specified an execution layer JSON RPC endpoint. Setting offline mode.')

        # Use a local testing EVM in order to interact with the contract
        w3 = Web3(Web3.EthereumTesterProvider())

        # We need the contract either in offline or online mode
        contract = load_contract(w3, proxyContractAbi, CONTRACT_ADDRESS)

        # Create the transaction to sign
        tx = create_tx_offline(w3, contract, args.validatorPublicKey, args.message, args.signature,
                               args.ofacEnabled, args.chain, args.nonce, args.gas, args.maxFeePerGas,
                               args.maxPriorityFeePerGas)

    else:

        # ONLINE MODE
        print()
        print('Using execution layer JSON RPC endpoint. Setting online mode.')

        # Use the specified endpoint to interact with the contract and chain
        w3 = Web3(Web3.HTTPProvider(args.endpoint))

        # We need the contract either in offline or online mode
        contract = load_contract(w3, proxyContractAbi, CONTRACT_ADDRESS)

        # Create the transaction to sign
        tx = create_tx_online(w3, contract, args.validatorPublicKey, args.message, args.signature,
                              args.ofacEnabled, args.beneficiaryWalletAddress)

    # Get the beneficiary wallet's private key if it wasn't given on the CLI (will be hidden)
    print()
    msg = ("Please enter the beneficary wallet's private key. (Caution, please understand the source "
           "code of this script and know what it is doing with your private key. It is used to sign "
           "the registration transaction, but you should verify that statement. Anyone with your "
           "private key can steal your crypto!): ")
    beneficiaryWalletPrivateKey = args.beneficiaryWalletPrivateKey or getpass.getpass(msg)

    print()
    print('Raw signed transaction:')
    print(create_signed_transaction(w3, tx, beneficiaryWalletPrivateKey))
