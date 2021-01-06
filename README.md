# snapshotalyzer
Demo Project to manege AWS EC2 instance snapshots 

##ABOUT 

This project is a demo, and uses boto3 to manage AWS EC2 instace snapshots.

## Configuring 

shotty uses the configuration file created by the AWS Cli. e.g.

`aws configure --profile shotty`

##Running 

`pipenv run python shotty/shotty.py <command> <--project=PROJECT>`

*command* is list, stop or start 
*project* is optional 

