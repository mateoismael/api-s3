import json
import base64
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Se espera un JSON en el body:
    # {
    #   "bucket": "mi-bucket-existente",
    #   "directorio": "ruta/a/directorio/",   # opcional
    #   "nombreArchivo": "foto.png",
    #   "archivoBase64": "iVBORw0KGgoAAAANSUhEUg..."  # Cadena Base64
    # }
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'JSON inválido en el body'})
        }

    bucket_name   = body.get('bucket')
    directorio    = body.get('directorio', '')
    nombre_archivo = body.get('nombreArchivo')
    archivo_b64   = body.get('archivoBase64')

    if not bucket_name or not nombre_archivo or not archivo_b64:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Faltan parámetros: "bucket", "nombreArchivo" o "archivoBase64"'})
        }

    # Asegurar que el directorio termine en "/"
    if directorio and not directorio.endswith('/'):
        directorio += '/'

    # Decodificar Base64 a bytes
    try:
        contenido_bytes = base64.b64decode(archivo_b64)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Error al decodificar Base64: ' + str(e)})
        }

    key_final = f"{directorio}{nombre_archivo}"
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=key_final,
            Body=contenido_bytes
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'El bucket "{bucket_name}" no existe'})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Archivo "{nombre_archivo}" subido a "{bucket_name}/{directorio}"'
        })
    }
