# OAuth 2.0 Client and Server

Technical challenge: implement resource server, authorization service and client application, following an OAuth 2.0 Authorization Code grant type protocol.  

An illustration example ([source](https://docs.oracle.com/cd/E82085_01/160023/JOS%20Implementation%20Guide/Output/oauth.htm)):
![OAuth 2.0 Architecture](https://raw.githubusercontent.com/trivelt/img-resources/master/oauth2-arch.png)


Application is implemented as a three separate components:
* ClientApp - runs on port 9000 and provide 2 endpoints: `/current_time` and `/epoch_time`
* AuthService - runs on port 9001 and manages authorization tokens
* ResourceServer - runs on port 9002 and contains protected time resources

In order to run the application, please execute the following command:

    sudo docker-compose build && sudo docker-compose up

There are also implemented two example test suites:
* tests/test_api.py - run by `python3 -m unittest discover tests/` when all services are started
* AuthService/tests/test_auth_service.py - run by ` cd AuthService/ && python3 -m unittest discover tests/; cd -
`