import boto3
import os
import json
import logging


# Inicializar los clientes de boto3 para S3 y SQS
s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# Configurar el logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variable de entorno para obtener la URL de la cola SQS
queue_url = os.environ.get('QUEUE_URL')

def lambda_handler(event, context):
    '''
    Función Lambda que procesa un mensaje de una cola SQS y guarda un JSON en S3
    '''
    
    # Ver cuantos registros (mensajes) se recibieron en el evento
    records = event.get('Records', [])
    logger.info('Se recibieron {} mensajes de SQS para procesar'.format(len(records)))

    # Obtener el nombre del bicket donde se van a guardar los objetos json
    registers_bucket_name = os.environ.get('REGISTERS_BUCKET')
    
    for record in records:
        # Cada record contiene un mensaje de SQS
        try:
            logger.info('Extrayendo informacion del registro...')
            
            # Extraer los datos del mensaje
            message_body = json.loads(record['body'])
            message_receipt_handle = record['receiptHandle']
            
            logger.info('Procesando registro para asistente {}'.format(message_body['attendee_id']))
            
            json_data = {
                'event_id': message_body['event_id'],
                'attendee_id': message_body['attendee_id'],
                'attendee_name': message_body['attendee_name'],
                'attendee_email': message_body['attendee_email'], 
                'status': message_body['status']
            }
                    
            logger.info('Guardando json en S3...')

            # Guardar json en S#
            s3.put_object(
                Body=json.dumps(json_data),
                Bucket=registers_bucket_name,
                Key = '{}-{}.json'.format(json_data['event_id'], json_data['attendee_id'])
            )
            
            logger.info('Eliminando registro procesado de la cola...')
            
            # Eliminar mensaje de la cola
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message_receipt_handle
            )
            
            logger.info('Registro procesado exitosamente')
            
        except Exception as e:
            # Si hay un error al procesar un mensaje, lo logueamos.
            logger.error('Error al procesar el mensaje: {}'.format(e))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Registros procesados exitosamente')
    }

