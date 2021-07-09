#Python for creating an ec2 instance and installing NGINX
#
import boto3

try:
  ec2 = boto3.client('ec2')

except Exception as e: print(e)

#This function will describe all the instances
#with their current state
response = ec2.describe_instances()
print(response)