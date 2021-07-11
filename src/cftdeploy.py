#Python for creating an ec2 instance and installing NGINX
#
import boto3
import argparse
import os
import time
import sys
import uuid
from botocore.config import Config

# AWS image to use
# this could be replaced with AWS systems manager

#image = {'us-west-2': 'ami-01773ce53581acf22', 'us-east-2': 'ami-0b29b6e62f2343b46' }

# other default things that could be changed

security_group_name = "WebServer2"
security_group_description = "Inbound 443 and 80"
sessionId = str(uuid.uuid1().int)


def main(vpcid,region,name,keypair):
   # ami=image[region]
    print("vpc:", vpcid, " Region: ", region, " name: ", name, " keypair: ", keypair)
    print(sessionId)
    s3Bucket = 's3b' + sessionId
    print(s3Bucket)

    my_config = Config(
        region_name = region,
        signature_version = 'v4',
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )




  # basic setup check

    try:
      ec2 = boto3.client('ec2',config=my_config)
    except Exception as e:
      print("Unable to create ec2 client: ",e)
      sys.exit(1)
    try:
      ec2Res = boto3.resource('ec2',config=my_config)
    except Exception as e:
      print("Unable to create ec2 resource:", e)
      sys.exit(1)
    try:
      Vpc = ec2Res.Vpc(vpcid)
      Vpc.load()
    except Exception as e:
      print("VPC error ", vpcid , " not found in ", region, " : ", e)
      sys.exit(1)
    try:
       keyPair = ec2Res.KeyPair(keypair)
       keyPair.load()
       print(" Keypair id is ", keyPair.key_pair_id)
    except Exception as e:
      print("Keypair not found: ", e)
      sys.exit(1)

    ### Setup an S3 bucket for our CFT and config files to live in
    try:
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=s3Bucket, CreateBucketConfiguration={ 'LocationConstraint': region })
        print('S3bucket Created')
    except Exception as e:
                 print("Bucket not created: ", e)
                 sys.exit(1)



    ### Delete the S3 Bucket

    deleteBucket(s3Bucket)

### Function to empty and delete the bucket

def  deleteBucket(s3Bucket):

  try:
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3Bucket)

    print(bucket)
    # suggested by Jordon Philips
    res = bucket.objects.all().delete()
    print(res)
    res= s3.Bucket(bucket.name).delete()
    #print(res)
  except Exception as e:
                   print("Bucket not deleted: ", e)
                   sys.exit(1)



#     SecurityGroup=setup_security_group(security_group_name, security_group_description, ec2, ec2Res)
#
#     try:
#       instances = ec2.run_instances(
#               ImageId=ami,
#               MinCount=1,
#               MaxCount=1,
#               InstanceType="t4g.nano",
#               KeyName=keyPair.name
#       )
#     except Exception as e:
#
#    # quick check to see what is there
#
#     response = ec2.describe_instances(
#       Filters=[
#         {
#          'Name': 'vpc-id',
#          'Values': [vpcid]
#         }
#       ]
#     )
#     #print(response)
#
#
#     print(SecurityGroup)

# ### Stole this bit from
# ### https://docs.aws.amazon.com/code-samples/latest/catalog/python-ec2-ec2_basics-ec2_setup.py.html
#
# def setup_security_group(group_name, group_description, ec2, ec2Res):
#     """
#     Creates a security group in the default virtual private cloud (VPC) of the
#     current account, then adds rules to the security group to allow access to
#     HTTP, HTTPS and, optionally, SSH.
#
#     :param group_name: The name of the security group to create.
#     :param group_description: The description of the security group to create.
#     :param ssh_ingress_ip: The IP address that is granted inbound access to connect
#                            to port 22 over TCP, used for SSH.
#     :return: The newly created security group.
#     """
#     ## removed the code to find the default VPC since I want it specified
#
#     try:
#         security_group = ec2.create_security_group(
#             GroupName=group_name, Description=group_description)
#         sgID=security_group['GroupId']
# #         logger.info(
#         #print("Created security group ", security_group, "group id: ", sgID)
#     except  Exception as e:
# #         logger.exception("Couldn't create security group %s.", group_name)
#           raise
#
#     try:
#         ip_permissions = [{
#             # HTTP ingress open to anyone
#             'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
#             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
#         }, {
#             # HTTPS ingress open to anyone
#             'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443,
#             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
#         }]
#         ## removed ssh - not cool
#         print("secuirty group id: ", sgID)
#         sec_group=ec2Res.SecurityGroup(sgID)
#         print("foo: " ,sec_group.group_id)
#         sec_group.authorize_ingress(IpPermissions=ip_permissions)
#         #print("Set inbound rules for %s to allow all inbound HTTP and HTTPS ")
#
#     except Exception as e:
#         print("Couldnt authorize inbound rules for %s.", group_name, "  :", e)
#
#     else:
#         return security_group


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('vpcid', help='Your AWS VPC - must exist')
    parser.add_argument(
        '--region',
        default='us-east-2',
        help='AWS Region to deploy to - choose us-east-2 or us-west-2.',
        choices=['us-east-2', 'us-west-2'])
    parser.add_argument(
        '--name', default='demo-instance', help='New instance name.')
    parser.add_argument(
            '--keypair', help='aws keypair name to use')

    args = parser.parse_args()

    main(args.vpcid, args.region, args.name, args.keypair)