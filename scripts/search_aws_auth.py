#!/usr/bin/python3
from opensearchpy import OpenSearch, Urllib3AWSV4SignerAuth, Urllib3HttpConnection
import boto3

host = 'vpc-test-domain-356me6iwld5infzdlw4ixskf6y.eu-west-2.es.amazonaws.com'
credentials = boto3.Session().get_credentials()
auth = Urllib3AWSV4SignerAuth(credentials, 'eu-west-2', 'es')

client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    connection_class = Urllib3HttpConnection,
    use_ssl = True
)

info = client.info()
print(info)