
# Sistema administrador de eventos y sus asistentes

Este proyecto utiliza AWS CloudFormation para gestionar recursos en la nube de manera eficiente, escalable y automatizada. Además, se gestiona mediante Bitbucket Pipelines para integración continua y despliegue automatizado.

A continuación, se detallan los pasos necesarios para instalar, configurar y desplegar la aplicación.

# Requisitos previos

1. Cuenta de AWS: Asegúrate de tener acceso a una cuenta de AWS con los permisos adecuados para crear recursos mediante CloudFormation para poder parametrizar las varibles: AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY.

2. Tener creado un bucked de S3 que irá en las variables SourceCodeBucketName y EventRegistersBucketName

3. Acceso a SES: Los correos del sistema se envían y reciben a través de Amazon SES, por lo que es necesario verificar las identidades de correo y estos se reemplazarán en las variables: SESVerifiedSenderEmailIdentityName y SESVerifiedDestinationEmailIdentityName


# Despliegue de IaC - Pasos de configuración

Se debe  configurar las siguientes variables de entorno en Bitbucket Pipelines para asegurar el correcto funcionamiento:

1. Credencial de AWS y su clave:

    AWS_ACCESS_KEY_ID: Clave de acceso utilizada como parte de las credenciales para autenticar al usuario.

    AWS_SECRET_ACCESS_KEY: Clave secreta utilizada para la autenticación.

2. Datos para el Buckets S3:
    
    SourceCodeBucketName: Nombre del bucket donde se suben los zip con el codigo de las funciones Lambda.
    
    EventRegistersBucketName: Nombre del bucket para guardar los json de registro de asistentes a eventos.

3. Configuración de SES:

    SESVerifiedSenderEmailIdentityName: Correo que será verificado manualmente en SES para enviar correos

    SESVerifiedDestinationEmailIdentityName: Correo que será verificado manualmente en SES para recibir correos

4. Parámetros adicionales:

    StageDeploy: Nombre stage del ambiente

    InstanceName: Nombre de la instancia de Lightsail


## Acceder al sitio web

Una vez que los recursos hayan sido aprovisionados, sigue estos pasos para acceder al sitio:

1. Obtener la URL del sitio de Lightsail ...................

2. Verificar el estado del sitio web accediendo mediante el navegador.
    Revisar de que las funciones Lambda estén respondiendo correctamente y los correos a través de SES sean enviados.

3. Revisar los logs en CloudWatch para identificar posibles errores o advertencias en el funcionamiento.