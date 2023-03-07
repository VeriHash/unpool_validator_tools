# Unpool.fi Validator Tools

A repository of tools for user administration of validators for [Unpool.fi](https://unpool.fi/)

## Registering a Validator

There are two steps to registering a validator with Unpool.fi:

1. The first step is generating a signed message using the validator's private key, which proves ownership of the validator itself.

2. The second step is requesting validator registration with Unpool.fi's MEV smoothing contracts. The signed message generated from step 1, along with the validator public key, are sent to Unpool.fi's MEV smoothing contracts as an Ethereum transaction. The transaction is signed using a wallet of your choice, which is also used to withdraw the funds (known throughout Unpool.fi's documentation and code as the "beneficiary wallet").

The scripts within this repository will generate a signature. If you would like, the scripts can also broadcast the transaction to the chain. You can either run everything via the "main" script, or run them individually. You can run the scripts online, partially offline, and fully offline.

When running fully online with a specified JSON RPC endpoint, the script will broadcast the transaction to the specified Ethereum chain (mainnet or Goerli supported). When running partially offline, the script will download the Unpool proxy contract ABI, which is required to generate an offline signed transaction. When running fully offline, you are required to have the proxy contract ABI. Then, the script will generate a signed transaction for you. You can take the signed transaction and broadcast it via something like Etherscan.

If you would like, you can also just run the "sign" step and copy/paste the output into the proxy contract via Etherscan, and skip all the other steps.

## Run via Docker

### Build the image

```
$ sudo -E docker build -t unpool.main -f main.dockerfile .
```

### Run the main docker image

#### Online

```
$ sudo -E docker run --rm -i unpool.main "$(cat reference/v4_scrypt.json)" yes "$(cat ~/wallet.txt)" --keystorePassword $(cat reference/v4_password.txt) --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --endpoint http://127.0.0.1:8545
```

#### Offline

```
$ sudo -E docker run --rm -i unpool.main "$(cat reference/v4_scrypt.json)" yes "$(cat ~/wallet.txt)" --keystorePassword $(cat reference/v4_password.txt) --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --nonce <walletNonce> --proxyContractAbiFilename proxy_abi.json --noVerify
```

## Run via Python

The script is written in Python and uses two external libraries written by the Ethereum Foundation:

1. The `staking-deposit-cli`, used to interface with Geth keystore files: https://github.com/ethereum/staking-deposit-cli/blob/master/staking_deposit/key_handling/keystore.py
2. The `py_ecc` library, used to generate BLS12-381 cryptographic signatures: https://github.com/ethereum/py_ecc

You must first have Python installed. Then you must install the prerequisites. I generally use `pip` like so:

```bash
pip install -r requirements.txt
```

### Run `main.py`, which does everything

#### Online

```
$ python main.py "$(cat reference/v4_scrypt.json)" yes 0x123456 --keystorePassword $(cat reference/v4_password.txt) --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --endpoint http://127.0.0.1:8545

Is the signature valid? True

Using execution layer JSON RPC endpoint. Setting online mode.

Raw signed transaction:
0x02f90213058208ef84038<snipd68eb3d55bed887

Sending validator registration transaction...
Transaction Hash: 0x9e2a1a66afa8b62d5e26085a46f787593d24ffdaf4215267a07b4172828b94ae
```

#### No chain interactions, but with contract ABI download

```
$ python main.py "$(cat reference/v4_scrypt.json)" yes 0x123456 --keystorePassword $(cat reference/v4_password.txt) --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --nonce 2288

Is the signature valid? True

You have not specified an execution layer JSON RPC endpoint. Setting offline mode.

Raw signed transaction:
0x02f90214058208f0840525<snip>ffde85442aad63d6f194bea3
```

#### No chain interactions, no contract ABI download, and no signature verification

```
$ python main.py "$(cat reference/v4_scrypt.json)" yes 0x123456 --keystorePassword $(cat reference/v4_password.txt) --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --nonce 2288 --proxyContractAbiFilename proxy_abi.json --noVerify

You have not specified an execution layer JSON RPC endpoint. Setting offline mode.

Raw signed transaction:
0x02f90214058<snip>497ac241097f14
```

### Or, run the scripts individually

You can also run each section of the registration individually, in order to have more control over
what is happening, or to learn what is going on internally.

#### Sign A Message

The input to the script is the contents of a Geth keystore file <sup>[1](https://eips.ethereum.org/EIPS/eip-2335)</sup> <sup>[2](https://ethereum.org/en/developers/docs/data-structures-and-encoding/web3-secret-storage)</sup> and an optional keystore password. If you do not specify your keystore password on the command line, the script will ask for hidden input during execution.

Default:
```
$ python sign.py "$(cat reference/v4_pbkdf2.json)" --keystorePassword $(cat reference/v4_password.txt)

Enter the following information into the mev smoothing contract:
Validator Public Key: 9612d7a727c9d0a22e185a1c768478dfe919cada9266988cb32359c11f2b7b27f4ae4040902382ae2910c15e2b420d07
Message: a31fd2712cac4fafa88812f261a9aad6
Signature: a3dddad29ea181db77a49287f880263f0a360bbcb9d3992f4e766e8dbd85eeb16713ae9c22b62792ee0d578ed6b3822b0b703f6f816e091ddcdc1e381cd24267ecc8a9d3a00ef56edff7dd4710730e3a5ac533877b209dea840476076fe721dc

Is the signature valid? True
```

With `--noVerify`, if you don't care about signature verification.

```
$ python sign.py "$(cat reference/v4_pbkdf2.json)" --keystorePassword $(cat reference/v4_password.txt) --noVerify

Enter the following information into the mev smoothing contract:
Validator Public Key: 9612d7a727c9d0a22e185a1c768478dfe919cada9266988cb32359c11f2b7b27f4ae4040902382ae2910c15e2b420d07
Message: b42586ce27814d3e80d8ae0e27839cbd
Signature: b7b6c193b6a40254325f079bbe3cc1c92eb8c58066e5b7a0f231947c9d3b93f1519b9de0e008035624373ac317f28d4b1112e689b388d88976141a05b0ac91236769cf00432ef11bca0c9364725184b97a15ea68b0a5676d2e77b8801d2b23a4
```

The `reference/v4_pbkdf2.json` file is the validator keystore file. We give the contents of the file to the script so we don't' have to mount a filesystem during Docker execution. The `reference/v4_password.txt` contains the password used during generation of the keystore file itself.

The password is used to decrypt the validator's private key from the keystore file and use it to sign a message. The message contents are not important; only the proof of ownership of the validator is important.

The script will output the required information used during validator registration:

1. The validator's public key
2. The signed message
3. The signature used to sign the message

#### Verify The Signature

Verifying the signature if handy if you want to save gas. It runs the same code as the Oracle uses to verify signatures.

```
$ python verify.py 9612d7a727c9d0a22e185a1c768478dfe919cada9266988cb32359c11f2b7b27f4ae4040902382ae2910c15e2b420d07 b42586ce27814d3e80d8ae0e27839cbd b7b6c193b6a40254325f079bbe3cc1c92eb8c58066e5b7a0f231947c9d3b93f1519b9de0e008035624373ac317f28d4b1112e689b388d88976141a05b0ac91236769cf00432ef11bca0c9364725184b97a15ea68b0a5676d2e77b8801d2b23a4

Is the signature valid? True
```

#### Create Registration Transaction

There are multiple ways to register a validator, but in the end, they all call the `add_validator` function of the Unpool.fi MEV pool [Proxy Contract](https://goerli.etherscan.io/address/0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231#code).

> **Caution:** However you register your validator, ensure you are calling the Unpool.fi Proxy Contract at the address `0x606A1cB03cED72Cb1C7D0cdCcb630eDba2eF6231`.

During the overall process we create a registration transaction. You can either broadcast the transaction to the chain yourself, or use the "broadcast" script to do it for you.

The beneficiary wallet is used to sign registration transaction, and is also committed on chain as the wallet used to withdraw the MEV smoothing balance for the registered validator.

Offline, beneficiary wallet private key not specified.
```
$ python transaction.py 864d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660 3a7294e3539848c1bd68808cba87b076 ad21bf340f2748725c43ee1ada80a675c153bcb144aab31fba8418b902abe989d842f3e876228fb13852ae8606404234143309360ddcde5674c96dc087662bd363da53d47545fb15bfeb4f1fe05c6bb58568b1fb308e2ff4f338ccb20056a0fd True 0x123456 --nonce 123456

Is the signature valid? True

Please enter the beneficary wallet's private key. (Caution, please understand the source code of this script and know what it is doing with your private key. It is used to sign the registration transaction, but you should verify that statement. Anyone with your private key can steal your crypto!):

You have not specified an execution layer JSON RPC endpoint. Setting offline mode.

Raw signed transaction:
0x02f90214058204<snip>173bd94b151380bbe9
```

Offline, beneficiary wallet private key specified via `--beneficiaryWalletPrivateKey` and signature verification disabled via `--noVerify`. Will still download the contract via unpool.fi.

> **Caution:** The `--beneficiaryWalletPrivateKey` flag inputs a wallet's private key on the command line. Please understand the source code of this script and know what it is doing with your private key. In this script, it is used to sign the registration transaction, but you should verify that statement. Anyone with your private key can steal your crypto! **NEVER** give a private key to anyone.

```
$ python transaction.py 864d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660 3a7294e3539848c1bd68808cba87b076 ad21bf340f2748725c43ee1ada80a675c153bcb144aab31fba8418b902abe989d842f3e876228fb13852ae8606404234143309360ddcde5674c96dc087662bd363da53d47545fb15bfeb4f1fe05c6bb58568b1fb308e2ff4f338ccb20056a0fd True 0x123456 --nonce 123456 --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --noVerify

You have not specified an execution layer JSON RPC endpoint. Setting offline mode.

Raw signed transaction:
0x02f90214058204<snip>173bd94b151380bbe9
```

Offline, same as above, but not even an internet connection, like in an air-gapped environment. We
have to specify the proxy contract ABI filename via `--proxyContractAbiFilename`. We will have had
to download it beforehand from https://unpool.fi/contracts/proxy_abi.json or use the one in this
repository.

```
$ python transaction.py 864d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660 3a7294e3539848c1bd68808cba87b076 ad21bf340f2748725c43ee1ada80a675c153bcb144aab31fba8418b902abe989d842f3e876228fb13852ae8606404234143309360ddcde5674c96dc087662bd363da53d47545fb15bfeb4f1fe05c6bb58568b1fb308e2ff4f338ccb20056a0fd True 0x123456 --nonce 123456 --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --proxyContractAbiFilename proxy_abi.json --noVerify

You have not specified an execution layer JSON RPC endpoint. Setting offline mode.

Raw signed transaction:
0x02f90215058<snip>65f14e5
```

Online, beneficiary wallet private key specified via `--beneficiaryWalletPrivateKey` and signature verification disabled via `--noVerify`. Notice we need to specify `--endpoint` to enable online mode.
```
$ python transaction.py 364d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660 437294e3539848c1bd68808cba87b076 3421bf340f2748725c43ee1ada80a675c153bcb144aab31fba8418b902abe989d842f3e876228fb13852ae8606404234143309360ddcde5674c96dc087662bd363da53d47545fb15bfeb4f1fe05c6bb58568b1fb308e2ff4f338ccb20056a0fd True 0x123456 --endpoint http://127.0.0.1:8545 --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --noVerify

Using execution layer JSON RPC endpoint. Setting online mode.

Raw signed transaction:
0x02f90214058204<snip>173bd94b151380bbe9
```

#### Broadcast The Transaction

To broadcast the registration you must have a working Web3 JSON RPC endpoint.

The Execution Layer JSON RPC endpoint might be from [Infura](https://www.infura.io/) or a locally running Geth endpoint. Usually it is run on port 8545.

The script will output the transaction receipt hash upon successful execution.

```
$ python broadcast.py http://127.0.0.1:8545 0x02f90214058208c584<snip>3642529f9661b

Sending validator registration transaction...
Transaction Hash: 0xefa77a809d11dcfc70c91629dd41073ff3c987c275c6018294da04c66fbda895
```
