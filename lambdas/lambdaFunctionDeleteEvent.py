import json
import boto3
import os
from botocore.exceptions import ClientError

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "events"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Intentar extraer y decodificar el cuerpo de la solicitud
        body = event.get('body', None)
        if not body:
            return {
                'statusCode': 400,
                'body': json.dumps("Falta el cuerpo de la solicitud")
            }

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps("El cuerpo de la solicitud no es un JSON válido")
            }

        # Validar el campo 'event_id'
        event_id = data.get('event_id')
        if not event_id:
            return {
                'statusCode': 400,
                'body': json.dumps("Falta el campo requerido: event_id")
            }

        # Eliminar el evento por ID
        delete_response = table.delete_item(
            Key={'event_id': event_id},
            ReturnValues='ALL_OLD'
        )

        # Verificar si el evento fue eliminado
        if 'Attributes' not in delete_response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Evento con ID {event_id} no encontrado para eliminar")
            }

        # Respuesta de éxito
        return {
            'statusCode': 200,
            'body': json.dumps(f"Evento con ID {event_id} eliminado con éxito")
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al eliminar el evento: {str(e)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        }
