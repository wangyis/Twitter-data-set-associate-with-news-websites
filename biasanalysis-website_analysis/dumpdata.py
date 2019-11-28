from google.cloud import bigquery
from google.cloud import storage

# run this in sqlite3 to convert to csv and save to source_file_name
# $ sqlite3 extraction_db.sqlite
# sqlite3> .headers on
# sqlite3> .mode csv
# sqlite3> .output article_dump.csv
# sqlite3> SELECT * FROM article_data;
# sqlite3> .quit

# GOOGLE CLOUD FUNCTIONS - currently not using, but could in the future
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


def main():
    # name of bucket is news_website_data
    source_file_name = "article_dump.csv"
    destination_blob_name = "article_dump.csv"
    upload_blob("news_website_data", source_file_name, destination_blob_name)

# so far, this doesn't work yet. In the future with Google Cloud debugging, this code could be used.
# main()