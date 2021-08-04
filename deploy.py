subcmd = [
    "cd /home/blockchain/",
    "unzip -o archive.zip",
    "rm archive.zip",
]

services = [
    "copy_token_prices",
    "poll_listings",
    "poll_new",
    "poll_pairs",
    "poll_verified",
    "synv_listing_tokens",
    "sync_verified",
    "update_holders",
]

# for script in services:
#     subcmd += [f"""pm2 restart service-{script} || pm2 start run_service.py --interpreter ./env/bin/python --name service-{script} -- {script}"""]

subcmd += [
    "systemctl restart nginx",
    "systemctl status nginx",
]

subcmd_str =  "&& ".join(subcmd)
cmds = [
    "git archive --format zip --output archive.zip master",
    "scp archive.zip coinscan:/home/blockchain",
    f"ssh coinscan '{subcmd_str}'",
]

print(subcmd)
# subprocess.call(" && ".join(cmds),shell=True)