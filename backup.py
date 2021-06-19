import boto3
from botocore.exceptions import NoCredentialsError
import settings

def upload_to_aws(filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.BACKUP_AWS_ACCESS_KEY,
        aws_secret_access_key=settings.BACKUP_AWS_SECRET_KEY
    )

    try:
        fn = f"{settings.BACKUP_DIR}{filename}"
        print("FROM:",fn)
        print("TO:",filename)
        s3.upload_file(fn, "coinscan-backups", filename)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

import subprocess
if __name__ == "__main__":
    dbname = "tokens"

    dbuser = "postgres" if settings.sandbox == True else "coinscan"
    sandbox_str = "-sandbox" if settings.sandbox == True else "-prod"
    filename = f"{dbname}-fc{sandbox_str}.dump"
    cmds = [
        f"cd {settings.BACKUP_DIR}",
        f'PGPASSWORD="root" pg_dump -h localhost -U {dbuser} -Fc {dbname} > {filename}'
    ]
    subprocess.call(" && ".join(cmds),shell=True)
    uploaded = upload_to_aws(filename)