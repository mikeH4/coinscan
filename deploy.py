import subprocess

subcmd = [
    "sudo nginx -t",
    "cd /home/coinscan/",
    "unzip -o archive.zip",
    "rm archive.zip",
    "systemctl restart coinscan_api",
    "systemctl status coinscan_api",
    "systemctl restart nginx",
    "systemctl status nginx",
]
subcmd_str =  "&& ".join(subcmd)
cmds = [
    "git archive --format zip --output archive.zip master",
    "scp archive.zip coinscan:/home/coinscan",
    "scp nginx.conf coinscan:/etc/nginx/nginx.conf",
    f"ssh coinscan '{subcmd_str}'",
]

subprocess.call(" && ".join(cmds),shell=True)