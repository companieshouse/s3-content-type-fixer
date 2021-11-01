import boto3
import os
import mimetypes

mimetypes.add_type('text/html', '.shtml')
mimetypes.add_type('application/xml', '.xsd')

def upload_files(path):
    session = boto3.Session(
        aws_access_key_id='access-key',
        aws_secret_access_key='secret-key',
        region_name='region'
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket('bucket')

    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            file_mime = mimetypes.guess_type(file)[0] or 'binary/octet-stream'
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=full_path[len(path)+1:], Body=data, ContentType=file_mime)

if __name__ == "__main__":
    upload_files('extract')