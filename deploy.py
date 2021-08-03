import subprocess

subcmd = [
    "cd /home/blockchain/",
    "unzip -o archive.zip",
    "rm archive.zip",
    "systemctl restart nginx",
    "systemctl status nginx",
]
subcmd_str =  "&& ".join(subcmd)
cmds = [
    "git archive --format zip --output archive.zip master",
    "scp archive.zip coinscan:/home/blockchain",
    f"ssh coinscan '{subcmd_str}'",
]

subprocess.call(" && ".join(cmds),shell=True)