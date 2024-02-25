!/usr/bin/python3
from opensearchpy import OpenSearch

proxy = '10.0.162.208'
host = 'vpc-test-domain-356me6iwld5infzdlw4ixskf6y.eu-west-2.es.amazonaws.com'
auth = ('admin', 'admin')

client = OpenSearch(
    hosts = [{'host': proxy, 'port': 8080}],
    http_auth = auth,
    use_ssl = False
)

info = client.info()
print(info)