import boto3 # invoke foundational services
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic:str)->str:
    prompt=f"""<s>[INST]Human: Write a 200 words blog on the topic of {blogtopic}</s>
    Assistant:[/INST]    
    """
    
    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }
    
    try:
        bedrock=boto3.client("bedrock-runtime",region_name="us-east-1",
                             config=botocore.config.Config(retries={"max_attempts":0},read_timeout=300))
        response=bedrock.invoke_model(body=json.dumps(body),modelId="meta.llama2-13b-chat-v1")
        response_content = response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error generating the blog: {e}")
        return "Error generating the blog"
 
def save_blog_to_s3(s3_key,s3_bucket,generate_blog):
    s3=boto3.client("s3")
    try:
        s3.put_object(Body=blog_details,Bucket=s3_bucket,Key=s3_key)
        print("code saved to s3")
    except Exception as e:
        print("Error while saving the code to s3")
        
def lambda_handler(event, context):
    # TODO implement
    event=json.loads(event['body'])
    blogtopic=event["blog_topic"]
    generate_blog=blog_generate_using_bedrock(blogtopic=blogtopic)
    if generate_blog:
        current_time=datetime.now().strftime("%H:%M:%S")
        s3_key=f"blog-output/{current_time}.txt"
        s3_bucket='aws_bedrock_blogs1'
        save_blog_details_s3(s3_key,s3_bucket,generate_blog)
    else:
        print("No blog was generated")
    return {
        'statusCode': 200,
        'body': json.dumps('Blog generated successfully!')
    }
