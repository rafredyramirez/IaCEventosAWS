import json
import boto3
import os
from botocore.exceptions import ClientError

# Lambda que permite eliminar un evento

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "events"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Extraer el parámetro 'name_event' desde el body (PUT solicita cuerpo)
        if 'body' in event:
            data = json.loads(event['body'])
        else:
            return {
                'statusCode': 400,
                'body': json.dumps("Falta el cuerpo de la solicitud")
            }

        # Validación básica: Verifica si se pasó el campo 'name_event'
        name_event = data.get('name_event')
        if not name_event:
            return {
                'statusCode': 400,
                'body': json.dumps("Falta el campo requerido: name_event")
            }

        # Consulta en el índice secundario global (GSI) NameEventIndex
        query_response = table.query(
            IndexName="NameEventIndex",  # Nombre del índice
            KeyConditionExpression=boto3.dynamodb.conditions.Key('name_event').eq(name_event)
        )

        # Verifica si se encontró el evento
        if 'Items' not in query_response or not query_response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps(f"No se encontraron eventos con nombre '{name_event}'")
            }

        # Asumimos que solo habrá un evento con ese nombre
        event_to_delete = query_response['Items'][0]
        event_id = event_to_delete['id_evento']

        # Elimina el evento utilizando su ID
        delete_response = table.delete_item(
            Key={'id_evento': event_id},
            ReturnValues='ALL_OLD'
        )

        # Verifica si se eliminó correctamente
        if 'Attributes' not in delete_response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Evento con ID {event_id} no encontrado para eliminar")
            }

        # Respuesta de éxito
        return {
            'statusCode': 200,
            'body': json.dumps(f"Evento '{name_event}' eliminado con éxito")
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