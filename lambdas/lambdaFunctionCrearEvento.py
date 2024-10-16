import json
import boto3
import os

from datetime import datetime
from botocore.exceptions import ClientError

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "eventos"
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
        required_fields = ['id_evento', 'nombre_evento', 'descripcion', 'fecha', 'hora', 
                           'capacidad_max', 'organizador', 'estado', 'lugar_evento']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f"Falta el campo requerido: {field}")
                }
        
        # Inserta el nuevo evento en la tabla de DynamoDB
        table.put_item(
            Item={
                'id_evento': data['id_evento'],
                'nombre_evento': data['nombre_evento'],
                'descripcion': data['descripcion'],
                'fecha': data['fecha'],  # Formato ISO YYYY-MM-DD
                'hora': data['hora'],    # Formato HH:MM
                'capacidad_max': int(data['capacidad_max']),
                'organizador': data['organizador'],
                'estado': data['estado'],  # Por ejemplo: "activo", "cancelado"
                'lugar_evento': data['lugar_evento'],
                'creado_en': datetime.now().isoformat()  # Fecha y hora de creación
            }
        )
        
        # Respuesta de éxito
        return {
            'statusCode': 201,
            'body': json.dumps(f"Evento {data['nombre_evento']} creado con exito")
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