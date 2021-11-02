# S3 Content Type Fixer #

This script will upload files to S3 with Python3 keeping the original folder structure with correct MIME type

To run the script, first install the dependencies:

    pip install -r requirements.txt

Then run the fixer:

    python3 s3_content_type_fixer.py --region_name <your AWS region> --access_key <your AWS access key> --secret_key <your AWS secret key> --bucket_name <your S3 bucket> --local_path <your local path>
