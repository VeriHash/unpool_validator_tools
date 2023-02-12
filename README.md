# Unpool.fi Validator Tools

A repository of tools for administration of validators on Unpool.fi

## Registering a Validator

There are two steps to registering a validator with Unpool.fi:

1. The first step is generating a signed message using the validator's private key, which proves ownership of the validator itself.

2. The second step is requesting validator registration with Unpool.fi's MEV sharing contracts. The signed message generated from step 1, along with the validator public key, are sent to Unpool.fi's MEV sharing contracts as an Ethereum transaction. The transaction is signed using a wallet of your choice, which is also used to withdraw the funds (known throughout Unpool.fi's documentation and code as the "beneficiary wallet").

### Step 1 - Generate The Signed Message

The [`sign.py`](signer/sign.py) script in the [`/signer`](signer) directory of this repository contains a Python script which will generate a BLS12-381 signature on random message content. The script must be run wherever the validator keystore file is stored.

##### Prerequisites

The script is written in Python and uses two external libraries written by the Ethereum Foundation:

1. The `staking-deposit-cli`, used to interface with Geth keystore files: https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/key_handling/keystore.py
2. The `py_ecc` library, used to generate GLS12-381 cryptographic signatures: https://github.com/ethereum/py_ecc

You must first have Python installed. Then you must install the prerequisites. I generally use `pip` like so:

```bash
pip install -r requirements.txt
```

##### Execution

```bash
$ python sign.py -h
usage: sign.py [-h] [--password PASSWORD] [--showPK] filename

Extract the public and private keys from a Geth keystore file in order to create a BLS sigature.

positional arguments:
  filename             The Geth keystore v4 file.

options:
  -h, --help           show this help message and exit
  --password PASSWORD  The password used for encrypting the private keys.
  --showPK             Set if you want to show the private key
```

The input to the script is a Geth keystore file <sup>[1](https://eips.ethereum.org/EIPS/eip-2335)</sup> <sup>[2](https://ethereum.org/en/developers/docs/data-structures-and-encoding/web3-secret-storage)</sup> and an optional keystore password. If you do not specify your keystore password on the command line, the script will ask for hidden input during execution.

An example execution of the script would be:
```bash
python sign.py ~/keys/keystore-m_12345_1234_0_0_0-1234567890.json --password "$(cat ~/keys/password.txt)"
```
The `.json` file is the filename of the validator keystore file, and `~/keys/password.txt` contains the password used during generation of the keystore file itself.

> **Caution:** The `--showPK` flag is used to display the validator's private key on the command line. It should be used for verification and debugging purposes only. **NEVER** give the validator private key to anyone.

The password is used to decrypt the validator's private key from the keystore file and use it to sign a message. The message contents are not important; only the proof of ownership of the validator is important.

The script will output the required information used during validator registration:

1. The validator's public key
2. The signed message
3. The signature used to sign the message

### Step 2 - Register the validator

There are multiple ways to register a validator, but in the end, they all call the `add_validator` function of the Unpool.fi MEV pool [Proxy Contract](https://goerli.etherscan.io/address/0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231#code).

> **Caution:** However you register your validator, ensure you are calling the Unpool.fi Proxy Contract at the address `0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231`.