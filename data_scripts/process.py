import boto3

bucket_name = 'cdsquantfinance'
s3 = boto3.resource('s3')
# s3.meta.client.download_file('cdsquantfinance', 'AAPL.csv', '/Users/marvin/zipline/data_scripts/AAPL.csv')

bucket = s3.Bucket(bucket_name)
exists = True

try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
except botocore.exceptions.ClientError as e:
    error_code = int(e.response['Error']['Code'])
    if error_code == 404:
        exists = False

# for obj in bucket.objects.all():
#     print(obj.key)

object = s3.Object(bucket_name, 'AAPL.csv')
print object.get()["Body"].read()