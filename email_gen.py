# Import necessary libraries
from langchain_groq import ChatGroq
from langchain.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Access the Groq API Key from the .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file.")

# Set up the LLM (Groq with LLaMA 3)
llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile"
)


def generate_cold_email(url):
    """
    Scrapes machine learning internship details from Internshala using WebBaseLoader 
    and generates personalized cold emails.

    Returns:
        tuple: (cold_emails, metadata) where metadata contains company and role for each email.
    """
    try:
        # Step 1: Use WebBaseLoader to fetch page content
        loader = WebBaseLoader(url)
        docs = loader.load()

        # Step 2: Extract text content
        page_content = docs[0].page_content

        # Step 3: Preprocess Data (Keep only relevant content)
        # Clean up the page content: remove excessive whitespace but keep structure
        filtered_data = re.sub(r'\n+', '\n', page_content)  # Collapse multiple newlines into one
        filtered_data = re.sub(r'[ \t]+', ' ', filtered_data)  # Remove excessive spaces/tabs
        filtered_data = filtered_data.strip()


        # Step 4: Extract Job Details
        prompt_extract = PromptTemplate.from_template(
            """
            Extract all machine learning internships from the given text. 
            Present the data as a JSON array where each internship is an object containing these keys:
            - "company": Company offering the internship  
            - "role": Job title or role  
            - "location": Location of the internship (e.g., Work from home, Bangalore)  
            - "duration": Internship duration (e.g., 3 Months)  
            - "stipend": Stipend amount (e.g., ₹ 15,000 /month, Unpaid)  
            Only return the JSON. No explanations, no preamble, and no additional formatting.
            """
        )

        # Extract job details
        chain_extract = prompt_extract | llm
        result = chain_extract.invoke({"page_data": filtered_data})

        # Parse the Resulting JSON
        json_parser = JsonOutputParser()
        job_details = json_parser.parse(result.content)

        # Step 5: Generate Cold Emails for each internship
        cold_emails = []
        metadata = []  # Store company and role info

        prompt_email = PromptTemplate.from_template(
            """
            Write a formal and personalized cold email for applying to the '{role}' position at '{company}'.
            Mention the location as '{location}' and internship duration as '{duration}', but do not mention the stipend.
            Ensure the tone is polite, concise, and enthusiastic while remaining professional. 
            Conclude by stating that links to the applicant's work and portfolio are attached with the email. 
            Return only the email content, no extra text or preamble.
            """
        )

        chain_email = prompt_email | llm

        for job in job_details:
            email_result = chain_email.invoke(job)
            cold_emails.append(email_result.content.strip())
            metadata.append({"company": job["company"], "role": job["role"]})

        return cold_emails, metadata

    except Exception as e:
        print(f"Error: {e}")
        return [], []
