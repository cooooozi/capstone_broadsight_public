# emailScraper


## Submitting a Pull Request 

When you've finished a task, please make a pull request and tag me or let me know. Please include the following headers in your pull request

*Summary of Change*

*Acceptance Criteria* <-- you can just copy paste from the task description below, it's essentially what this PR does

*How to Test It* <-- this is important, so I can run it myself and take a look

*Screenshots or Ouput* <-- Please show the output that the PR produces 


## Using API calls to run LLMs hosted on hugging face

I believe we should be able to run LLMs hosted on Huggingface. For now, please only use with the data in the cloud_safe folder. 

API token: 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

Dedicated instances, tuned for text summarization:
* meta-llama-3-8b-instruct: https://y8tol6394epbaxkw.us-east-1.aws.endpoints.huggingface.cloud
* meta-llama-3-8b: https://odou2kzqunj28l1j.eu-west-1.aws.endpoints.huggingface.cloud

Feel free to make more dedicated instances on HuggingFace, I think I invited you both to the account. Please don't spend more than $1/hour though, as I don't think we'll ever want to spend more than that in production. Please also configure it to shut down after 15 minutes of inactivity so to try to keep the costs contained. 

[Quicktour](https://huggingface.co/docs/api-inference/quicktour)

[In-depth](https://huggingface.co/docs/huggingface_hub/v0.14.1/en/guides/inference)

Example using llama 3 70B, with our api token
```
import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-70B"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
output = query({
	"inputs": "Can you please let us know more details about your ",
})
```



## Task 1

Please create a Python script that can take a .msg file (see examples in the .\data folder) and then outputs the sending
address, reicving address, subject line, and message body. 

The message body should be processed so that an LLM can take it in easily. I haven't opened a msg file so don't know 
what's in there, but you can take out any html/other code, take our URLs, take out images, etc. We should be left with 
just the text, such that we can then pass that to our LLM. 

While working on this, please make a branch. When you are done, make a pull request and tag me in it. Please provide, 
in the PR, an example of the outputs. 

Let me know if you have any questions! It would be great if you could do this in the next few days and I'll
get started on the next taxt. 

Please do not share any of the .msg files with anyone, they are confidential. 

## Task 2

Okay! Thank you both for the above. Now the real fun begins. 

I now want you to get started producing structured data (a JSON) from an email. 

This is a good guide doing so: Guide on [Email Extraction Using LLMs](https://docs.llamaindex.ai/en/stable/examples/usecases/email_data_extraction/)

HOWEVER, VERY IMPORTANT, WE DO NOT WANT TO USE THE OPENAI CALL! WE WANT TO INSTEAD RUN THE LLMs LOCALLY!

Again, do NOT send any data using the openai called - this sends the data to the cloud. 

Instead, you can use this [Guide on using local LLMs](https://docs.llamaindex.ai/en/stable/understanding/using_llms/using_llms/) or this one that specifically talks about [running locally](https://colab.research.google.com/drive/16QMQePkONNlDpgiltOi7oRQgmB8dU5fl?usp=sharing)

Please let me know if you have any questions. 

For now, for your JSON, you can just produce a JSON that has the sender, receiver, subject, and then a field called "requested task". We can refine it in later tasks. 

Let me know if you have any questions! Especially around not sending data to the cloud; it's important we keep stuff local. 

## Task 3 

As I kinda expected, it's been kinda hard to run LLMs locally. 

As such, please find an online provider we can use for iniital development (we'll eventually deploy with Amazon SageMaker)

You can try Kaggle, or there are probably other providers. You might even see if you can sign up for Amazon SageMaker for free 
for a student account or whatever. I can use our company card to pay for stuff. 

HOWEVER, if we're using cloud providers, it's important to NOT use any of the emails we already provided. 

Instead, we're going to use two of my own emails, and two forms that Kurt approved for sharing, now in the Safe to Use on Cloud folder:
* *jj_email_1.eml*
   - Our system should output a JSON as close as possible to jj_email_1_desired_output.txt but in a JSON
* *jj_email_2.eml*
   - --> jj_email_2_desired_extraction.txt
* *form_fill_1.txt*
   - --> form_fill_1_desired_extraction.txt
* *other_email_1.txt*
   - --> other_email_1_desired_extraction.txt
 
Once it is working for those 4, please make a PR, but also prepare a quick report (few pages) that introduces the task, how you've accomplished it, and please show the input/output. This should be somewhat none technical, and appropriate to show our CEO (who is not a programmer). You can use Word, Powerpoint, LaTeX, Google Doc/Slides, whatever you would like. 
