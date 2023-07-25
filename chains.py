from langchain.llms import OpenAI
from langchain.chains import LLMRequestsChain, LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain.document_loaders import Docx2txtLoader
# from langchain.chains import SimpleSequentialChain
load_dotenv()

# This program does the following:
# scrapes a job description from linkedin, summarizes the most important core requirements
# loads your resume as a docx file
# compares your resume to the job description and highlights your top defficency with respect to the job description
# recommends a hypothetical skill workshop that would bridge the skill gap
# returns free upcoming workshops addressing that skill on eventbrite

#specify a job description url
jd_url = "https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3603193583"

#specify the LLM base you want to use
llm = OpenAI(temperature=0)

# load the resume
loader = Docx2txtLoader("resume.docx")
resume_doc = loader.load()
resume_text = resume_doc[0].page_content

# scrape linkedin for the job description, summarize it
jd_template = """
Between >>> and <<< is the raw HTML content of a Linkedin web page.
Somewhere in the web page is a job description. 
The job description starts with: 
<h2 class="text-heading-large mb4"> About the job</h2>

The job description ends at the element: <div class="jobs-description__details"><!----></div>
        
Extract the job description and summarize all of its essential requrements, skills, expectations, and responsibilities into a concise set of bullet points.
All information and nuances in the job description should be reflected in the set of bullet points.

>>> {requests_result} <<<

Summary of job description and requirements:
"""
jd_prompt = PromptTemplate(input_variables=["requests_result"], template=jd_template)
jd_chain = LLMRequestsChain(llm_chain=LLMChain(llm=llm, prompt=jd_prompt))
jd_inputs = {
    "url": jd_url
}
jd_response = jd_chain(jd_inputs)['output']
#print(jd_response)


# compare the resume to the job description and highlight the top defficency
eval_template = """
You are a professional development coach. Your client wants to be competitive when applying for a job with 
the following job description: {jd_summary}.

Here is their resume: {resume}.

It is your job to compare the client's resume to the job description and identify the candidate's most critical defficency
with respect to what the job description is asking for.

For example, you could format your description of the deficiency like this: "Lack of Product Management Experience: The job description requires a candidate who has experience 
in product management, particularly in driving product initiatives from inception through execution, defining features, writing product 
specifications, and shipping products/features. Your resume shows you have solid experience as a software developer, but it doesn't 
showcase any direct product management experience."

Skill defficency:
"""
eval_prompt = PromptTemplate(input_variables=["jd_summary", "resume"], template=eval_template)
eval_chain = LLMChain(llm=llm, prompt=eval_prompt)
eval_inputs = {
    "jd_summary": jd_response,
    "resume": resume_text
}
eval_result = eval_chain(eval_inputs)['text']
#print(eval_result)


# come up with a descriptive title of a hypothetical skill workshop that would bridge the skill gap.
title_template = """
You are a professional development coach. Your client has a skill deficiency which is described as: {deficiency}. 
Given the skill gap, it is your job to come up with a descriptive title of a hypothetical skill workshop that the client should attend
in order to bridge the skill gap. Don't be creative, be precise. 

For example, if the skill gap is described as "Lack of Product Management Experience: The job description requires a candidate who has experience 
in product management, particularly in driving product initiatives from inception through execution, defining features, writing product 
specifications, and shipping products/features. Your resume shows you have solid experience as a software developer, but it doesn't 
showcase any direct product management experience." then the title of the hypothetical skill workshop could be "Product Management for Software Developers".
Do not use special characters in the title.

Workshop title:
"""
title_prompt = PromptTemplate(input_variables=["deficiency"], template=title_template)
title_chain = LLMChain(llm=llm, prompt=title_prompt)
title_inputs = {
    "deficiency": eval_result
}
title_result = title_chain(title_inputs)['text']
#print(title_result)


# search eventbrite for free upcoming workshops on that skill
events_template = """
Between >>> and <<< is the raw HTML content of a web page.
The web page is a list of online workshops for professional skill building. 
An example of the format of a workshop listing in the page is: 
                <script type="application/ld+json">
            {{"startDate":"2023-07-25","endDate":"2023-07-25","name":"Free Intro to Product Management (PM) Workshop","url":"https://www.eventbrite.sg/e/free-intro-to-product-management-pm-workshop-tickets-401916060757","image":"https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F335092879%2F470836894629%2F1%2Foriginal.20220814-130634?w=512\u0026auto=format%2Ccompress\u0026q=75\u0026sharp=10\u0026rect=0%2C0%2C2160%2C1080\u0026s=a153d6ea43aae8c85e6c03cff9a9f3c5","offers":{{"url":"https://www.eventbrite.sg/e/free-intro-to-product-management-pm-workshop-tickets-401916060757","lowPrice":"0.00","highPrice":"0.00","@type":"AggregateOffer","priceCurrency":""}},"location":{{"url":"https://www.eventbrite.sg/e/free-intro-to-product-management-pm-workshop-tickets-401916060757","@type":"VirtualLocation"}},"eventAttendanceMode":"https://schema.org/OnlineEventAttendanceMode","@context":"http://schema.org","@type":"Event","description":"Learn the fundamentals of PM  by joining CuriousCore's Free Intro to Product Management (PM) Workshop conducted by our founder Daylon Soh"}}
        </script>
        
Extract the first three workshop names, their start dates, and their URLs.

>>> {requests_result} <<<

Extracted:
"""
events_prompt = PromptTemplate(input_variables=["requests_result"],template=events_template)
events_chain = LLMRequestsChain(llm_chain=LLMChain(llm=llm, prompt=events_prompt))
title = title_result
inputs = {
    "url": "https://www.eventbrite.com/d/online/free--events/" +title.replace(" ", "-")+ "/?page=1"   
}
events_result = events_chain(inputs)['output']

# List the workshops and thier links to sign up
print(events_result)