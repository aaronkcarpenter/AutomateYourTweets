import boto3
import gspread
import json
import random
import tweepy
from datetime import datetime
from gspread_formatting import *

d = datetime.now()
timeTweeted = d.strftime("%d/%m/%Y %H:%M:%S")

def lambda_handler(event, context):
    """Lambda function That automates tweet sending of a twitter bot."""
    google_sheets_authentication()

def getClientAWS():
    """
    This function is used to connect the bot to the correct
    Twitter account after getting the proper credentials
    from the AWS Parameter Store.
    
    Once authorized, the bot is ready to tweet.
    """
    auth_creds = get_twitter_keys()
    client = tweepy.Client(
                        bearer_token=auth_creds['bearer_token'], #1
                        consumer_key=auth_creds['consumer_key'], #2
                        consumer_secret=auth_creds['consumer_secret'], #4
                        access_token=auth_creds['access_token'], #0
                        access_token_secret=auth_creds['token_secret'],
                        wait_on_rate_limit=True
            )
    return client

def get_twitter_keys():
    """
    This function pulls the auth Tokens and Keys from AWS Systems Manager
    parameter store, which is needed for the bot to access Twitter.
    Retrieve secrets from Parameter Store.
    
    We connect to  aws via our boto package and once we have access,
    we take the needed k/v's from the store. To make access to the values
    simple, we store each of the keys in a dictionary that we ultimately
    pass to our Twitter client when attempting to create an automated tweet.
    """
    aws_client = boto3.client('ssm')

    parameters = aws_client.get_parameters(
        Names=[
            'bearer_token',
            'consumer_key',
            'consumer_secret',
            'access_token',
            'token_secret'
        ],
        WithDecryption=True
    )

    keys = {}
    for parameter in parameters['Parameters']:
        keys[parameter['Name']] = parameter['Value']
    return keys

def get_json_from_bucket():
    """
    We have our credentials for the Google API stored in a JSON file
    within S3. We first connect to AWS through the boto package, and
    once authorized, we get the json key/values after parsing the file.
    """
    aws_s3_client = boto3.resource('s3')
    json_bucket = 'twitter-bot-cloudformation'
    json_file_name = 'google_creds.json'
    obj = aws_s3_client.Object(json_bucket, json_file_name)
    data = obj.get()['Body'].read().decode('utf-8')
    json_data = json.loads(data)
    return json_data

def nextCellToTweet(sheet):
    """
    Starting from the last row checking the Google Sheet for the Next Cell To Get A Tweet From.
    """
    nextAvailableTweet = len(sheet.col_values(1))
    return random.randint(0, nextAvailableTweet)

def nextAvail(sheet):
    """
    Checking the Google Sheet for the Next Available Empty Cell To Enter USED Tweets Into.
    This is a new sheet that stores the already posted tweets, which covers the case of the bot 
    potentially tweeting duplicates since Tweets are removed from a cell after it has posted.
    """
    nextAvailableRow = len(sheet.col_values(1)) + 1
    return nextAvailableRow

def google_sheets_authentication():
    """
    Google sheets authentication is responsible for giving the Twitter Bot
    Access to the Google Sheets API. This is done by passing the sheets auth credentials
    as a dictionary to Google via a Service Account.
    """
    credential_info = get_json_from_bucket()
    gc = gspread.service_account_from_dict(credential_info)
    workbook = gc.open_by_key("16H1bvad7Xc7heosH9QvGclWli3OqhpJ_WYP5e-lR4gc")
    sheet = workbook.worksheet("MultipleFunnies")
    sheetToCopyUsedTweetTo = workbook.worksheet('AlreadyTweeted')
    nextTweet = nextCellToTweet(sheet)
    status = sheet.acell(f'B{nextTweet}').value
    badTweet = 'and copied to Already Tweeted'
    recycled_bad_tweet = badTweet in sheetToCopyUsedTweetTo.findall(badTweet)
    recycled_tweet = status in sheetToCopyUsedTweetTo.findall(status)
    
    while badTweet in status or recycled_tweet:
        print(status)
        nextTweet = nextCellToTweet(sheet)
        status = sheet.acell(f'B{nextTweet}').value
        print(status)
        
    try:
        send_tweet(status)
    except Exception as e:
        print(f'Problem Sending The Tweet {e}')
    
    nextEmptyRow = nextAvail(sheetToCopyUsedTweetTo)
    sheetToCopyUsedTweetTo.update(f"A{nextEmptyRow}", status)
    sheet.update(f'B{nextTweet}', f'Tweeted on {timeTweeted} and copied to Already Tweeted')
    
def send_tweet(status: str):
    twitter_client = getClientAWS()
    try:
        twitter_client.create_tweet(text=status)
        print('Tweet Successfully Sent', status)
    except Exception as e:
        print(f'Ran into an issue connecting to Twitter and Tweeting status.')
