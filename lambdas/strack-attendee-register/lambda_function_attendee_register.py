import json
import boto3
import os
from datetime import datetime
import string
import secrets
import logging


# Inicializar los clientes de boto3 para DynamoDB y SQS
dynamodb = boto3.client('dynamodb')
sqs = boto3.client('sqs')

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variables de entorno para obtener los nombres de las tablas y la URL de la cola SQS
events_table_name = os.environ.get('EVENTS_TABLE_NAME')
event_registers_table_name = os.environ.get('EVENT_REGISTERS_TABLE_NAME')
attendees_table_name = os.environ.get('ATTENDEES_TABLE_NAME')
queue_url = os.environ.get('QUEUE_URL')

def lambda_handler(event, context):
    '''
    Función Lambda que inserta datos en DynamoDB y luego envía un mensaje a una cola SQS.
    '''
    
    # Los datos que provienen del evento pueden estar en un formato JSON
    event_id = event.get('event_id')
    attendee_id = event.get('attendee_id')
    attendee_name = event.get('attendee_name')
    attendee_email = event.get('attendee_email')
    status = 'Confirmado'
    
    if not event_id or not attendee_id or not attendee_name or not attendee_email:
        return {
            'statusCode': 400,
            'body': json.dumps('Faltan campos para registrar al asistente al evento')
        }

    # Obtener datos del evento
    event_data = dynamodb.get_item(
        TableName=events_table_name,
        Key={
            'event_id': {'S': event_id}
        }
    )

    name_event = event_data['Item']['name_event']['S']
    event_date = event_data['Item']['event_date']['S']
    organizer = event_data['Item']['organizer']['S']
    max_capacity = int(event_data['Item']['max_capacity']['N'])

    # Calcular el número de asistentes actuales consultando la tabla de registros de asitentes a los eventos
    current_attendees_amount = dynamodb.query(
        TableName=event_registers_table_name,
        IndexName='EventIDIndex',
        KeyConditionExpression='event_id = :event_id',
        ExpressionAttributeValues={
            ':event_id': {'S': event_id}
        },
        Select='COUNT'
    )

    # Verificar el número de asistentes actuales
    current_attendees_amount = current_attendees_amount['Count']

    # Comparar el número de asistentes actuales con la capacidad máxima
    if current_attendees_amount >= max_capacity:
        return {
            'statusCode': 400,
            'body': json.dumps('Capacidad maxima alcanzada para el evento')
        }
    
    # Crear el item para la tabla DynamoDB de registro a eventos
    # Tamanio del registration_id unico
    N = 10

    # Generar una cadena aleatoria
    gen_id = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(N))

    event_register_item = {
        'registration_id': {'S': str(gen_id)},
        'event_id': {'S': event_id},
        'attendee_id': {'S': attendee_id},
        'registration_date': {'S': datetime.today().strftime('%Y-%m-%d')},
        'status': {'S': status}
    }

    # Crear el item para la tabla DynamoDB de asistentes
    attendee_item = {
        'attendee_id': {'S': attendee_id},
        'attendee_name': {'S': attendee_name},
        'attendee_email': {'S': attendee_email}
    }
    
    # Inserción en DynamoDB
    try:
        dynamodb.put_item(
            TableName=event_registers_table_name,
            Item=event_register_item
        )

        dynamodb.put_item(
            TableName=attendees_table_name,
            Item=attendee_item
        )

        logger.info('Se ha registrado el asistente al evento exitosamente')
    except Exception as e:
        # Si hay un error al procesar un mensaje, lo logueamos.
        logger.error('Error al registrar el usuario al evento: {}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error al registrar el usuario al evento: {}'.format(e))
        }
    
    # Crear el mensaje en formato JSON para enviar a SQS
    message_body = {
        'event_id': event_id,
        'name_event': name_event,
        'event_date': event_date,
        'organizer': organizer,
        'attendee_id': attendee_id,
        'attendee_name': attendee_name,
        'attendee_email': attendee_email, 
        'status': status
    }

    sqs_message = json.dumps(message_body)
    
    # Enviar el mensaje a la cola SQS
    try:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=sqs_message
        )
        logger.info('Mensaje enviado a la cola exitosamente')
    except Exception as e:
        # Si hay un error al procesar un mensaje, lo logueamos.
        logger.error('Error al enviar mensaje a la cola: {}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error al enviar mensaje a la cola: {}'.format(e))
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Registro realizado exitosamente')
    }
