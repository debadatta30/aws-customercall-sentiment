import os
import boto3
import uuid
import time
import json
from jinja2 import Template

# Env variables from  CFN 
bucket_name = os.environ['SOURCEBUCKET']
key = os.environ['SOURCEFILE']


def lambda_handler(event, context):

    print(json.dumps(event))
    
    record = event['Records'][0]
    
    s3bucket = record['s3']['bucket']['name']
    s3object = record['s3']['object']['key']
    
    s3Path = f's3://{s3bucket}/{s3object}'
    jobName = f'{s3object}--{str(uuid.uuid4())}'
    outputKey = f'transcripts/{s3object}-transcript.json'
    
    transcribe_client = boto3.client('transcribe')
    
    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=jobName,
        LanguageCode='en-US',
        Media={'MediaFileUri': s3Path},
        OutputBucketName=s3bucket,
        OutputKey=outputKey,
        Settings={
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': 2
        }
    )
    
    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=jobName)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(2)
    print(status['TranscriptionJob']['TranscriptionJobStatus'])
    
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        
        # Load the transcript from S3.
        transcript_key = f"{jobName}.json"
        transcript_obj = s3_client.get_object(Bucket=s3bucket, Key=outputKey)
        transcript_text = transcript_obj['Body'].read().decode('utf-8')
        transcript_json = json.loads(transcript_text)
        
        output_text = ""
        current_speaker = None
        
        items = transcript_json['results']['items']
        
        for item in items:
            
            speaker_label = item.get('speaker_label', None)
            content = item['alternatives'][0]['content']
            
            # Start the line with the speaker label:
            if speaker_label is not None and speaker_label != current_speaker:
                current_speaker = speaker_label
                output_text += f"\n{current_speaker}: "
                
            # Add the speech content:
            if item['type'] == 'punctuation':
                output_text = output_text.rstrip()
                
            output_text += f"{content} "
            
        # Save the transcript to a text file
        with open(f'{jobName}.txt', 'w') as f:
            f.write(output_text)
            
    #Sentiment Analysis Code 
    s3_client = boto3.client('s3')
    bedrock_runtime = boto3.client('bedrock-runtime', 'us-east-1')
    prompt_content = ""
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    prompt_content = response['Body'].read().decode('utf-8')
    data = {
        'feedback' : output_text
    }
    template = Template(prompt_content)
    prompt = template.render(data)

    config = {
        "modelId": "amazon.titan-text-express-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                "maxTokenCount": 500,
                "temperature": 0,
                "topP": 0.9
            }
        }
        )
    }
    response = bedrock_runtime.invoke_model(**config)
    summarize = json.loads(response.get('body').read()).get('results')[0].get('outputText')
    
    #Write the ouytput to the Bucket 
    Keyresult = 'output.txt'
    s3_client.put_object(
        Bucket=bucket_name,
        Key=Keyresult,
        Body=summarize,
        ContentType='text/plain'
    )
    
    print (json.dumps(response, default=str))
    
    return {
        'statusCode': 200
    }