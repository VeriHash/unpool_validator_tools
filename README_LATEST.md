## Run `main.py`, which does everything

## Or, run the scripts individually

You can also run each section of the registration individually, in order to have more control over
what is happening, or to learn what is going on internally.

### Sign A Message

Default:
```
$ python sign.py ~/keystore-m_12345_3600_0_0_0-0123456789.json --keystorePassword "$(cat ~/password.txt)"

Enter the following information into the mev smoothing contract:
Validator Public Key: 864d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660
Message: 1c073708d3ba43678f63049c366b2720
Signature: aea0f03f490a51a6d4e662c9d8f7aed37d7b9d87e5517ef307165a81fade284de507d3b92ce9baaa453c1827d4461817165a9fbbb335e7d46d3ac2f4c701fcf6ab7ba3797b750db7c435af98a4549cb45f269ab999216231dff6f6206255770b

Is the signature valid? True
```

With `--noVerify`
```
$ python sign.py ~/keystore-m_12345_3600_0_0_0-0123456789.json --keystorePassword "$(cat ~/password.txt)" --noVerify

Enter the following information into the mev smoothing contract:
Validator Public Key: 864d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660
Message: 0114f986ebdd4a88a7d866b4d7fb0b11
Signature: a8de2cdd1a6b18f3b16c0bb0caf03e45d38da024137f3e5765d6e5a9608e9c4a31a4395675eaa9b5135dbbe1ffa43fa1059601e149fbf97656311520fb7bf5ed4980078f742ee0b951f72f61f9227d16aa7a682c583e69050dbdb0fd3355e522
```

### Verify The Signature

```
$ python verify.py 864d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660 3a7294e3539848c1bd68808cba87b076 ad21bf340f2748725c43ee1ada80a675c153bcb144aab31fba8418b902abe989d842f3e876228fb13852ae8606404234143309360ddcde5674c96dc087662bd363da53d47545fb15bfeb4f1fe05c6bb58568b1fb308e2ff4f338ccb20056a0fd

Is the signature valid? True
```

### Create Registration Transaction

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
$ python transaction.py 364d6e36d35753476269a8cd81c65bc8b1847f54b864b88cb73aca0d3d2cbfb73c6a9d396c39e7b7ccd89ad07786c660 437294e3539848c1bd68808cba87b076 3421bf340f2748725c43ee1ada80a675c153bcb144aab31fba8418b902abe989d842f3e876228fb13852ae8606404234143309360ddcde5674c96dc087662bd363da53d47545fb15bfeb4f1fe05c6bb58568b1fb308e2ff4f338ccb20056a0fd True 0x5b0DF4Ab7905F7e5098865900819188fA153dD0D --endpoint http://127.0.0.1:8545 --beneficiaryWalletPrivateKey $(cat ~/private_key.txt) --noVerify

Using execution layer JSON RPC endpoint. Setting online mode.

Raw signed transaction:
0x02f90214058204<snip>173bd94b151380bbe9
```

### Broadcast The Transaction

```
$ python broadcast.py http://127.0.0.1:8545 0x02f90214058208c584<snip>3642529f9661b

Sending validator registration transaction...
Transaction Hash: 0xefa77a809d11dcfc70c91629dd41073ff3c987c275c6018294da04c66fbda895
```
