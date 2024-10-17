import json
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Lambda que permite editar un evento

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource("dynamodb")
table_name = "events"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Si 'body' no está presente, utiliza el evento directamente
        if 'body' in event:
            data = json.loads(event['body'])
        else:
            # Si estás probando localmente, simplemente asume que el evento ya contiene los datos
            data = event
        
        # Validación básica (verifica que ciertos campos existan)
        required_fields = ['event_id']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f"Falta el campo requerido: {field}")
                }

        # Construye los valores que serán actualizados
        update_expression = "SET "
        expression_attribute_values = {}
        fields_to_update = ['name_event', 'description', 'date', 'time', 'max_capacity', 'organizer', 'status', 'event_location']
        
        # Añade cada campo a la expresión de actualización si está presente en el cuerpo
        for field in fields_to_update:
            if field in data:
                update_expression += f"{field} = :{field}, "
                expression_attribute_values[f":{field}"] = data[field]
        
        # Remueve la coma y el espacio final de la expresión de actualización
        update_expression = update_expression.rstrip(", ")

        # Ejecuta la actualización
        response = table.update_item(
            Key={
                'event_id': data['event_id']
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"  # Retorna los nuevos valores actualizados
        )

        # Respuesta de éxito con los valores actualizados
        return {
            'statusCode': 200,
            'body': json.dumps(f"Evento {data['event_id']} actualizado exitosamente: {response['Attributes']}")
        }
    
    except ClientError as e:
        # Manejo de errores si hay problemas al acceder a DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error al actualizar el evento: {str(e)}")
        }
    
    except Exception as e:
        # Manejo de cualquier otro error
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error inesperado: {str(e)}")
        }
