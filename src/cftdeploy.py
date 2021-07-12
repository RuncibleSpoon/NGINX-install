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
stackname = "NGINXStack" + sessionId

def main(vpcid,region,name,keypair):
   # ami=image[region]
    print('Starting Deployment' )
    print('####################')
    print('Supplied arguments')
    print("vpc:", vpcid, " Region: ", region, " name: ", name, " keypair: ", keypair)
    print('Generated unique id: ', sessionId)
    s3BucketName = 's3b' + sessionId
    #print(s3BucketName)

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
       #print("Keypair id is ", keyPair.key_pair_id)
    except Exception as e:
      print("Keypair not found: ", e)
      sys.exit(1)

    try:
      subnets = ec2Res.subnets.filter(
          Filters=[{"Name": "vpc-id", "Values": [vpcid]}]
      )
      subnet_ids = [sn.id for sn in subnets]
      #print(subnet_ids)
      subnetid=subnet_ids[0]
      #print('Subnet ' , subnetid , ' selected' )
      #availabilityZone = ec2Res.subnets()
    except Exception as e:
      print("Subnets in VPC ",vpcid, " not found: " , e)
      sys.exit(1)

    ### Setup an S3 bucket for our CFT and config files to live in
    try:
        # create S3 client connection
        s3 = boto3.client("s3")
        s3Bucket = s3.create_bucket(Bucket=s3BucketName, CreateBucketConfiguration={ 'LocationConstraint': region })
        # Create S3 resource connection
        s3res = boto3.resource("s3")
        # retrieve bucket object - could this be more elegant?
        bucket = s3res.Bucket(s3BucketName)
        contentUrl = "https://" + s3BucketName + ".s3." + region + ".amazonaws.com/index.html"
        configUrl = "https://" + s3BucketName + ".s3." + region + ".amazonaws.com/nginx.conf"
        templateUrl = "https://s3.amazonaws.com/" + s3BucketName + "/nginx.cft"
        print(templateUrl, "  ", contentUrl)
        print('S3bucket Created')




    except Exception as e:
                 print("Bucket not created: ", e)
                 sys.exit(1)

    ### Add template and nginx source files to bucket

    ### walk the content directory to build a file list
    print('Building upload file list')
    arr=os.listdir('./content')
    #print(arr, "\n")
    # use the file list to upload to the s3 bucket
    # use the bucket resource object not the client conneciton
    try:
        for file_name in arr:
          print('uploading ',file_name)
          # should really paramerize the path
          file_path = './content/' + file_name
          bucket.upload_file(
            Filename=file_path,
            Key=file_name,
            ExtraArgs={'ACL': 'public-read'}
          )
    except Exception as e:
        print("file upload failure: ", e)
        deleteBucket(s3BucketName)
        sys.exit(1)

   ##### Files are uploaded so lets try to create a stack from the template
   ### need to add a stack wait thing
    try:
      print('Creating stack')
      cftres = boto3.resource('cloudformation',config=my_config)
      cftclient = boto3.client('cloudformation',config=my_config)
      response = cftclient.create_stack(
        StackName=stackname,
        TemplateURL=templateUrl,
        Parameters=[
           {
                       'ParameterKey': 'VpcId',
                       'ParameterValue': vpcid
           },
           {
                       'ParameterKey': 'SubnetID',
                       'ParameterValue': subnetid
           },
           {
                        'ParameterKey': 'KeyName',
                        'ParameterValue': keypair
           },
           {
                        'ParameterKey': 'configUrl',
                        'ParameterValue': configUrl
           },
           {
                        'ParameterKey': 'contentUrl',
                        'ParameterValue': contentUrl

           }
        ]
      )
     # print(response)
    except Exception as e:
      print("could not create stack ", e)
      deleteBucket(s3BucketName)
      sys.exit(1)

    print('Please Wait while the Stack Completes')
    try:
      waiter = cftclient.get_waiter('stack_create_complete')
      waiter.wait(
        StackName=stackname,
        WaiterConfig={
                     'Delay': 30,
                      'MaxAttempts': 10
                   }
      )
    except Exception as e:
                 print("Could not create waiter", e)
                 deleteBucket(s3BucketName)
                 sys.exit(1)

    ### lets see if we can get the status of the stack

    stack = cftres.Stack(stackname)

    if stack.stack_status == 'CREATE_COMPLETE':
      print('Congratulations your NGIX instance has been deployed')
      print(stack.outputs)
    else:
      print('stack status failed with ', stack.stack_status)


  ### Delete the S3 Bucket
      deleteBucket(s3BucketName)

### Function to empty and delete the bucket

def  deleteBucket(s3BucketName):

  try:
    s3 = boto3.resource("s3")
    #bucket = s3Bucket
    bucket = s3.Bucket(s3BucketName)
    #print(bucket)
    # suggested by Jordon Philips
    res = bucket.objects.all().delete()
    res= s3.Bucket(bucket.name).delete()
    print('Bucket ', s3BucketName, ' deleted')
  except Exception as e:
    print("Bucket " , S3BucketName, " not deleted: ", e)
    sys.exit(1)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
         '--vpcid', help='Your AWS VPC - must exist')
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