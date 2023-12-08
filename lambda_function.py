import boto3
import json
from ldap3 import Server, Connection, ALL
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret(secret_name):
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None


secrets = get_secret('aws/lambda/password-expiry-notifier')  
AD_USER = secrets['AD_USER']
AD_PASSWORD = secrets['AD_PASSWORD']
AD_SERVER = "ldap://myorg.aws"
AD_SEARCH_BASE = "DC=myorg,DC=aws"

def lambda_handler(event, context):
    conn = None
    try:
        logger.info('1. Starting Lambda function...')
        data = json.loads(event['body'])
        ad_username = data['ad_username']
        token = data['token']
        new_password = data['new_password']

        logger.info('2. Connecting to AD server...')
        server = Server(AD_SERVER, get_info=ALL)
        conn = Connection(server, user=AD_USER, password=AD_PASSWORD, auto_bind=True)
        logger.info('Connected to AD server successfully.')

        if not validate_token(ad_username, token, conn):
            raise ValueError("Invalid token")

        client = boto3.client('ds')
        response = client.reset_user_password(
            DirectoryId='dir-id',
            UserName=ad_username,
            NewPassword=new_password
        )

        logger.info('Password reset successful')
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Password reset successful'})
        }
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {
            'statusCode': 400,
            'body': json.dumps({'message': str(e)})
        }
    finally:
        if conn is not None:
            conn.unbind()
            logger.info('Disconnected from AD server')

def validate_token(username, token, conn):
    try:
        logger.info(f'Validating token for user: {username}')
        search_filter = f'(sAMAccountName={username})'
        conn.search(AD_SEARCH_BASE, search_filter, attributes=['description'])

        if conn.entries:
            user_description = conn.entries[0]['description'].value
            if user_description == token:
                logger.info('Token validation successful')
                return True
            else:
                logger.warning('Token validation failed: Token does not match')
                return False
        else:
            logger.warning('Token validation failed: User not found')
            return False

    except Exception as e:
        logger.error(f'Error in validate_token: {str(e)}')
        return False
