import boto3
import argparse
import os
import mimetypes

mimetypes.add_type('text/html', '.shtml')
mimetypes.add_type('application/xml', '.xsd')
      
def upload_files(region, access_key, secret_key, bucket, path):
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket)

    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            file_mime = mimetypes.guess_type(file)[0] or 'binary/octet-stream'
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=full_path[len(path)+1:], Body=data, ContentType=file_mime)

def main():
 parser = argparse.ArgumentParser(description="Fixes the content-type of assets on S3")

 parser.add_argument("--region-name", "-r", type=str, default="eu-west-2", required=True, help="The region name")
 parser.add_argument("--access-key", "-a", type=str, required=True, help="The AWS access key")
 parser.add_argument("--secret-key", "-s", type=str, required=True, help="The AWS secret key")
 parser.add_argument("--bucket-name", "-b", type=str, required=True, help="The S3 bucket to check")
 parser.add_argument("--local-path", "-p", type=str, required=True, help="The local path to scan for files to upload")
  
 args = parser.parse_args()
 upload_files(args.region-name, args.access-key, args.secret-key, args.bucket-name, args.local-path)

if __name__ == "__main__":
  main() 