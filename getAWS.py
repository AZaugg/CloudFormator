#!/usr/bin/python
#
# Written by: Andreas Zaugg <andy.zaugg at dot com>
#
# Interface with AWS to retrieve dynamic content used for cloud formator
# In summary it will retrieve the following
#    - Lists of AMIs
#    - Lists of ssh keys
#    - Lists of  Regions
#    - Lists of  DB engines supported by RDS
#
# This is far from complete:
# TODO: List AMIs based on region
# TODO: List avaialble subnets based on Availability zones
# TODO: ...
#



import os, sys, subprocess
# Module toget anything amazoniny



#----------------------------------------------------------------------
def getAMIs():
	''' Retrive a list of all AMIs owned my account that are hosted in AWS
	'''
	aws_query = ["aws", "ec2", "describe-images", "--owner", "self", "--output", "text", "--query", "Images[].ImageId"]
	amiImageList = subprocess.check_output( aws_query )
	amiImageList = amiImageList.split()
	f = open("aws_cache/ami.list", "w")
	for ami in amiImageList:
		f.writelines(ami + "\n")
	f.close()
#----------------------------------------------------------------------
def getSSHKeys():
	''' Retrive a list of SSH keys from AWS
	'''
	aws_query = ["aws", "ec2", "describe-key-pairs", "--output", "text", "--query", "KeyPairs[].KeyName"]
	keys = subprocess.check_output( aws_query )
	keys = keys.split()
	f = open("aws_cache/ssh-keys.list", "w")
	for key in keys:
		f.writelines(key + "\n")
	f.close()
#----------------------------------------------------------------------
def getRegions():
	'''Retrieve a list of regions that AWS supports
	'''
	aws_query = ["aws", "ec2", "describe-regions", "--output", "text", "--query", "Regions[].RegionName"]
	regions = subprocess.check_output(aws_query)
	regions = regions.split()
	f = open("aws_cache/aws-regions.list", "w")
	for region in regions:
		f.write(region + "\n")	
	f.close()
#----------------------------------------------------------------------
def getDBEngines():
	'''Retrieve a list of available DB engines
	'''
	aws_query = ["aws", "rds", "describe-db-engine-versions", "--output", "text", "--query", " DBEngineVersions[].Engine"]
	DBEngines = subprocess.check_output(aws_query)
	# Grab a list of all DB engine and remove duplicates
	DBEngines = set(DBEngines.split())

	f = open("aws_cache/aws-DBEngines.list", "w")
	for engine in DBEngines:
		f.write(engine + "\n")	
	f.close()

#----------------------------------------------------------------------
def main():
	#getAMIs()
	#getSSHKeys()
	#getRegions()
	getDBEngines()
#----------------------------------------------------------------------
if __name__ == "__main__":
	main()
