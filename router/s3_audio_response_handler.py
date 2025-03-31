import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class S3AudioResponseHandler:
    def __init__(self):
        # Initialize any necessary attributes here
        pass

    def upload_audio_response_to_s3(self, file_name: str, region: str, bucket: str, object_name: str = None):
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Create an S3 client
        s3_client = boto3.client('s3')

        try:
            # Upload the file
            s3_client.upload_file(file_name, bucket, object_name)
            print(f"File {file_name} uploaded to {bucket}/{object_name}")

            # Construct the full URL of the uploaded file
            file_url = f"https://{bucket}.s3.{region}.amazonaws.com/{object_name}"
            return file_url  # Return the full URL
        except FileNotFoundError:
            print(f"The file {file_name} was not found")
        except NoCredentialsError:
            print("Credentials not available")
        except ClientError as e:
            print(f"An error occurred: {e}")