import boto3
import StringIO
import csv

bucket_name = 'cdsquantfinance'
start_year = 2000
start_month = 1
start_day = 1

def get_start_date():
  y = str(start_year)
  m = str(start_month)
  d = str(start_day)

  if (start_month < 10):
    m = "0" + m
  if (start_day < 10):
    d = "0" + d
  return y + "-" + m + "-" + d

def mean(col):
  c = [float(i) for i in col]
  return sum(c)/float(len(c))

def stdev(col, mean):
  c = [(float(i) - mean)**2 for i in col]
  return (sum(c)/float(len(c) - 1))**0.5

def normalize(col, mean, stdev):
  c = [((float(i) - mean)/stdev) for i in col]
  return c

s3 = boto3.resource('s3')
# s3.meta.client.download_file(
  # 'cdsquantfinance', 
  # 'AAPL.csv', 
  # '/Users/marvin/zipline/data_scripts/AAPL.csv')

bucket = s3.Bucket(bucket_name)
exists = True

try:
  s3.meta.client.head_bucket(Bucket=bucket_name)
except botocore.exceptions.ClientError as e:
  error_code = int(e.response['Error']['Code'])
  if error_code == 404:
    exists = False

# Processes each csv file in the bucket
for obj in bucket.objects.limit(count = 1):
  # dumps csv conteents into a string
  content_str = obj.get()["Body"].read()
  file_name = obj.key
  
  # find the first date starting at the start date where the market is open
  while content_str.find(get_start_date()) == -1:
    start_day += 1
  
  start_i = content_str.find(get_start_date())
  
  # truncate the data to just the data from the start date onwards
  content_str = content_str[start_i:]
  
  # parse the content into a list of lists
  content_file = StringIO.StringIO(content_str)
  reader = csv.reader(content_file, delimiter=',')

  data_t = [list(i) for i in zip(*reader)]
  
  # take the date column and start the output data table
  output_t = data_t[0:1]
  
  # remove the date column from the data to be normalized
  data_t = data_t[1:]

  # store the means and standard deviations for each column
  means = []
  stdevs = []

  # normalize each column
  for col in data_t:
    m = mean(col)
    s = stdev(col, m)
    means.append(m)
    stdevs.append(s)
    output_t.append(normalize(col, m, s))

  # transpose the output_t to get it back into row format
  output = [list(i) for i in zip(*output_t)]

  # open output file and get a csv writer
  outfile = open(file_name, "w")
  writer = csv.writer(outfile)

  # write header and data
  header = ["Date", "Open", "High", "Low", "Close", "Volume", "Ex-Dividend", "Split Ratio", "Adj. Open", "Adj. High", "Adj. Low", "Adj. Close", "Adj. Volume"]
  writer.writerow(header)

  [writer.writerow(x) for x in output]

  # close file
  outfile.close()

  




