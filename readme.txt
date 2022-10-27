These functions handle the notification service.

TO setup:
1. python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. npm install

start application in offline mode:
sls offline start


to debug a function in local:
sls invoke local --f <function name>




To install the codes on lambda:
1. python3 -m venv venv (ubuntu) or  .\venv\Scripts\activate (Windows)
2. source venv/bin/activate
3. pip install -r requirements.txt --target .
4. npm install

there are 3 stages as of now:
1. local => local developement
2. dev
3. Qa

Need to add the stages for the uat, demo and prod.

This project also uses AWS appsync more on this can be found on: https://docs.aws.amazon.com/appsync/latest/devguide/quickstart.html
dev appsync: https://console.aws.amazon.com/appsync/home?region=us-east-1#/ugomguhf55goxkwuew5p4znkne/v1/home


sls invoke local --function premium --path .\sample_data\calculatemotorpremiumsig_data.json
