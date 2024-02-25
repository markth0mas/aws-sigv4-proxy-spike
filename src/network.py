import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_ec2 as ec2)


class NetworkStack(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)

        self.vpc = ec2.Vpc(self, 'vpc',
                           max_azs=1,
                           nat_gateway_provider=ec2.NatProvider.instance(instance_type=ec2.InstanceType("t2.nano"))
                           )
