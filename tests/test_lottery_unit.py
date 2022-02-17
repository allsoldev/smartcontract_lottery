from asyncio import exceptions
from brownie import Lottery, accounts, config, network, exceptions
import pytest
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_NETWORKS, get_account, fund_with_link, get_contract
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3


def test_get_entrance_fee():

    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()

    else:
        print("Entered Else")
        lottery = deploy_lottery()
        expected_entrace_fee = Web3.toWei(0.016, "ether")
        entrace_fee = lottery.getEntraceFee()
        assert entrace_fee >= expected_entrace_fee


def test_cant_enter_until_start():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter(
            {"from": get_account(), "value": lottery.getEntraceFee()})


def test_can_start_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account,
                  "value": lottery.getEntraceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account,
                  "value": lottery.getEntraceFee()})
    fund_with_link(lottery)
    lottery.EndLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_pick_winner():
    if network.show_active() not in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account,
                  "value": lottery.getEntraceFee()})
    lottery.enter({"from": get_account(index=1),
                  "value": lottery.getEntraceFee()})
    lottery.enter({"from": get_account(index=2),
                  "value": lottery.getEntraceFee()})
    fund_with_link(lottery)
    transaction = lottery.EndLottery({"from": account})
    request_Id = transaction.events["RequestedRandomness"]["requestId"]
    StaticRandom = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_Id, StaticRandom, lottery.address, {"from": account})

    startbal = account.balance()
    Lotbalance = lottery.balance()
    assert lottery.winner() == account
    assert lottery.balance() == 0
    assert account.balance() == startbal+Lotbalance
