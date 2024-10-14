import pdfplumber
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
import os
import environ

env = environ.Env()
environ.Env.read_env()

# Function to extract text from resume PDF
def extract_pdf_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to setup Langchain and handle RAG
def initialize_langchain():
    # Path to your resume PDF (adjust as per your file location)
    resume_pdf_path = os.path.join(os.getcwd(), 'portfolio/static/resume', 'Samir_Tak-Resume.pdf')
    # resume_pdf_path = os.path.join(os.getcwd(), 'static/resume', 'Samir_Tak-Resume.pdf')
    
    # Extract text from the resume PDF
    resume_text = extract_pdf_text(resume_pdf_path)

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    texts = text_splitter.split_text(resume_text)

    # Initialize OpenAI API key
    openai_api_key = env("openai_api_key")

    # Create embeddings and initialize FAISS
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    db = FAISS.from_texts(texts, embeddings)

    # Create a retriever
    retriever = db.as_retriever()

    # Initialize OpenAI LLM
    llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)

    # Set up RetrievalQA chain with the retriever and LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever()
    )

    return qa_chain

# Function to get a response based on user query
def get_response_from_langchain(user_message, history, time_remaining):
    # Initialize the QA chain only once (or implement a singleton pattern)
    user_messages = [entry for entry in history if entry['type'] == 'user']
    if len(user_messages) > 10 and not time_remaining:
        # Default reply if too many user queries have been sent
        return (
            "It seems like you've been asking a lot of questions! Please note that processing each query "
            "uses resources, including GPU power. Let's try to keep it concise. Contact me if you have more queries, or let's talk again tomorrow?"
        )

    qa_chain = initialize_langchain()
    # Define the initial system message
    system_prompt = (
        "You are Samir Tak, and your Resume is provided to the user. "
        "Answer accordingly and shortly as well as positively and solely related to the resume. "
        "You can also take reference from my projects repositories here if required: https://github.com/sameertak?tab=repositories"
        "Apart from this, you can also consider my portolio for related questions: https://samir31.pythonanywhere.com/"
        "Do not consider any other information."
    )

    formatted_history = "\n".join(
        [f"{entry['type'].capitalize()}: {entry['text']}" for entry in history]
    )

    # Concatenate system prompt with chat history and user message
    # full_query = (
    #     f"{system_prompt}\n\nChat History:\n{formatted_history}\n\nUser's new question: {user_message}"
    # )

    # # Concatenate system prompt with user message
    full_query = f"{system_prompt}\nUser's question: {user_message}"

    # Get the response from the QA chain using invoke
    response = qa_chain.invoke({"query": full_query})
    answer = response.get("result", "No response")  # Default to "No response" if the key doesn't exist

    return answer

