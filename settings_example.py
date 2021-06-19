sandbox = True # False

BACKUP_AWS_ACCESS_KEY = "XXXX"
BACKUP_AWS_SECRET_KEY = "XXXX"
BACKUP_DIR = "/path/to"

def __getattr__(name: str):
    return None