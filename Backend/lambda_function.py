import json
import boto3
import os
import logging
import requests
import base64

api_key = os.environ['API_KEY']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def event_contents(event):
    """
    Function to check the event and extract the image json
    """
    try:
        print(f'body: {event['image']}')
        image_data = (event['image'])
        prefix = "base64,"
        body = image_data[image_data.find(prefix) + len(prefix):]
        print(f'body: {body}')
        return body

    except Exception as e:
        logger.error("ERROR: Unexpected error in event_contents()")
        logger.error(e)


def api_invocation():
    """
    Function to pass the screenshot to OpenAI API and get the hint
    """
    print(f'In api Invocation')
    s3_client = boto3.client('s3')

    try:
        image_url = s3_client.generate_presigned_url('get_object',
            Params={'Bucket': 'leetcode-hint-record', 'Key': 'screenshot.png'},
            ExpiresIn=3600  
        )
        print(f'image_url : {image_url}')
        print({type(image_url)})

        api_url = "https://api.openai.com/v1/chat/completions"
        headers_ = {'Content-Type' : 'application/json', 'Authorization' : f'Bearer {api_key}'}
        request_data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Give me a one line hint on what can be done based on the screenshot given in prompt to start the code or correct it. Do not include any code as a response, or give me a step by step on what to do, I just want a nudge in the right direction."
                },
                {
                    "role": "user",
                    "content" : [
                        {
                            "type": "image_url",
                            "image_url" : {
                                "url": f"{image_url}",
                            }
                        },
                    ]
                }
            ]
        }

        api_response = requests.post(f'{api_url}', data = json.dumps(request_data), headers = headers_, timeout = 45)
        print(f'response :{api_response}')
        print(f'response json : {api_response.json()}')
        response_json = api_response.json()
        api_response_string = response_json['choices'][0]['message']['content']
        return api_response_string
    
    except Exception as e:
        logger.error("ERROR: Unexpected error in api_invocation()")
        logger.error(e)
        return f'api_invocation did not work'


def insert_into_S3(image_input_base64):
    """
    Function to insert image into S3 bucket as screenshot.png
    """
    s3_client = boto3.client('s3')
    try:
        image_decoded_bytes = base64.b64decode(image_input_base64)
        s3_leetcode_hint_response = s3_client.put_object(Body = image_decoded_bytes, Bucket = "leetcode-hint-record", Key = f'screenshot.png')
        s3_response_put_acl = s3_client.put_object_acl(Bucket = "leetcode-hint-record", Key = f'screenshot.png', ACL = 'public-read')
    except Exception as e:
        logger.error(f'ERROR: Could not insert into S3')
        logger.error(e)


def delete_from_S3():
    """
    Function to delete the screenshot from S3
    """
    s3_client = boto3.client('s3')
    try:
        s3_delete_response = s3_client.delete_object(Bucket = "leetcode-hint-record", Key = f'screenshot.png')
    except Exception as e:
        logger.error(f'ERROR: Could not insert into S3')
        logger.error(e)


def lambda_handler(event, context):
    print(f'event : {event}')

    try:
        image_input_base64 = event_contents(event)
        print(f'image_imput_64 in lambda handler: {image_input_base64}')
        insert_into_S3(image_input_base64)
        api_response = api_invocation()
        print(f'api_response in main:{api_response}')
        delete_from_S3()

        return {
            'statusCode': 200,
            'body': json.dumps(f'Hint : {api_response}')
        }
    
    except Exception as e:
        logger.error(f'ERROR: Did not work somewhere')
        logger.error(e)
        return {
            'statusCode' : 506,
            'body' : json.dumps('Failed lol')
        }

    
