import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

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
        # Verificar si hay query parameters
        query_params = event.get('queryStringParameters', {})

        if query_params:
            # Consultar por 'event_id' si está presente
            if 'event_id' in query_params:
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

            # Consultar por 'event_status' usando el GSI con el EventStatusIndex
            elif 'event_status' in query_params:
                event_status = query_params['event_status']
                response = table.query(
                    IndexName="EventStatusIndex", 
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('event_status').eq(event_status)
                )

                if 'Items' not in response or not response['Items']:
                    return {
                        'statusCode': 404,
                        'body': json.dumps(f"No se encontraron eventos con status '{event_status}'")
                    }

                # Retornar los eventos encontrados
                return {
                    'statusCode': 200,
                    'body': json.dumps(response['Items'], default=decimal_to_float)
                }

        # Si no hay parámetros, escanear todos los eventos
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
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al consultar el evento: {str(e)}")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        }
