import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (aws_ecs as ecs, aws_ec2 as ec2, aws_opensearchservice as oss, aws_iam as iam)


class AppTierStack(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, vpc: ec2.Vpc, **kwargs):
        super().__init__(scope, id_, **kwargs)

        search_security_group = ec2.SecurityGroup(self, 'open-search-security-group', vpc=vpc)
        # Allow inbounds

        search_domain = oss.Domain(self, 'open-search-service',
                                   version=oss.EngineVersion.OPENSEARCH_2_11,
                                   domain_name='test-domain',
                                   vpc=vpc,
                                   security_groups=[search_security_group],
                                   removal_policy=cdk.RemovalPolicy.DESTROY,
                                   capacity=oss.CapacityConfig(
                                       data_nodes=1,
                                       data_node_instance_type='t3.small.search',
                                   ),
                                   ebs=oss.EbsOptions(
                                       enabled=True,
                                       volume_size=10,
                                       volume_type=ec2.EbsDeviceVolumeType.GP2,
                                   )
                                   )

        search_domain.add_access_policies(iam.PolicyStatement(
            principals=[iam.AnyPrincipal()],
            actions=['es:ESHttp*'],
            resources=[search_domain.domain_arn + '/*']
        ))

        cdk.CfnOutput(self, 'search-domain-host', value=search_domain.domain_endpoint)

        bastion_security_group = ec2.SecurityGroup(self, 'bastion-security-group',
                                                   vpc=vpc,
                                                   allow_all_outbound=True
                                                   )

        search_security_group.add_ingress_rule(bastion_security_group, ec2.Port.tcp(443))

        bastion = ec2.BastionHostLinux(self, 'bastion',
                                       vpc=vpc,
                                       security_group=bastion_security_group,
                                       machine_image=ec2.MachineImage.latest_amazon_linux2023()
                                       )

        compute_cluster = ecs.Cluster(self, 'ecs-cluster',
                                      vpc=vpc,
                                      enable_fargate_capacity_providers=True
                                      )
        proxy_task_definition = ecs.FargateTaskDefinition(self, 'proxy-task-def',
                                                          memory_limit_mib=512,
                                                          cpu=256)
        proxy_task_definition.add_container('proxy-container',
                                            image=ecs.ContainerImage.from_registry(
                                                'public.ecr.aws/aws-observability/aws-sigv4-proxy:latest'),
                                            port_mappings=[ecs.PortMapping(container_port=8080, host_port=8080)],
                                            command=['--verbose', '--region=eu-west-2', '--name=es', '--host=' + search_domain.domain_endpoint],
                                            logging=ecs.LogDriver.aws_logs(stream_prefix='aws-sigv4-proxy')
                                            )
        proxy_security_group = ec2.SecurityGroup(self, 'proxy-security-group',
                                                 vpc=vpc,
                                                 allow_all_outbound=True
                                                 )

        proxy_security_group.add_ingress_rule(bastion_security_group, ec2.Port.tcp(8080))
        search_security_group.add_ingress_rule(proxy_security_group, ec2.Port.tcp(443))

        proxy_service = ecs.FargateService(self, 'proxy-service',
                                           cluster=compute_cluster,
                                           task_definition=proxy_task_definition,
                                           security_groups=[proxy_security_group]
                                           )
