// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";

contract TrueMarkMintEngine is ERC721URIStorage, Ownable, IERC2981 {
    struct NFTType {
        string name;
        bool enabled;
    }
    mapping(uint256 => NFTType) public nftTypes;
    uint256 public nextTokenId;
    address public admin;
    uint96 public constant SALE_ROYALTY = 150; // 1.5% (basis points)
    uint96 public constant LICENSE_ROYALTY = 300; // 3% (basis points)
    mapping(uint256 => address) public minters;
    mapping(uint256 => uint96) public customRoyalty;

    event Minted(address indexed to, uint256 indexed tokenId, string nftType);

    constructor() ERC721("True Mark Mint Engine", "TRUEMARK") {
        admin = msg.sender;
        nftTypes[0] = NFTType("K-NFT", true);
        nftTypes[1] = NFTType("H-NFT", true);
        nftTypes[2] = NFTType("L-NFT", true);
        nftTypes[3] = NFTType("C-NFT", true);
    }

    function mint(address to, string memory uri, uint256 nftTypeId) external onlyOwner returns (uint256) {
        require(nftTypes[nftTypeId].enabled, "NFT type not enabled");
        uint256 tokenId = nextTokenId++;
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
        minters[tokenId] = to;
        emit Minted(to, tokenId, nftTypes[nftTypeId].name);
        return tokenId;
    }

    function setNFTType(uint256 typeId, string memory name, bool enabled) external onlyOwner {
        nftTypes[typeId] = NFTType(name, enabled);
    }

    // EIP-2981 royalty info (sale royalty)
    function royaltyInfo(uint256 tokenId, uint256 salePrice) external view override returns (address, uint256) {
        uint256 royaltyAmount = (salePrice * SALE_ROYALTY) / 10000;
        return (minters[tokenId], royaltyAmount);
    }

    // Licensing royalty (off-chain enforcement, returns royalty amount)
    function licenseRoyalty(uint256 tokenId, uint256 licensePrice) external view returns (address, uint256) {
        uint256 royaltyAmount = (licensePrice * LICENSE_ROYALTY) / 10000;
        return (minters[tokenId], royaltyAmount);
    }

    // Inheritance logic (admin can transfer ownership to heir)
    function transferToHeir(uint256 tokenId, address heir) external {
        require(msg.sender == ownerOf(tokenId) || msg.sender == admin, "Not authorized");
        _transfer(ownerOf(tokenId), heir, tokenId);
    }
}
