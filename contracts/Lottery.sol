//SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    uint256 public USDEntryFee;
    address payable[] public players;
    AggregatorV3Interface internal EthUSDPriceFeed;
    enum LOTTERY_STATE {
        CLOSE,
        OPEN,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 internal fee; // if error comes try changinf fee and keyhash to public
    bytes32 internal keyhash;
    address payable public winner;
    uint256 public randomNumber;
    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _PriceFeed,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        USDEntryFee = 50 * (10**18);
        EthUSDPriceFeed = AggregatorV3Interface(_PriceFeed);
        lottery_state = LOTTERY_STATE.CLOSE;
        fee = _fee;
        keyhash = _keyhash;
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Can't enter in closed state "
        );
        require(msg.value >= getEntraceFee(), "Not enough ETH");
        players.push(payable(msg.sender));
    }

    function getEntraceFee() public view returns (uint256) {
        (, int256 price, , , ) = EthUSDPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        uint256 EthToEnter = (USDEntryFee * 10**18) / (adjustedPrice);
        return EthToEnter;
    }

    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSE, "Can't restart ");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function EndLottery() public onlyOwner {
        /*         require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Can't End a closed Lottery "
        ); */
        /*        uint256(
            keccak256(
                abi.encodePacked(
                    block.number,
                    msg.sender,
                    block.difficulty,
                    block.timestamp
                )
            )
        ) % players.length; */
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;

        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Not in calculating state"
        );
        require(_randomness > 0, "Random number is 0");
        uint256 WinnerIndex = _randomness % players.length;
        winner = players[WinnerIndex];
        winner.transfer(address(this).balance);
        randomNumber = _randomness;
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSE;
    }
}
