#!/usr/bin/python

#
# Written by: Andreas Zaugg <andy.zaugg at dot com>
#
# Flask runtime envinomrent, used to launch cloud formator
#
# This is far from complete:
# TODO: Remove all hard coded values
# TODO: Clean up code
# TODO: Argument/value validation
# TODO: Push data to AWS cloud formatiions directly
# TODO: Set mime type for file download of complete CF script
# TODO: Support for ELB
# TODO: Support EBS
# TODO: Installatuion fo extra packages
# TODO: Add all provision steps


import flask
import getAWS
from flask import request,redirect,url_for
from troposphere import Base64, FindInMap, GetAtt, GetAZs, Join, Output
from troposphere import Parameter, Ref, Template
import troposphere.ec2 as ec2
import troposphere.rds as rds

app = flask.Flask(__name__)
#------------------------------------------------------
@app.route("/runit", methods=["POST"])
def runit():
	pass
	query = ["aws", "cloudformation", "create-stack", "--stack-name"]
#------------------------------------------------------
@app.route("/display", methods=["GET"])
def display():
	if not request.method == "GET":
		return flask.render_template("index.html")

	# lets get the data from the form/Get
	selectedEc2Count = int(request.args.get("selectedEc2Count"))
	selectedRdsCount = int(request.args.get("selectedRdsCount"))
	selectedKey = request.args.get("Key")
	selectedRegion = request.args.get("Region")

	# Need to move as you may want to deploy to different availabiulity zones
	subnets = request.args.get("Subnets") 

	if selectedEc2Count:
		selectedEc2Count = range(0,selectedEc2Count)
	if selectedRdsCount:
		selectedRdsCount = range(0,selectedRdsCount)


	genericComputeConfig = {}
	genericRDSConfig = {}
	output = ""
	t = Template()

	if selectedEc2Count:
		for node in selectedEc2Count:
			argName = "name-%s" % str(node)
			argAmi = "ami-%s" % str(node)
			argSize = "size-%s" % str(node)

			ami = request.args.get(argAmi)	
			name = request.args.get(argName)	
			size = request.args.get(argSize)	
			genericComputeConfig[name] = (ami, size)
			
			# Populate troposphere objects with form data
			instance = ec2.Instance(name)
			instance.ImageId = ami
			instance.InstanceType = size
			instance.KeyName = selectedKey
			#instance.SecurityGroups = ["default"] # Moved to Subnets 
			instance.SubnetId = subnets
			t.add_resource(instance)

	if selectedRdsCount:
		for node in selectedRdsCount:
			print node
			argDBEngine = "rdsEngine-%s" % str(node)
			argDBName = "dbname-%s" % str(node)
			argDBUsername = "dbusername-%s" % str(node)
			argDBPassword = "dbpassword-%s" % str(node)
			#argDBgbs = "dbgbs-%s" % str(node)
			argDBSize = "dbsize-%s" % str(node)

			DBEngine = request.args.get(argDBEngine)
			DBName = request.args.get(argDBName)
			DBUsername = request.args.get(argDBUsername)
			DBPassword = request.args.get(argDBPassword)
			#DBgbs = request.args.get(argDBgbs)
			DBSize = request.args.get(argDBSize)
			
			# Populate troposphere objects with form data
			RDSinstance = rds.DBInstance(DBName)
			RDSinstance.Engine = DBEngine
			RDSinstance.DBName = DBName
			RDSinstance.MasterUsername = DBUsername
			RDSinstance.MasterUserPassword = DBPassword
			RDSinstance.AllocatedStorage = "5"
			RDSinstance.DBInstanceClass = DBSize
			RDSinstance.DBSubnetGroupName = "rds-test" # HAard coded
			t.add_resource(RDSinstance)

	#for element in genericComputeConfig:
		#instance = ec2.Instance(element)
		#instance.ImageId = genericComputeConfig[element][0]
		#instance.InstanceType = genericComputeConfig[element][1]
		#instance.KeyName = selectedKey
		##instance.SecurityGroups = ["default"]
		#instance.SubnetId = subnets
		#t.add_resource(instance)

	output = t.to_json()
	print output

	return flask.render_template("display.html", output=output)
#------------------------------------------------------
@app.route("/refresh")
def refreshdata():
	'''Refresh data from AWS and update all cache files '''
	getAWS.getAMIs()
	getAWS.getSSHKeys()
	getAWS.getRegions()
	#getDBEngines()
	return redirect("/")
	
#------------------------------------------------------
@app.route("/config", methods=["POST","GET"])
def config():
	#if request.method == "POST":
	if request.method == "GET":

		if request.args.get('ec2Count'):
			selectedEc2Count = int(request.args.get('ec2Count'))
			Ec2Count = range(0,selectedEc2Count)
		if request.args.get('rdsCount'):
			selectedRdsCount = int(request.args.get('rdsCount'))
			RdsCount = range(0,selectedRdsCount)
		#selectedEc2Count = int(flask.request.form["ec2Count"])
		#selectedRdsCount = int(flask.request.form["rdsCount"])
		#selectedElb = flask.request.form["elb"]
	
		#RdsCount = range(0,selectedRdsCount)

		try:
			amiList = open("aws_cache/ami.list", "r").readlines()
			sshKeys = open("aws_cache/ssh-keys.list", "r").readlines()
			regions = open("aws_cache/aws-regions.list", "r").readlines()
			# Need to pull from AWS
			DBEngines = ['Mysql']
			subnets = ['SUBNET-ID']
		except IOError:
			getAWS.getAWS.main()

	return flask.render_template("config.html", sshKeys=sshKeys, regions=regions, Ec2Count=Ec2Count, RdsCount=RdsCount, amiList=amiList, rawEc2Count=selectedEc2Count, rawRdsCount=selectedRdsCount, DBEngines=DBEngines, subnets=subnets)
#------------------------------------------------------
#@app.route("/", methods=["POST", "GET"])
@app.route("/")
def index():
	#sshKeys = ['key1', 'key2']
	#regions = ["us-west2", "ap-southeast-1"]
	return flask.render_template("index.html")
#------------------------------------------------------
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0')
