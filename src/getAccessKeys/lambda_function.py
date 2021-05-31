import boto3
from datetime import date
import os

def lambda_handler(event, context):

	maximum_duration = 90

	iamClient =  boto3.client('iam', region_name = os.environ["REGION"])
	emailClient = boto3.client('sns', region_name = os.environ["REGION"])

	# response = emailClient.create_topic(Name="CheckingAccessKeys")
	# topic_arn = response["TopicArn"]
	topic_arn = "arn:aws:sns:eu-west-1:062424101843:test-topic"

	my_list=list()
	access_keys_of_user=list()
	iam_all_users = iamClient.list_users()
	
	for user in iam_all_users['Users']:
		my_list.append(user['UserName'])

	for user_name in my_list:
		access_keys_of_user = iamClient.list_access_keys(UserName=user_name)

		for access_key_of_user in access_keys_of_user['AccessKeyMetadata']:
			accessKeydate = access_key_of_user['CreateDate'].date()
			currentdate = date.today()
			active_days = currentdate - accessKeydate
			
			print("+++++++++++++", active_days.days)
			
			if int(active_days.days) > maximum_duration:
				try:
					response = iamClient.delete_access_key(
						UserName = user_name,
						AccessKeyId = access_key_of_user['AccessKeyId']
					)
					emailClient.publish(
						TopicArn=topic_arn,
						Message="You could not use this access key, because it was expired.",
						Subject="This Access Key was expired."
					)
				except Exception as e:
					return {"Exception", e}
		if len(access_keys_of_user['AccessKeyMetadata']) > 1:
			temp_accessKeyID = access_keys_of_user['AccessKeyMetadata'][0]['AccessKeyId']
			temp_date = access_keys_of_user['AccessKeyMetadata'][0]['CreateDate'].date()

			for access_key_of_user in access_keys_of_user['AccessKeyMetadata']:
				if temp_date < access_key_of_user['CreateDate'].date():
					try:
						response = iamClient.delete_access_key(
							UserName = user_name,
							AccessKeyId = access_key_of_user['AccessKeyId']
						)
						emailClient.publish(
							TopicArn=topic_arn, 
							Message="You could not use this access key, because it was older.", 
							Subject="This Access Key was older."
						)
					except Exception as e:
						return {"Exception", e}
		access_keys_of_user["AccessKeyMetadata"][0]["CreateDate"] = str(access_keys_of_user["AccessKeyMetadata"][0]["CreateDate"])	

	user_key_list = []
	currentdate = date.today()

	for user_name in my_list:
		accessKey = iamClient.list_access_keys(UserName=user_name)['AccessKeyMetadata'][0]['AccessKeyId']
		availableDuration = currentdate - iamClient.list_access_keys(UserName=user_name)['AccessKeyMetadata'][0]['CreateDate'].date()
		user_key_list.append({"userName": user_name, "accessKey": accessKey, "availableDuration": "%d(%d)" % (int(availableDuration.days), maximum_duration)})
		
	return {
		'body': {'keyList': user_key_list},
		'headers': {'Content-Type': 'text/html', 'Access-Control-Allow-Origin': '*'}
	}
