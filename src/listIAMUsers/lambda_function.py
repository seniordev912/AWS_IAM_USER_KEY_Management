import boto3
import os

def lambda_handler(event, context):

	client =  boto3.client('iam', region_name = os.environ["REGION"])
	my_list = list()
	iam_all_users = client.list_users()
	for user in iam_all_users['Users']:
		my_list.append(user['UserName'])

	return {
			'body': {'userList': my_list},
			'headers': {'Content-Type': 'text/html', 'Access-Control-Allow-Origin': '*'}
	}