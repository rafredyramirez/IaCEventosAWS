import json
import boto3
import os
from botocore.exceptions import ClientError

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "eventos"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Si 'body' no está presente, utiliza el evento directamente
        if 'body' in event:
            data = json.loads(event['body'])
        else:
            # Si estás probando localmente, simplemente asume que el evento ya contiene los datos
            data = event
        
        # Validación básica (verifica que el campo 'id_evento' esté presente)
        if 'id_evento' not in data:
            return {
                'statusCode': 400,
                'body': json.dumps("Falta el campo requerido: id_evento")
            }

        # Realiza la operación de eliminación en DynamoDB utilizando la clave primaria (id_evento)
        response = table.delete_item(
            Key={
                'id_evento': data['id_evento']
            },
            ReturnValues='ALL_OLD'  # Retorna el valor del item antes de eliminarlo, si existe
        )

        # Verifica si el evento existía antes de eliminarlo
        if 'Attributes' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Evento con ID {data['id_evento']} no encontrado")
            }

        # Respuesta de éxito indicando que el evento fue eliminado
        return {
            'statusCode': 200,
            'body': json.dumps(f"Evento con ID {data['id_evento']} eliminado con éxito")
        }
    
    except ClientError as e:
        # Manejo de errores si hay problemas al acceder a DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al eliminar el evento: {str(e)}")
        }
    
    except Exception as e:
        # Manejo de cualquier otro error
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        }
