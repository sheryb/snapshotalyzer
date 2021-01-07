from setuptools import setup

setup(
	name='Snapshotalyzer',
	version='0.1',
	author='SB',
	description="Snapshotalyzer is a tool to manage AWS EC2 snapshots",
	packages=["shotty"],
	url="https://github.com/sheryb/snapshotalyzer",
	install_requires=[
		'click',
		'boto3'
	],
	entry_points='''
		[console_scripts]
		shotty=shotty.shotty:cli
	''',
	)