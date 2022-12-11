# Fully Automated Twitter Bot
- Twitter: @BentleySuperior

### Dependencies
***
- boto3 - 
- gspread - Google API wrapper that allows for interaction with Google Sheets
- tweepy - Twitter API wrapper that allows for Interaction with Twitter

### Technologies Utilized
***
- Python
- AWS ECR
- AWS Lambda
- AWS EventBridge
- AWS S3
- Docker Container
- Google Sheets API
- Twitter API

### The Script - app.py
***

### Problems Experienced
***
- BIGGEST PROBLEM: Dependencies Too Big. 264MB. Lambda Functions only upload zip files up to 50MB. Zip Files to S3 up to 250MB. Tried everything. 1 layer for all dependencies, 1 layer per dependency. Nothing worked and I was forced to go the Docker container route.
- M1 Macbook Architecture - x86/84
- Figuring Out How To Pull Google Credentials From S3 Bucket

### Understanding The Dockerfile - Dockerfile
***

### Building The Bot Docker Image And Storing It On AWS ECR - Command Line & AWS ECR
***

**Build**
- `docker build -t ect-container-name:latest .`

**Tag**
- `docker tag twitter_bot_lambda_func_container:latest 580708967395.dkr.ecr.us-east-2.amazonaws.com/twitter_bot_dkr_container:latest`

**Push(To AWS ECR)**
- `docker push 580708967395.dkr.ecr.us-east-2.amazonaws.com/twitter_bot_dkr_container:latest`

***

###  Deploying The Docker Image In An AWS Lambda Function - Command Line/AWS Lambda
***

### Automating Tweet Creation Via AWS EventBridge Scheduler - AWS EventBridge
***

### What's Next?
***
- Updating Image via CI/CD(Github Actions) every time the master branch is updated
- Convert to OOP
