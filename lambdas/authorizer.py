import json

def lambda_handler(event, context):
    # Obtener el token de autorización del encabezado (usualmente "Bearer <token>")
    token = event.get('authorizationToken')

    # Definir los recursos de la API Gateway (en este caso, puedes agregar un ARN específico)
    method_arn = event['methodArn']

    # Lógica para validar el token (en este ejemplo, validamos si el token es "allow" o "deny")
    if token == 'allow':
        # Generar política de autorización para permitir el acceso
        return generate_policy('user', 'Allow', method_arn)
    else:
        # En caso contrario, denegar el acceso
        return generate_policy('user', 'Deny', method_arn)

def generate_policy(principal_id, effect, resource):
    """
    Función para generar una política de autorización que permite o deniega acceso.
    :param principal_id: Identificador del principal (usuario).
    :param effect: 'Allow' o 'Deny' para otorgar o denegar acceso.
    :param resource: El ARN del recurso que intenta acceder.
    """
    auth_response = {
        'principalId': principal_id
    }

    if effect and resource:
        policy_document = {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
        auth_response['policyDocument'] = policy_document

    return auth_response
