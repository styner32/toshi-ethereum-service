pragma solidity ^0.4.21;

contract Token {

  function totalSupply() constant returns (uint supply) {}
  function balanceOf(address _owner) constant returns (uint balance) {}
  function transfer(address _to, uint _value) returns (bool success) {}
  function transferFrom(address _from, address _to, uint _value) returns (bool success) {}
  function approve(address _spender, uint _value) returns (bool success) {}
  function allowance(address _owner, address _spender) constant returns (uint remaining) {}

  event Transfer(address indexed _from, address indexed _to, uint _value);
  event Approval(address indexed _owner, address indexed _spender, uint _value);
}

contract SimpleExchange {

  address public ZRX_CONTRACT;
  uint256 public ZRX_COST = 10 ** 18;

  mapping (bytes32 => bool) orders;

  constructor(address _zrx_contract) {
    ZRX_CONTRACT = _zrx_contract;
  }

  function createOrder(address _src, uint256 _src_val, address _dst, uint256 _dst_val) public {
    require(_src != 0);
    require(_dst != 0);
    bytes32 hash = sha3(msg.sender, _src, _src_val, _dst, _dst_val);
    orders[hash] = true;
  }

  function fillOrder(address _orderer, address _src, uint256 _src_val, address _dst, uint256 _dst_val) public {
    bytes32 hash = sha3(_orderer, _src, _src_val, _dst, _dst_val);
    require(orders[hash] != false);
    orders[hash] = false;
    Token srcToken = Token(_src);
    Token dstToken = Token(_dst);
    Token zrxToken = Token(ZRX_CONTRACT);
    require(srcToken.balanceOf(_orderer) >= _src_val);
    require(dstToken.balanceOf(msg.sender) >= _dst_val);
    require(zrxToken.balanceOf(_orderer) >= ZRX_COST);
    require(zrxToken.balanceOf(msg.sender) >= ZRX_COST);
    require(srcToken.allowance(_orderer, this) >= _src_val);
    require(dstToken.allowance(msg.sender, this) >= _dst_val);
    require(zrxToken.allowance(_orderer, this) >= ZRX_COST);
    require(zrxToken.allowance(msg.sender, this) >= ZRX_COST);

    srcToken.transferFrom(_orderer, msg.sender, _src_val);
    dstToken.transferFrom(msg.sender, _orderer, _dst_val);
    zrxToken.transferFrom(msg.sender, this, ZRX_COST);
    zrxToken.transferFrom(_orderer, this, ZRX_COST);
  }
}
