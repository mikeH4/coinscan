import subprocess

def create_pm2(
    name: str,
    script: str,
    args: str = "", *,
    restart: bool = True
):
    args = f"" if args.strip() == "" else f"-- {args}"
    restart_str = "" if restart else "--no-autorestart"
    cmd = f"""pm2 restart {name} || pm2 start {script} {restart_str} --interpreter ./env/bin/python --name {name} {args}"""
    return cmd

subcmd = [
    "cd /home/blockchain/",
    "unzip -o archive.zip",
    "rm archive.zip",
    create_pm2("api","api.py")
]

services = [
    "copy_token_prices",
    "poll_listings",
    "poll_new",
    "poll_pairs",
    "poll_verified",
    "sync_listing_tokens",
    "sync_verified",
    "update_holders",
]

subcmd += [
    create_pm2(
        service,
        "run_service.py",
        service,
        restart = service[:5] != "sync_"
    )
    for service
    in services
]

subcmd += [
    "systemctl restart nginx",
    "systemctl status nginx",
]

subcmd_str =  " ; ".join(subcmd)

cmds = [
    "git archive --format zip --output archive.zip master",
    "scp archive.zip coinscan:/home/blockchain",
    f"ssh coinscan '{subcmd_str}'",
]

subprocess.call(" && ".join(cmds),shell=True)