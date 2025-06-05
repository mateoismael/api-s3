import json, base64, boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # 1) Imprime el evento completo para depurar
    print("DEBUG ── event completo:")
    print(json.dumps(event))

    # 2) Intentamos parsear el body
    try:
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "JSON inválido en el body: " + str(e)})
        }

    # Resto de la lógica...
    bucket = body.get("bucket", None)
    if not bucket:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Falta parámetro 'bucket'"})
        }

    # … creación del bucket …
    return {
        "statusCode": 200,
        "body": json.dumps({"message": f"Bucket '{bucket}' creado correctamente"})
    }
