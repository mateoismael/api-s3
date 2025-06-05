import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Handler para el endpoint POST /s3/crear-directorio.
    Acepta un JSON en el body con la forma:
      { "bucket": "nombre-del-bucket", "directorio": "ruta/carpeta" }
    Maneja los casos en que API Gateway entregue event["body"] como string JSON
    o como un dict Python ya parseado.
    """

    # 1) DEBUG: imprimimos el evento completo para inspeccionar en CloudWatch Logs
    print("DEBUG ── event completo:")
    print(json.dumps(event))

    # ------------------------------------------------------------------
    # 2) Extraer raw_body: puede venir como dict (si API Gateway ya lo parseó)
    #    o como string JSON. Si no existe, raw_body = None.
    raw_body = event.get("body", None)

    # 3) Determinar si ya está parseado (dict) o es string JSON
    if isinstance(raw_body, dict):
        body = raw_body
    else:
        # raw_body es un string (JSON) o None
        try:
            body = json.loads(raw_body or "{}")
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": f"JSON inválido en el body: {str(e)}"
                })
            }

    # ------------------------------------------------------------------
    # 4) Verificar que tengamos los parámetros "bucket" y "directorio" en el body
    bucket_name = body.get("bucket")
    directorio = body.get("directorio")

    if not bucket_name or not directorio:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Faltan parámetros 'bucket' o 'directorio' en el body"
            })
        }

    # ------------------------------------------------------------------
    # 5) Asegurarnos de que la ruta del directorio termine en "/"
    if not directorio.endswith("/"):
        directorio += "/"

    # 6) Para “crear” el directorio en S3 simulamos subiendo un objeto vacío:
    #    clave = "directorio/_placeholder"
    key_placeholder = directorio + "_placeholder"

    try:
        s3.put_object(Bucket=bucket_name, Key=key_placeholder, Body=b"")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchBucket":
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": f"El bucket '{bucket_name}' no existe"
                })
            }
        # Otro error genérico de AWS S3
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": str(e)
            })
        }

    # ------------------------------------------------------------------
    # 7) Si llegamos aquí, el “directorio” (placeholder) se creó correctamente
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Directorio '{directorio}' creado exitosamente en el bucket '{bucket_name}'"
        })
    }
