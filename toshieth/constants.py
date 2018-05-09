from toshi.ethereum.utils import sha3

TRANSFER_TOPIC = '0x' + sha3("Transfer(address,address,uint256)").hex()
DEPOSIT_TOPIC = '0x' + sha3("Deposit(address,uint256)").hex()
WITHDRAWAL_TOPIC = '0x' + sha3("Withdrawal(address,uint256)").hex()

WETH_CONTRACT_ADDRESS = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"

ERC20_NAME_CALL_DATA = "0x" + sha3("name()")[:4].hex() + "0" * 56
ERC20_SYMBOL_CALL_DATA = "0x" + sha3("symbol()")[:4].hex() + "0" * 56
ERC20_DECIMALS_CALL_DATA = "0x" + sha3("decimals()")[:4].hex() + "0" * 56
ERC20_BALANCEOF_CALL_DATA = "0x" + sha3("balanceOf(address)")[:4].hex()
