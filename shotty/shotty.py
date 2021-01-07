import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
	instaces = []

	if project: 
		filters = [{'Name':'tag:Project', 'Values':[project]}]
		instances = ec2.instances.filter(Filters=filters)
	else:
		instances = ec2.instances.all()
	return instances

def has_pending_snapshot(volume):
	snapshots = list(volume.snapshots.all())
	return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
	"""Shotty manages snapshots"""
@cli.group('snapshots')
def snapshots():
	"""Commands for snapshots"""
	
@snapshots.command('list')
@click.option('--project', default=None, help="Only snapshots for project (tag project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help="List all snapshots for each volumes, not just the most recent")

def list_snapshots(project, list_all):
	"Lits of ec2 snapshots"

	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			for s in v.snapshots.all():
				print(", ".join((
					s.id,
					v.id,
					i.id,
					s.state,
					s.progress,
					s.start_time.strftime("%C")
					)))
				if s.state == 'completed' and not list_all: break
	return

@cli.group('volumes')
def volumes():
	"""Commands for volumes"""

@cli.group('instances')
def instances():
	"""Commands for instances"""
@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project (tag project:<name>)")

def list_volumes(project):
	"Lits of ec2 volumes"

	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			print(", ".join((
			v.id,
			i.id,
			v.state,
			str(v.size) + "GiB",
			v.encrypted and "Encrypted" or "Not Encrypted")))
	return

@instances.command('snapshot', 
	help='Create snapshots of all volumes')
@click.option('--project', default=None, 
	help="Only instaces for project (tag project:<name>)")
def create_snapshots(project):
	"Create snapshots for EC2 instances"

	instances = filter_instances(project)

	for i in instances:
		print("Stopping {0}...".format(i.id))

		i.stop()
		i.wait_until_stopped()

		for v in i.volumes.all():
			if has_pending_snapshot(v):
				print(" Skipping {0}, snapshot already in progress".format(v.id))
				continue
			print("Creating snapshot of {0}".format(v.id))
			v.create_snapshot(Description="Created by Snapshotalyzer")

		print("Starting {0}...".format(i.id))

		i.start()
		i.wait_until_running()

	print("Job Done!")
	return

@instances.command('list')
@click.option('--project', default=None, help="Only instaces for project (tag project:<name>)")

def list_instances(project):
	"Lits of ec2 instaces"
	
	instances = filter_instances(project)

	for i in instances:
		tags = { t['Key']: t['Value'] for t in i.tags or []}
		print(', '.join((
			i.id,
			i.instance_type,
			i.placement['AvailabilityZone'],
			i.state['Name'],
			i.public_dns_name,
			tags.get('project', '<no project>'))))
	return

@instances.command('stop')
@click.option('--project', default=None, help="Only instances for project")

def stop_instances(project):
	"Stop EC2 Instaces"
	
	instances = filter_instances(project)
	for i in instances:
		print('Stopping {0}...'.format(i.id))
		try:
			i.stop()
		except botocore.exceptions.ClientError as e:
			print(" Could not stop {0}. ".format(i.id) + str(e))
			continue
	return

@instances.command('start')
@click.option('--project', default=None, help="Only instances for project")

def stop_instances(project):
	"Stop EC2 Instaces"
	
	instances = filter_instances(project)
	for i in instances:
		print('Starting {0}...'.format(i.id))
		try:
			i.start()
		except botocore.exceptions.ClientError as e:
			print(" Could not start {0}. ".format(i.id) + str(e))
			continue
	return

if __name__ == '__main__':
	cli()

	