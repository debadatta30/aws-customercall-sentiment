# aws-customercall-sentiment
Customer phone call sentiment analysis using Amazon Bedrock
This code takes customer call as an audio file as an input , convert the phonecall to text transcript using Amazon Transcribe. Then it use Amazon Bedrock with a Foundation Model to analyse the sentiment using a predefined prompt tempalate which will be updated with the actual data in the runtime of the code and the output will be written to S3 Bucket. The architecture of the solution is shown below : 

![image](https://github.com/user-attachments/assets/3ccb7109-1c74-4f19-a0bb-9b8752f9715f)

The flow of the solution :
1. Cusomer call uploaded to Amazon S3
2. Amazon S3 Event invokes AWS Lambda
3. The  AWS Lambda Function convert the phone call to transcrit with lebels
4. AWS Lambda invokes reads the S3 file for call Transcript and use predefined prompt with Jinja to create the final prompt with the context data
5. AWS Lambda invoke Amazon Bedrock using Amazon titan-text-express-v1 model to do the sentiment analysis of the call recording
6. AWS Lambda store output in Amazon S3.

You Need to enable the Model Access, You can use the Amazon Bedrock console by selecting the Model Access option as shown in the below screen:
![image](https://github.com/user-attachments/assets/2b9ae30b-7baf-460c-a51e-9cf3363361fa)

The code contains the cloudformation templates which will create the S3Bucket and event notication on file upload of call recording mp3 , you can extend to other files with the suffix option a, Lambda Role and AWS Lambda Function which will process the file from S3 and put the transcript out to the S3Bucket and further uses Amazon Bedrock with Amazon titan-text-express-v1 model to do the sentiment analysis.

The AWS Lambda code is written in Python and the source code is available in the Python folder , this is pacakaged as a zip packagae with the dependency. The code uses boto3 and jinja2 template to create the prompt using the user feedbcak and prompt template.Python folder contain the Lambdacode in the file named lambda_function.py . If you cahnge the source code you can create the zip package , the directory is named python . Navigate to the Project directory cd Python

Create a new directory named package install the Jinja2 & boto3  dependency mkdir package , pip install --target ./package Jinja2 , pip install --target ./package boto3

Create a .zip file with the installed libraries at the root project cd package zip -r ../my_deployment_package.zip .

Add the lambda_function.py file to the root of the .zip file cd .. zip my_deployment_package.zip lambda_function.py

Upload the .zip package to the S3 Bucket and pass the reference to the cloudformation template , cloudformation template will create the lambda function from the zip pacakge.

Upload Template Files from the cfn folder to S3 Bucket:

aws s3 cp . s3://my-bucket/cfntemplate.yaml/ --recursive

CloudFormation Stack Creation:

aws cloudformation create-stack --stack-name reviewSummarize --template-url https://my-bucket.s3.region.amazonaws.com/ReviewSummarize/cfntemplate.yaml --capabilities CAPABILITY_NAMED_IAM



