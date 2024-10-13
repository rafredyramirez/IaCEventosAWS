# IaCEventosAWS
Infraestructura como código para aprovisionar servicios en la nube de AWS. 

##Nota
Para almacenar las lambdas del proyecto cree una carpera dentro del bucket S3  

##Orden de ejecuión 

1. lambdas-stack.yml

Comando para aprovicionar en Windows:
aws cloudformation create-stack 
    --stack-name lambdas-stack 
    --template-body file://lambdas-stack.yml 
    --capabilities CAPABILITY_NAMED_IAM

Comando para aprovicionar en Mac:
aws cloudformation create-stack \
    --stack-name lambdas-stack \
    --template-body file://lambdas-stack.yml \
    --capabilities CAPABILITY_NAMED_IAM

2. api-gateway-stack.yml

Comando para aprovicionar en Windows:
aws cloudformation create-stack 
    --stack-name api-gateway-stack 
    --template-body file://api-gateway-stack.yml 
    --capabilities CAPABILITY_NAMED_IAM

Comando para aprovicionar en Mac:
aws cloudformation create-stack \
    --stack-name api-gateway-stack \
    --template-body file://api-gateway-stack.yml \
    --capabilities CAPABILITY_NAMED_IAM 
