import json
import boto3
import os
import logging


# Inicializar los clientes de boto3 para DynamoDB y SQS
dynamodb = boto3.client('dynamodb')
sqs = boto3.client('sqs')

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variables de entorno para obtener los nombres de las tablas y la URL de la cola SQS
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
            'body': json.dumps('Faltan campos para registrar al asistentes al evento')
        }
    
    # Crear el item para la tabla DynamoDB de registro a eventos
    event_register_item = {
        'event_id': {'S': event_id},
        'attendee_id': {'S': attendee_id},
        'status': {'S': status}
    }

    # Crear el item para la tabla DynamoDB de asistentes
    attendee_item = {
        'id': {'S': attendee_id},
        'name': {'S': attendee_name},
        'email': {'S': attendee_email}
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
