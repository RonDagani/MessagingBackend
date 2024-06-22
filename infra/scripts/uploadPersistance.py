import pulumi
import pulumi_aws as aws
import pulumi_mongodbatlas as mongodbatlas

# Configuration
config = pulumi.Config()
atlas_project_id = config.require('atlasProjectId')
atlas_api_key_public = config.require('atlasApiKeyPublic')
atlas_api_key_private = config.require('atlasApiKeyPrivate')
mongodb_admin_username = config.require('mongodbAdminUsername')
mongodb_admin_password = config.require('mongodbAdminPass')
region = aws.config.region or 'us-east-1'


def modify_connection_string(connection_string, username, password):
    parts = connection_string.split("://")
    return f"{parts[0]}://{username}:{password}@{parts[1]}"

def get_endpoint(nodes):
    if nodes and len(nodes) > 0 and "address" in nodes[0]:
        # Combine address and port to form the complete endpoint
        address = nodes[0]["address"]
        port = nodes[0]["port"]
        return f"{address}:{port}"
    return "Endpoint not available"

# Fetch the VPC and Subnets
async def get_vpc_and_subnets():
    vpc = await aws.ec2.get_vpc(default=True)
    subnets = await aws.ec2.get_subnets(filters=[{'name': 'vpc-id', 'values': [vpc.id]}])
    return vpc, subnets

def split_endpoint(endpoint):
    host, port = endpoint.split(':')
    return {
        'host': host,
        'port': port
    }

def upload():

    # MongoDB Atlas 
    mongodbatlas_provider = mongodbatlas.Provider("atlas", public_key=atlas_api_key_public, private_key=atlas_api_key_private)
    cluster = mongodbatlas.Cluster("MessagingDB",
        project_id=atlas_project_id,
        provider_name="TENANT",
        backing_provider_name="AWS",
        provider_region_name="US_EAST_1",
        provider_instance_size_name="M0",
        opts=pulumi.ResourceOptions(provider=mongodbatlas_provider)
    )
    pulumi.export('cluster_name', cluster.name)
    pulumi.export('connection_string', cluster.connection_strings)
    mongodb_connection_string_modified = cluster.connection_strings.apply(
        lambda connections: modify_connection_string(connections[0]['standard_srv'], mongodb_admin_username, mongodb_admin_password)
    )

    #Redis

    # Use pulumi.Output.from_input to handle the async function
    vpc_and_subnets_output = pulumi.Output.from_input(get_vpc_and_subnets())
    vpc = vpc_and_subnets_output.apply(lambda result: result[0])
    subnet_ids = vpc_and_subnets_output.apply(lambda result: result[1].ids)

    # Create a Redis subnet group using the subnet IDs
    subnet_group = aws.elasticache.SubnetGroup(
        "redisSubnetGroup",
        description="Subnet group for Redis cache",
        subnet_ids=subnet_ids  # Use the subnet IDs obtained asynchronously
    )

    redis_security_group = aws.ec2.SecurityGroup(
        "redisSecurityGroup",
        description="Allow inbound traffic to Redis",
        vpc_id=vpc.id,
        ingress=[
            {"protocol": "tcp", "from_port": 6379, "to_port": 6379, "cidr_blocks": [vpc.cidr_block]}
        ]
    )

    # Create a security group in the VPC
    # security_group = aws.ec2.SecurityGroup(
    #     "redisSecurityGroup",
    #     description="Security group for Redis",
    #     vpc_id=vpc_id,
    #     ingress=[aws.ec2.SecurityGroupIngressArgs(protocol="tcp", from_port=6379, to_port=6379, cidr_blocks=["0.0.0.0/0"])],
    #     egress=[aws.ec2.SecurityGroupEgressArgs(protocol="-1", from_port=0, to_port=0, cidr_blocks=["0.0.0.0/0"])],
    # )

    # Create a parameter group compatible with Redis 6.x
    parameter_group = aws.elasticache.ParameterGroup(
        "redisParameterGroup",
        family="redis6.x",
        description="Parameter group for Redis 6.x"
    )

    # Create the Redis cluster
    redis_cluster = aws.elasticache.Cluster(
        "redisCluster",
        engine="redis",
        engine_version="6.x",
        node_type="cache.t2.micro",
        num_cache_nodes=1,
        parameter_group_name=parameter_group.name,
        subnet_group_name=subnet_group.name,
        security_group_ids=[redis_security_group.id]
    )

    # Applying the corrected function to get the Redis endpoint
    redis_endpoint = redis_cluster.cache_nodes.apply(get_endpoint)
    pulumi.export('redis_endpoint', redis_endpoint)
    redis_endpoint_parts = redis_endpoint.apply(split_endpoint)
    redis_host = redis_endpoint_parts.apply(lambda parts: parts['host'])
    redis_port = redis_endpoint_parts.apply(lambda parts: parts['port'])

    return redis_host, redis_port, mongodb_connection_string_modified
