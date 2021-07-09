#Python for creating an ec2 instance and installing NGINX
#
import boto3
import argparse
import os
import time
import sys



def main(vpcid,region,name,keypair):
    print("vpc:", vpcid, " Region: ", region, " name: ", name, " keypair: ", keypair)

    try:
      ec2 = boto3.client('ec2')
    except Exception as e: print(e)

    try:
      ec2Res = boto3.resource('ec2')

    except Exception as e: print(e)

    try:
      Vpc = ec2Res.Vpc(vpcid)
    except Exception as e: print("VPC not found: ", e)

    try:
       keyPair = ec2Res.KeyPair(keypair)
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
    parser.add_argument('vpcid', help='Your AWS VPC')
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS Region to deploy to.')
    parser.add_argument(
        '--name', default='demo-instance', help='New instance name.')
    parser.add_argument(
            '--keypair', help='aws keypair name to use')

    args = parser.parse_args()

    main(args.vpcid, args.region, args.name, args.keypair)