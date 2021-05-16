import subprocess

cmds = [
    "git archive --format zip --output archive.zip master",
    "scp archive.zip coinscan:/home/coinscan",
    "ssh coinscan 'cd /home/coinscan/ && unzip -o archive.zip && rm archive.zip'",
]

subprocess.call(" && ".join(cmds),shell=True)