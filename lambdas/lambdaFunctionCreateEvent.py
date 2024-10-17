import json
import boto3
import os

from datetime import datetime
from botocore.exceptions import ClientError

# Lambda que permite crear un evento

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "events"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    # Se espera que la solicitud HTTP POST tenga un body con la información del evento
    try:
        # Si 'body' no está presente, utiliza el evento directamente
        if 'body' in event:
            data = json.loads(event['body'])
        else:
            # Si estás probando localmente, simplemente asume que el evento ya contiene los datos
            data = event

        # Validación básica (verifica que ciertos campos existan)
        required_fields = ['event_id', 'name_event', 'description', 'date', 'time', 
                           'max_capacity', 'organizer', 'status', 'event_location']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f"Falta el campo requerido: {field}")
                }
        
        # Inserta el nuevo evento en la tabla de DynamoDB
        table.put_item(
            Item={
                'event_id': data['event_id'],
                'name_event': data['name_event'],
                'description': data['description'],
                'date': data['date'],  # Formato ISO YYYY-MM-DD
                'time': data['time'],    # Formato HH:MM
                'max_capacity': int(data['max_capacity']),
                'organizer': data['organizer'],
                'status': data['status'],  # Por ejemplo: "activo", "cancelado"
                'event_location': data['event_location']
            }
        )
        
        # Respuesta de éxito
        return {
            'statusCode': 201,
            'body': json.dumps(f"Evento {data['name_event']} creado con exito")
        }
    
    except ClientError as e:
        # Manejo de errores si hay problemas al acceder a DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al crear el evento: {str(e)}")
        }
    
    except Exception as e:
        # Manejo de cualquier otro error
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        } 