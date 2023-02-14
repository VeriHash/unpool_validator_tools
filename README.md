# Unpool.fi Validator Tools

A repository of tools for user administration of validators for [Unpool.fi](https://unpool.fi/)

## Registering a Validator

There are two steps to registering a validator with Unpool.fi:

1. The first step is generating a signed message using the validator's private key, which proves ownership of the validator itself.

2. The second step is requesting validator registration with Unpool.fi's MEV smoothing contracts. The signed message generated from step 1, along with the validator public key, are sent to Unpool.fi's MEV smoothing contracts as an Ethereum transaction. The transaction is signed using a wallet of your choice, which is also used to withdraw the funds (known throughout Unpool.fi's documentation and code as the "beneficiary wallet").

### Step 1 - Generate The Signed Message

The [`sign.py`](sign/sign.py) script in the [`/sign`](sign) directory of this repository contains a Python script which will generate a BLS12-381 signature on random message content. The script must be run wherever the validator keystore file is stored.

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
$ python sign.py \
~/keys/keystore-m_12345_1234_0_0_0-1234567890.json \
--password "$(cat ~/keys/password.txt)"

Enter the following information into the mev smoothing contract:
Public Key: 12345636d35753476269a8cd81c65b4433447f54b864b88cb73aca34b32cbfb73c6a9d3a83912337ccd89ad0778112a0
Message: 566ab2123ad742e0928489b015aaf8
Signature: 949999229999ab2123ad742e0928489b015aaf875f2530192837483f7a46839f90e0a6f16e54acbb71b2640bcfe005fa1673a2410f32ebe66b32995fd57f730d3c864b88cb73aca34b32cbfb73c6a9d3a83912337ccd89ad079a64122aa334cf
```
The `.json` file is the filename of the validator keystore file, and `~/keys/password.txt` contains the password used during generation of the keystore file itself.

> **Caution:** The `--showPK` flag is used to display the validator's private key on the command line. It should be used for verification and debugging purposes only. **NEVER** give the validator private key to anyone.

The password is used to decrypt the validator's private key from the keystore file and use it to sign a message. The message contents are not important; only the proof of ownership of the validator is important.

The script will output the required information used during validator registration:

1. The validator's public key
2. The signed message
3. The signature used to sign the message

### Step 2 - Register The Validator

There are multiple ways to register a validator, but in the end, they all call the `add_validator` function of the Unpool.fi MEV pool [Proxy Contract](https://goerli.etherscan.io/address/0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231#code).

> **Caution:** However you register your validator, ensure you are calling the Unpool.fi Proxy Contract at the address `0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231`.

#### Register using `register/register.py`

The [`register.py`](`register/register.py`) script in the [`/register`](register) directory of this repository will add your validator to the registration queue. You need to have a Web3 JSON RPC endpoint available for interacting with the chain.

##### Prerequisites

The script is written in Python and uses one external library written by the Ethereum Foundation:

1. The `web3` library, used to interface Ethereum: https://github.com/ethereum/web3.py

You must first have Python installed. Then you must install the prerequisites. I generally use `pip` like so:

```bash
pip install -r requirements.txt
```

##### Execution

```bash
$ python register.py -h
usage: register.py [-h] [--beneficiaryWalletPrivateKey BENEFICIARYWALLETPRIVATEKEY] endpoint proxyContractAddress proxyContractABIFilename publicKey message signature beneficiaryWalletAddress

Queue a validator for registration with Unpool.fi's MEV smoothing contracts

positional arguments:
  endpoint              The Web3 JSON RPC endpoint
  proxyContractAddress  The address of the proxy contract used for registration
  proxyContractABIFilename
                        The filename of the JSON-formatted ABI of the proxy contract
  publicKey             The validator's public key
  message               The message signed by the validator, from `sign.py`
  signature             The signature used to sign the message, from `sign.py`
  beneficiaryWalletAddress
                        The wallet allowed to withdraw your balance

options:
  -h, --help            show this help message and exit
  --beneficiaryWalletPrivateKey BENEFICIARYWALLETPRIVATEKEY
                        The private key of the beneficiary wallet
```

To execute the registration script you must have a working Web3 JSON RPC endpoint, information about the Proxy Contract, the output of a `sign.py` run, and beneficiary wallet credentials.

- The Web3 JSON RPC endpoint might be from [Infura](https://www.infura.io/) or a locally running Geth endpoint. Usually it is run on port 8545.
- The proxy contract address is `0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231`
- You can get the Proxy contract's ABI from Etherscan: https://goerli.etherscan.io/address/0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231#code. Export the JSON or copy/paste into a file on your system.
- The `publicKey`, `message`, and `signature` are the outputs from the script `sign/sign.py`, located in this repository.
- The `beneficiaryWalletAddress` and `beneficiaryWalletPrivateKey` are the address and private key of the wallet which will be used to withdraw that validator's MEV balance at a later date.

An example execution of the script would be:

```bash
$ python register.py \
> http://127.0.0.1:8545/ \
> 0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231 \
> ~/proxy_contract_abi.json \
> 12345636d35753476269a8cd81c65b4433447f54b864b88cb73aca34b32cbfb73c6a9d3a83912337ccd89ad0778112a0 \
> 566ab2123ad742e0928489b015aaf8 \
> 949999229999ab2123ad742e0928489b015aaf875f2530192837483f7a46839f90e0a6f16e54acbb71b2640bcfe005fa1673a2410f32ebe66b32995fd57f730d3c864b88cb73aca34b32cbfb73c6a9d3a83912337ccd89ad079a64122aa334cf \
> 0x3b0DF1Ab7405F7e5235874900811328fB153dF0B \
> --beneficiaryWalletPrivateKey "$(cat ~/private_key.txt)"

Sending transactions to register validator...
Transaction Hash: 0x11e3c325433bdf67c88b2466d074838249a80cbc3b041df14ce882c012241ad2
```

The beneficiary wallet is used to sign registration transaction, and is also committed on chain as the wallet used to withdraw the MEV smoothing balance for the registered validator.

> **Caution:** The `--beneficiaryWalletPrivateKey` flag inputs a wallet's private key on the command line. Please understand the source code of this script and know what it is doing with your private key. In this script, it is used to sign the registration transaction, but you should verify that statement. Anyone with your private key can steal your crypto! **NEVER** give a private key to anyone.

The script will output the transaction receipt hash upon successful execution.

#### Register using Etherscan

(To be written)
