pragma solidity ^0.4.21;

// kinda erc20 (enough for testing)
contract ArtToken {
  mapping (address => uint256) balances;
  mapping (address => mapping (address => uint256)) allowed;

  uint256 public totalSupply;

  string public name;
  string public symbol;
  string public tokenURI;
  address public creator;

  event Transfer(address indexed _from, address indexed _to, uint256 _value);

  function ArtToken(string assetTitle, uint supply, string _tokenURI, address _creator, address _owner) public {
    name = assetTitle;
    totalSupply = supply;
    tokenURI = _tokenURI;
    creator = _creator;
    balances[_owner] = supply;
  }

  function transfer(address _to, uint256 _value) returns (bool success) {
    require(balances[msg.sender] >= _value);
    balances[msg.sender] -= _value;
    balances[_to] += _value;
    Transfer(msg.sender, _to, _value);
    return true;
  }

  function balanceOf(address _owner) constant returns (uint256 balance) {
    return balances[_owner];
  }


}

contract ArtTokenCreator {

  event AssetCreated(address indexed asset);

  function ArtTokenCreator() {}

  function createAsset(string assetname, uint supply, string tokenURI, address creator) public returns (ArtToken asset) {
    ArtToken newAsset;

    newAsset = new ArtToken(assetname, supply, tokenURI, creator, msg.sender);
    AssetCreated(newAsset);
    return newAsset;
  }
}
