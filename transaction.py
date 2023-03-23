import argparse
import getpass
import json
import warnings
import requests

from distutils.util import strtobool

from web3 import Web3

from verify import main as verify_main, add_verify_args

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
    fnCall = contract.functions.add_validator(bytes.fromhex(validatorPublicKey),
                                              bytes.fromhex(message),
                                              bytes.fromhex(signature),
                                              isOfac)

    # Since we are online we can build the transaction which will estimate gas.
    txArgs = {
        'from': beneficiaryWalletAddress,
        'nonce': w3.eth.get_transaction_count(beneficiaryWalletAddress),
    }
    return fnCall.build_transaction(txArgs)


def create_tx_offline(w3, contract, validatorPublicKey, message, signature, isOfac, chain, nonce,
                      gas=DEFAULT_GAS, maxFeePerGas=DEFAULT_MAX_FEE_PER_GAS,
                      maxPriorityFeePerGas=DEFAULT_MAX_PRIORITY_FEE_PER_GAS):

    # Since we are offline we need to manually generate the txConstruct. We need data.
    data = contract.encodeABI(fn_name='add_validator',
                              args=[bytes.fromhex(validatorPublicKey),
                                    bytes.fromhex(message),
                                    bytes.fromhex(signature),
                                    isOfac])

    # We manually create the transaction args, usually produced by fnCall.build_transaction
    return {
        'value': 0,
        'gas': gas,
        'maxPriorityFeePerGas': w3.to_wei(maxPriorityFeePerGas, 'gwei'),
        'maxFeePerGas': w3.to_wei(maxFeePerGas, 'gwei'),
        'to': contract.address,
        'data': data,
        'nonce': nonce,
        'chainId': CHAIN_IDS[chain.lower()],
    }


def load_contract(w3, abi, address=CONTRACT_ADDRESS):

    return w3.eth.contract(address=w3.to_checksum_address(address), abi=abi)


def create_signed_transaction(w3, tx, beneficiaryWalletPrivateKey):

    signed = w3.eth.account.sign_transaction(tx, beneficiaryWalletPrivateKey)
    return signed.rawTransaction.hex()


def main(validatorPublicKey, message, signature, ofacEnabled, beneficiaryWalletAddress,
         beneficiaryWalletPrivateKey, endpoint, chain, nonce, proxyContractAbiFilename,
         gas=DEFAULT_GAS, maxFeePerGas=DEFAULT_MAX_FEE_PER_GAS,
         maxPriorityFeePerGas=DEFAULT_MAX_PRIORITY_FEE_PER_GAS):

    # We require the nonce when in offline mode. The other arguments have defaults.
    if endpoint is None and nonce is None:
        raise RuntimeError(('You are in offline mode. You need to specify the Nonce '
                            'of the beneficiary wallet address via `--nonce <nonce>`'))

    # Load the contract ABI from disk or download it from unpool.fi
    if proxyContractAbiFilename is None:
        proxyContractAbi = requests.get(CONTRACT_ABI_URL).json()
    else:
        proxyContractAbi = json.load(open(proxyContractAbiFilename))

    # Parse the endpoint to see if we work in offline mode or online mode
    if endpoint is None:

        # OFFLINE MODE
        print()
        print('You have not specified an execution layer JSON RPC endpoint. Setting offline mode.')

        # Use a local testing EVM in order to interact with the contract
        w3 = Web3(Web3.EthereumTesterProvider())

        # We need the contract either in offline or online mode
        contract = load_contract(w3, proxyContractAbi, CONTRACT_ADDRESS)

        # Create the transaction to sign
        tx = create_tx_offline(w3, contract, validatorPublicKey, message, signature, ofacEnabled,
                               chain, nonce, gas, maxFeePerGas, maxPriorityFeePerGas)

    else:

        # ONLINE MODE
        print()
        print('Using execution layer JSON RPC endpoint. Setting online mode.')

        # Use the specified endpoint to interact with the contract and chain
        w3 = Web3(Web3.HTTPProvider(endpoint))

        # We need the contract either in offline or online mode
        contract = load_contract(w3, proxyContractAbi, CONTRACT_ADDRESS)

        # Create the transaction to sign
        tx = create_tx_online(w3, contract, validatorPublicKey, message, signature, ofacEnabled,
                              beneficiaryWalletAddress)

    # Get the beneficiary wallet's private key if it wasn't given on the CLI (will be hidden)
    if not beneficiaryWalletPrivateKey:
        print()
    msg = ("Please enter the beneficary wallet's private key. (Caution, please understand the source "
           "code of this script and know what it is doing with your private key. It is used to sign "
           "the registration transaction, but you should verify that statement. Anyone with your "
           "private key can steal your crypto!): ")
    bwpk = beneficiaryWalletPrivateKey or getpass.getpass(msg)

    print()
    print('Raw signed transaction:')
    signedTx = create_signed_transaction(w3, tx, bwpk)
    print(signedTx)

    return w3, signedTx


def add_create_tx_args(parser):
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

    return parser


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
    parser = add_verify_args(parser)
    parser = add_create_tx_args(parser)
    # Add this here because it originally lives in sign_args.
    parser.add_argument('--noVerify', action='store_true', help='Set flag to disable signature verification. You might waste gas.')
    args = parser.parse_args()

    # Verify the signature. It can fail if libraries aren't the corect versions.
    if not args.noVerify:
        verify_main(args.validatorPublicKey, args.message, args.signature)

    # Create the transaction
    main(args.validatorPublicKey, args.message, args.signature, args.ofacEnabled,
         args.beneficiaryWalletAddress, args.beneficiaryWalletPrivateKey, args.endpoint,
         args.chain, args.nonce, args.proxyContractAbiFilename, args.gas, args.maxFeePerGas,
         args.maxPriorityFeePerGas)
