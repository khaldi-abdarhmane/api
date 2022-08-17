import boto3
from botocore.exceptions import ClientError
import io
import hashlib


s3_client = boto3.client('s3', region_name='eu-west-1', aws_access_key_id='AKIAUDAPALWJEOH34RHH',
                               aws_secret_access_key='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')


def upload_my_file(bucket, folder, file_as_binary, file_name):
        file_as_binary = io.BytesIO(file_as_binary)
        key = folder+"/"+file_name
        try:
            s3_client.upload_fileobj(file_as_binary, bucket, key)
        except ClientError as e:
            print(e)
            return False
        return True
    

hasher = hashlib.md5()
def hash_my_file(pathtxt):
     BLOCKSIZE = 65536
     with open(pathtxt, 'rb') as afile:
          buf = afile.read(BLOCKSIZE)
          while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
     return hasher.hexdigest()


