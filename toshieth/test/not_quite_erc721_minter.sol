pragma solidity ^0.4.19;

contract Mintable {
  function mint(address _owner, uint256 _tokenId, string _metadata) external;
}

contract NonFungibleTokenMinter {

  address public tokenAddress;

  event TokenMinted(address _to, uint256 _tokenId);

  function NonFungibleTokenMinter(address _tokenAddress) {
    tokenAddress = _tokenAddress;
  }

  function mint(uint256 _tokenId, string _metadata) public {
    Mintable token = Mintable(tokenAddress);
    token.mint(msg.sender, _tokenId, _metadata);
    TokenMinted(msg.sender, _tokenId);
  }
}
