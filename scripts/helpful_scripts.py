from brownie import accounts, network, config, MockV3Aggregator, Contract, VRFCoordinatorMock, LinkToken
DECIMLS = 8
StartValue = 200000000
FORKED_MAINNET_ENVIRNOMENT = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_NETWORKS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]

    elif id:
        accounts.load(id)
    elif network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS or network.show_active() in FORKED_MAINNET_ENVIRNOMENT:
        return accounts[0]

    else:
        return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_NETWORKS:
        if len(contract_type) <= 0:
            deploy_mock()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active(
        )][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi)
    return contract


def fund_with_link(contract_address, account=None, link_token=None, amount=5000000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Contract Funded")
    return tx


def deploy_mock(decimals=DECIMLS, initial_value=StartValue):
    account = get_account()
    MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("Mocks Deployed!")
