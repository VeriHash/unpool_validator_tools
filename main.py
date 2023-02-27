import argparse
import warnings

from sign import main as sign_main, add_sign_args
from verify import main as verify_main, add_verify_args
from transaction import main as create_tx_main, add_create_tx_args
from broadcast import main as broadcast_main


# Turn off the deprecation warnings that I have no control over anyway - part 1
def warn(*args, **kwargs):
    pass


# Turn off the deprecation warnings that I have no control over anyway - part 2
warnings.warn = warn


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
    parser = add_sign_args(parser)
    parser = add_verify_args(parser)
    parser = add_create_tx_args(parser)
    args = parser.parse_args()

    # Verify the signature. It can fail if libraries aren't the corect versions.
    validatorPublicKey, message, signature = sign_main(args.keystoreFilename, args.keystorePassword)
    verify_main(validatorPublicKey, message, signature)
    w3, signedTx = create_tx_main(validatorPublicKey, message, signature, args.ofacEnabled,
                                  args.beneficiaryWalletAddress, args.beneficiaryWalletPrivateKey,
                                  args.endpoint, args.chain, args.nonce, args.proxyContractAbiFilename,
                                  args.gas, args.maxFeePerGas, args.maxPriorityFeePerGas)
    broadcast_main(w3, signedTx)
