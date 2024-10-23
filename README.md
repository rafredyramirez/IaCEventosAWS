# IaCEventosAWS

Infraestructura como código para aprovisionar servicios en la nube de AWS.

## Pasos de configuración

1. Para almacenar las lambdas y archivos yml del proyecto cree previamente un bucket de S3 y actualice los valores `Default` del parámetro `SourceCodeBucketName` en cada stack anidado segun se requiera con el nombre de dicho bucket.

2. Para probar la funcionalidad de envio de correos, actualice los valores `Default` de los parámetros `SESVerifiedSenderEmailIdentityName` y `SESVerifiedDestinationEmailIdentityName` en el stack anidado `stack-attendee-register.yml`

3. Suba al bucket de S3 que se creó en el paso 1 los archivos yml de los stacks anidados (sin incluir el `stack-main.yml`), asi como los acrhivos zip con el código de las funciones lambda.

4. Tome la url del objeto correspondiete a cada archivo yml de los stack anidados, generada por S3, (las que inician por https) y actualice los parámetros `TemplateURL` de cada stack en el archivo `stack-main.yml` según se requiera.

## Ejecución

Comando para aprovicionar el stack principal:

`aws cloudformation deploy --stack-name stack-main --template-file stack-main.yml --capabilities CAPABILITY_NAMED_IAM`