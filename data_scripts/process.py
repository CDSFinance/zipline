import boto3
import StringIO
import csv

bucket_name = 'cdsquantfinance'
start_year = 2000
start_month = 1
start_day = 1

def getStartDate():
  y = str(start_year)
  m = str(start_month)
  d = str(start_day)

  if (start_month < 10):
    m = "0" + m
  if (start_day < 10):
    d = "0" + d
  return y + "-" + m + "-" + d

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

for obj in bucket.objects.limit(count = 1):
  data = obj.get()["Body"].read()
  
  while data.find(getStartDate()) == -1:
    start_day += 1
  
  startIndex = data.find(getStartDate())
  data =  data[startIndex:]
  f = StringIO.StringIO(data)
  reader = csv.reader(f, delimiter=',')
  for row in reader:
    print '\t'.join(row)
    
  




