import os
import json
import urllib3


http = urllib3.PoolManager()

def lambda_handler(event, context):
    business_id = event.get('business_id')

    if not business_id:
        print('Error: `business_id` not found in the event payload.')
        return {'statusCode': 400, 'body': 'Missing business_id'}

    print(f'Processing task for business_id: {business_id}')

    try:
        payload = {
            'max_tokens': 10000,
            'business_id': business_id,
            'sync_generation': False,
        }
        encoded_payload = json.dumps(payload).encode('utf-8')
        response = http.request(
            'POST',
            f"{os.environ['BACKEND_DOMAIN']}/researches",
            body=encoded_payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {os.environ['SERVICE_TOKEN']}",
            }
        )

        print(f'ECS response status: {response.status}')
        print(f'ECS response data: {response.data.decode("utf-8")}')

        if response.status != 200:
            raise Exception(f'ECS service returned non-200 status: {response.status}')

        return {
            'statusCode': 200,
            'body': f'Successfully triggered ECS for {business_id}',
        }

    except Exception as e:
        print(f'An error occurred: {e}')
        raise e
