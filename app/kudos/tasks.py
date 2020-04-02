import time

from django.conf import settings

from app.redis_service import RedisService
from celery import app
from celery.utils.log import get_task_logger
from dashboard.utils import get_web3
from hexbytes import HexBytes
from kudos.models import KudosTransfer, TokenRequest
from kudos.utils import kudos_abi
from marketing.mails import notify_kudos_minted
from web3 import Web3

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2
delay_if_gas_prices_gt = 10

@app.shared_task(bind=True, max_retries=10)
def mint_token_request(self, token_req_id, retry=False):
    """
    :param self:
    :param token_req_id:
    :return:
    """
    with redis.lock("tasks:all_kudos_requests", timeout=LOCK_TIMEOUT):
        with redis.lock("tasks:token_req_id:%s" % token_req_id, timeout=LOCK_TIMEOUT):
            from kudos.management.commands.mint_all_kudos import sync_latest
            from gas.utils import recommend_min_gas_price_to_confirm_in_time
            from dashboard.utils import has_tx_mined
            obj = TokenRequest.objects.get(pk=token_req_id)
            multiplier = 1
            gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * multiplier)
            if gas_price > delay_if_gas_prices_gt:
                self.retry(countdown=120)
                return
            tx_id = obj.mint(gas_price)
            if tx_id:
                while not has_tx_mined(tx_id, obj.network):
                    time.sleep(1)
                sync_latest(0)
                sync_latest(1)
                sync_latest(2)
                sync_latest(3)
                notify_kudos_minted(obj)
            else:
                self.retry(countdown=(30 * (self.request.retries + 1)))


@app.shared_task(bind=True, max_retries=10)
def redeem_bulk_kudos(self, kt_id, retry=False):
    """
    :param self:
    :param kt_id:
    :return:
    """
    with redis.lock("tasks:all_kudos_requests", timeout=LOCK_TIMEOUT):
        with redis.lock("tasks:redeem_bulk_kudos:%s" % kt_id, timeout=LOCK_TIMEOUT):
            from dashboard.utils import has_tx_mined
            from gas.utils import recommend_min_gas_price_to_confirm_in_time
            try:
                multiplier = 1
                gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * multiplier)
                if gas_price > delay_if_gas_prices_gt:
                    self.retry(countdown=120)
                    return

                obj = KudosTransfer.objects.get(pk=kt_id)
                w3 = get_web3(obj.network)
                token = obj.kudos_token_cloned_from
                if token.owner_address.lower() != '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F'.lower():
                    raise Exception("kudos isnt owned by Gitcoin; cowardly refusing to spend Gitcoin's ETH minting it")
                kudos_owner_address = settings.KUDOS_OWNER_ACCOUNT
                kudos_owner_address = Web3.toChecksumAddress(kudos_owner_address)
                kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
                contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
                nonce = w3.eth.getTransactionCount(kudos_owner_address)
                tx = contract.functions.clone(Web3.toChecksumAddress(obj.receive_address), token.token_id, 1).buildTransaction({
                    'nonce': nonce,
                    'gas': 500000,
                    'gasPrice': gas_price,
                    'value': int(token.price_finney / 1000.0 * 10**18),
                })
                private_key = settings.KUDOS_PRIVATE_KEY
                signed = w3.eth.account.signTransaction(tx, private_key)
                obj.txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
                obj.receive_txid = obj.txid
                obj.save()
                while not has_tx_mined(obj.txid, obj.network):
                    time.sleep(1)
                pass
            except Exception as e:
                print(e)
                self.retry(countdown=(30 * (self.request.retries + 1)))
