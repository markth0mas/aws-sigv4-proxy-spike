import os

import aws_cdk as cdk
from app_tier import AppTierStack
from network import NetworkStack

env = cdk.Environment(account=os.environ['CDK_DEFAULT_ACCOUNT'], region=os.environ['CDK_DEFAULT_REGION'])
app = cdk.App(outdir='cdk.out')

network = NetworkStack(app, 'network', env=env)
AppTierStack(app, 'app', vpc=network.vpc, env=env)

app.synth()
