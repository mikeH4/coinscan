def main():
    from time import time
    from library.Repeater import Repeater
    from core.sources.BscScan import BscScan
    from core.Holders.AddressInfo import AddressInfo
    from library.postgres import DB

    with DB("tokens") as db:
        repeater = Repeater(min=0)
        bscscan = BscScan()

        while True:
            with repeater.manager():
                addresses = [
                    address_info.address
                    for address_info
                    in AddressInfo.unknown_contract(db=db,limit=30)
                ]
                addresses_len = len(addresses)

                for i,address in enumerate(addresses):
                    data = bscscan.address_info(address)
                    
                    AddressInfo(
                        address=address,
                        is_contract=data["is_contract"],
                        bscscan_tag=data["bscscan_tag"],
                        updated=time(),
                        added=time()
                    ).insert(db=db,replace=True)

                    db.conn.commit()

                    print(f"{i+1}/{addresses_len} Info added for {address}")