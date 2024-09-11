# aws-customercall-sentiment
Customer phone call sentiment analysis using Amazon Bedrock
This code takes customer call as an audio file as an input , convert the phonecall to text transcript using Amazon Transcribe. Then it use Amazon Bedrock with a Foundation Model to analyse the sentiment using a predefined prompt tempalate which will be updated with the actual data in the runtime of the code and the output will be written to S3 Bucket. The architecture of the solution is shown below : 

![image](https://github.com/user-attachments/assets/3ccb7109-1c74-4f19-a0bb-9b8752f9715f)

The flow of the solution :
1. Cusomer call uploaded to Amazon S3
2. S3 Event invokes AWS Lambda
3. The Lambda Function convert the phone call to transcrit with lebels
4. Lambda invokes reads the S3 file for call Transcript and use predefined prompt with Jinja to create the final prompt with the context data
5. Invoke Amazon Bedrock and LLM to do the sentiment analysis of the call recording
