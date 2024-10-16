import json
import boto3
import os
from botocore.exceptions import ClientError
from decimal import Decimal

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "eventos"
table = dynamodb.Table(table_name)

# Función para convertir Decimals a float para serialización
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

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

        # Realiza la consulta en DynamoDB utilizando la clave primaria (id_evento)
        response = table.get_item(
            Key={
                'id_evento': data['id_evento']
            }
        )

        # Verifica si el evento existe en la tabla
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Evento con ID {data['id_evento']} no encontrado")
            }

        # Convierte la respuesta en JSON, manejando los Decimals
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'], default=decimal_to_float)  # Serializa Decimals a float
        }
    
    except ClientError as e:
        # Manejo de errores si hay problemas al acceder a DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al consultar el evento: {str(e)}")
        }
    
    except Exception as e:
        # Manejo de cualquier otro error
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        }
