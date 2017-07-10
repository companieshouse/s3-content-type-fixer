# S3 Content Type Fixer #

This script will scan an S3 bucket to find files with bad content-types and
fix them.

To run the script, first install the dependencies:

    pip install -r requirements.txt

Then run the fixer:

    python s3_content_type_fixer.py --access-key <your AWS access key> --secret-key <your AWS secret key> --bucket <your S3 bucket> --region <region name where the bucket is located>

## Special authentication considerations

Certain regions (e.g.: `eu-central-1`) require requests to be signed with a specific algorithm and will complain with a 400 error and a message along the lines of “The authorization mechanism you have provided is not supported. Please use AWS4-HMAC-SHA256.”

In order to avoid this problem, you _must_ specify the region name when calling the script:

    python s3_content_type_fixer.py --access-key <your AWS access key> --secret-key <your AWS secret key> --bucket mybucket --region eu-central-1
