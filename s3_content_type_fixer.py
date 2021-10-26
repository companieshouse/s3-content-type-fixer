import requests
import boto3
import argparse
import multiprocessing
import sys
import mimetypes

mimetypes.add_type('text/html', '.shtml')
mimetypes.add_type('application/xml', '.xsd')

BLOCK_TIME = 60 * 60

def find_matching_files(bucket, prefixes):
    """
    Returns a set of files in a given S3 bucket that match the specificed file
    path prefixes
    """
    return set(key for prefix in prefixes for key in bucket.objects.filter(Prefix=prefix))

def get_bucket(region, access_key, secret_key, bucket):
    """Gets an S3 bucket"""
    session = boto3.Session(
      region_name=region,
      aws_access_key_id=access_key,
      aws_secret_access_key=secret_key,
    )

    s3 = session.resource('s3')
    return s3.Bucket(bucket)

def check_headers(bucket, queue, verbose, dryrun):
    """
    Callback used by sub-processes to check the headers of candidate files in
    a multiprocessing queue
    """

    while True:
        try:
            key_name = queue.get(BLOCK_TIME)
        except:
            break

        if key_name == None:
            break

        key = bucket.lookup(key_name)

        if not key:
            print("%s: Could not lookup" % key.name, file=sys.stderr)
            continue

        content_type = key.content_type
        expected_content_type, _ = mimetypes.guess_type(key.name, strict=False)

        if not expected_content_type:
            print("%s: Could not guess content type" % key.name, file=sys.stderr)
            continue

        if content_type == expected_content_type:
            if verbose:
                print("%s: Matches expected content type" % key.name)
        else:
            print("%s: Current content type (%s) does not match expected (%s); fixing" % (key.name, content_type, expected_content_type))
            if not dryrun:
                metadata = {"Content-Type": expected_content_type}

                if key.content_disposition:
                    metadata["Content-Disposition"] = key.content_disposition

                key.copy(key.bucket, key.name, preserve_acl=True, metadata=metadata)

def main():
    parser = argparse.ArgumentParser(description="Fixes the content-type of assets on S3")

    parser.add_argument("--region", "-r", type=str, default="eu-west-2", required=True, help="The region name")
    parser.add_argument("--access-key", "-a", type=str, required=True, help="The AWS access key")
    parser.add_argument("--secret-key", "-s", type=str, required=True, help="The AWS secret key")
    parser.add_argument("--bucket", "-b", type=str, required=True, help="The S3 bucket to check")
    parser.add_argument("--prefixes", "-p", type=str, default=[""], required=False, nargs="*", help="File path prefixes to check")
    parser.add_argument("--workers", "-w", type=int, default=4, required=False, help="The number of workers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--dryrun", "-d", action="store_true", default=False, required=False,help="Add this for a dry run (don't change any file)")

    args = parser.parse_args()
    queue = multiprocessing.Queue()
    processes = []
    bucket = get_bucket(args.region, args.access_key, args.secret_key, args.bucket)

    # Start the workers
    for _ in range(args.workers):
        p = multiprocessing.Process(target=check_headers, args=(bucket, queue, args.verbose, args.dryrun))
        p.start()
        processes.append(p)
    
    # Add the items to the queue
    for key in find_matching_files(bucket, args.prefixes):
        queue.put(key)

    # Add None's to the end of the queue, which acts as a signal for the
    # proceses to finish
    for _ in range(args.workers):
        queue.put(None)

    for p in processes:
        # Wait for the processes to finish
        try:
            p.join()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()