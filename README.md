# echo-api
Simple API which echos back what it is sent

It is designed to be deployed behind a AWS v2 HTTP API Gateway.

It will extact the email claim from the JWT authorizer which is expected to be configured.

It adds the email address into the response payload.
