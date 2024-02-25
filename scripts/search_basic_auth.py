#!/usr/bin/python3
from opensearchpy import OpenSearch

host = 'vpc-test-domain-356me6iwld5infzdlw4ixskf6y.eu-west-2.es.amazonaws.com'
auth = ('admin', 'admin')

client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True
)

info = client.info()
print(info)