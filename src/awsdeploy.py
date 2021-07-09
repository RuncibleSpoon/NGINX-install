#Python for creating an ec2 instance and installing NGINX
#
import boto3
import argparse
import os
import time
import sys
from botocore.config import Config


def main(vpcid,region,name,keypair):
    print("vpc:", vpcid, " Region: ", region, " name: ", name, " keypair: ", keypair)



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
      print("VPC not found in ", region, " : ", e)
      sys.exit(1)
    try:
       keyPair = ec2Res.KeyPair(keypair)
       keyPair.load()
       print(" Keypair id is ", keyPair.key_pair_id)
    except Exception as e:
      print("Keypair not found: ", e)
      sys.exit(1)

   # quick check to see what is there

    response = ec2.describe_instances(
      Filters=[
        {
         'Name': 'vpc-id',
         'Values': [vpcid]
        }
      ]
    )
    print(response)




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