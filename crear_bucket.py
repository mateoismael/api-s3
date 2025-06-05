import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Se espera un JSON en el body: { "bucket": "nombre-nuevo-bucket" }
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'JSON inválido en el body'})
        }

    bucket_name = body.get('bucket')
    if not bucket_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Falta parámetro "bucket"'})
        }

    # Intentar crear el bucket
    try:
        s3.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        # Si el bucket ya existe o el nombre no es válido, boto3 lanzará un error
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou' or error_code == 'BucketAlreadyExists':
            return {
                'statusCode': 409,
                'body': json.dumps({'error': f'El bucket "{bucket_name}" ya existe'})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    return {
        'statusCode': 200,
        'body': json.dumps({'message': f'Bucket "{bucket_name}" creado exitosamente'})
    }
