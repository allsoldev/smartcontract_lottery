from brownie import Lottery, accounts, config, network, exceptions
import pytest
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_NETWORKS, get_account, fund_with_link, get_contract
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import time


def test_int():
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account,
                   "value": lottery.getEntraceFee()})
    lottery.enter({"from": account,
                   "value": lottery.getEntraceFee()})
    lottery.enter({"from": account,
                   "value": lottery.getEntraceFee()})
    fund_with_link(lottery)
    lottery.EndLottery({"from": account})
    time.sleep(60)
    assert lottery.winner() == account
    assert lottery.balance() == 0
