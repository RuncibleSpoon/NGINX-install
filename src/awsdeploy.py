#Python for creating an ec2 instance and installing NGINX
#
import boto3
import argparse
import os
import time



def main(vpcid,region,name):
    print("vpc:", vpcid, " Region: ", region, " name: ", name)

    try:
      ec2 = boto3.client('ec2')
    except Exception as e: print(e)

    try:
      ec2Res = boto3.resource('ec2')
    except Exception as e: print(e)

     try:
       vpc = ec2res.Vpc(vpcid)
     except Exception as e: print("VPC not found: ", e)



    response = ec2.describe_instances()
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

    args = parser.parse_args()

    main(args.vpcid, args.region, args.name)