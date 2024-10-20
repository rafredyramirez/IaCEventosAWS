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
        # Verificar si hay query parameters (event_id)
        query_params = event.get('queryStringParameters', {})

        if query_params and 'event_id' in query_params:
            # Obtener evento por event_id
            event_id = query_params['event_id']
            response = table.get_item(Key={'event_id': event_id})

            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f"No se encontró el evento con ID '{event_id}'")
                }

            # Retornar el evento encontrado
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'], default=decimal_to_float)
            }

        else:
            # Obtener todos los eventos
            response = table.scan()

            if 'Items' not in response or not response['Items']:
                return {
                    'statusCode': 404,
                    'body': json.dumps("No se encontraron eventos.")
                }

            # Retornar todos los eventos
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