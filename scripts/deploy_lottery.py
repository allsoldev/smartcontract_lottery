
import time
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, accounts, config, network


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(get_contract(
        "eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"], {"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))
    print("Lottery Deployed")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_tx = lottery.startLottery({"from": account})
    start_tx.wait(1)
    print("Lottery Started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    enter_value = lottery.getEntraceFee()+100000000
    enter_tx = lottery.enter({"from": account, "value": enter_value})
    enter_tx.wait(1)
    print("Entered in the Lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    end_tx = lottery.EndLottery({"from": account})
    end_tx.wait(1)
    print("Awaiting Response")
    time.sleep(200)
    print(f"{lottery.winner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
