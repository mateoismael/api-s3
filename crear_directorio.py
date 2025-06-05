import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Se espera un JSON en el body: 
    # { "bucket": "nombre-bucket-existente", "directorio": "ruta/a/directorio/" }
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'JSON inválido en el body'})
        }

    bucket_name = body.get('bucket')
    directorio = body.get('directorio')  # ej. "mi-carpeta/"

    if not bucket_name or not directorio:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Faltan parámetros "bucket" o "directorio"'})
        }

    # Asegurar que el directorio termine en "/"
    if not directorio.endswith('/'):
        directorio += '/'

    key_marker = directorio + "_placeholder"  # puede ser "_placeholder" o ".keep"
    try:
        # Subimos un objeto vacío para “marcar” el directorio
        s3.put_object(Bucket=bucket_name, Key=key_marker, Body=b"")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'El bucket "{bucket_name}" no existe'})
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': str(e)})
            }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Directorio "{directorio}" creado (o ya existía) en bucket "{bucket_name}"'
        })
    }
