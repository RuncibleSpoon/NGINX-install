# A Simple Python-Based Wrapper to Create an  NGINX Webserver via AWS Cloudformation 

## Introduction

This is an example script that: 

* Checks your input values - including if the VPC and keypair exist, and that you have selected a supported region
* Builds an Amazon Linux ec2 instance in an existing VPC
* Installs NGINX OSS
* Installs content from this repo 
* Starts NGINX
* Outputs the public IP address of the instance

## Prerequisites 

### System

1. Python 3.6 or above (tested on 3.6.9)
2. Pip
3. venv (not explicitly necessary, but recommended)
4. The [AWS cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-install) utility 

### AWS Environment

1. Supported regions  us-west-2 and us-east-2
2. An existing VPC in a supported region with internet gateway and routing configured
3. An AWS key pair for SSH access to the instance
4. An AWS Secret and Key for api access attached to a role with permissions to create
    1. CloudFormation templates 
   2. ec2 instances
    3. S3 storage buckets 
    
## Installation 

1. Clone the repo

```shell
git clone https://github.com/RuncibleSpoon/NGINX-install 
```

2. Create a virtual environment to mange your python dependencies. See [here](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) 
for more information on Python venv
```shell
python3 -m venv env
source env/bin/activate
```
3. Use pip to install the required packages
```shell
cd src
pip install -r requirements.txt
```

4. If not already installed and configured, [install](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-install)
the AWS CLI tool and run ```aws configure```, providing your AWS key and secret
   
5. If you want to edit the test page displayed, edit contents/index.html 

## Script Operation 

The script takes parameters and the files in the ```content``` directory and:

1. Verifies objects like region, VPC id, and keypair are correct  
2. Creates an S3 bucket and uploads a simple html file and CloudFormation template 
3. Builds a stack based on the CloudFormation template and user supplied parameters
4. Waits for the stack creation and NGINX software install to complete   
4. Empties and deletes the created S3 bucket




### Parameters

The script takes the following parameters:

```shell

usage: cftdeploy.py [-h] [--vpcid VPCID] [--region {us-east-2,us-west-2}]
                    [--name NAME] [--keypair KEYPAIR]

optional arguments:
  -h, --help                             show this help message and exit
  --vpcid VPCID                          Your AWS VPC - must exist.
  --region {us-east-2,us-west-2}         AWS Region to deploy to - choose us-east-2 or us- west-2.
  --name NAME                            New instance name.
  --keypair KEYPAIR                      AWS keypair name to use.

```
### Running the Script 

Example:

``` cftdeploy.py --name foo --vpcid vpc-47f9762c --keypair nginxkp --region us-east-2 ```

The The script outputs the public IP address of the created ec2 instance. If your VPC and networking is so configured, 
you will be able to go that page in a browser.



### To Do

* Propper logging using the Python logging module
* Replace the index.html install with a zip/unzip of a file archive
* Add functionality to replace the nginx.conf file 
* Additional region support
















