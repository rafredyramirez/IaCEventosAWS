import json
import boto3
import os
from botocore.exceptions import ClientError
from decimal import Decimal

# Lambda que permite consultar un evento

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "events"
table = dynamodb.Table(table_name)

# Función para convertir Decimals a float para serialización
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        # Extrae el parámetro 'name_event' desde los query parameters
        if 'queryStringParameters' in event and event['queryStringParameters']:
            name_event = event['queryStringParameters'].get('name_event')
        else:
            return {
                'statusCode': 400,
                'body': json.dumps("Falta el parámetro requerido: name_event")
            }

        # Realiza la consulta en DynamoDB utilizando el índice secundario (GSI)
        response = table.query(
            IndexName="NameEventIndex",  # Nombre del índice global secundario
            KeyConditionExpression=boto3.dynamodb.conditions.Key('name_event').eq(name_event)
        )

        # Verifica si se encontraron eventos
        if 'Items' not in response or not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps(f"No se encontraron eventos con nombre '{name_event}'")
            }

        # Retorna los eventos encontrados
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'], default=decimal_to_float)
        }

    except ClientError as e:
        # Manejo de errores de DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al consultar el evento: {str(e)}")
        }

    except Exception as e:
        # Manejo de errores generales
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        }