# load the necessary modules
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from dotenv import load_dotenv #hide your API keys! add .env to .gitignore

load_dotenv() 
#if you get an error, do `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

# note on google credentials: the directory is somewhat unpredictable. 
# although you can try placing the creds in the root directory, 
# I had to put mine in C:/Users/me/.credentials/credentials.json

# load the documents from a google drive folder
loader = GoogleDriveLoader(
    token_path='./token.json', #leave this alone
    folder_id= '1-sAD-TSBstS1IjbGPBXBqw2rCJpJcsnN', #copy from gdrive url
    recursive=False, # recursive=True will load all subfolders
    file_types=["sheet", "document", "pdf"] # "document" means google doc type, not .docx
)

docs = loader.load() 

# split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"])
texts = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(texts, embeddings)

retriever = db.as_retriever()
llm = ChatOpenAI(temperature=0, model_name="gpt-4-0613")
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

#Things to try:
# use a different chain type and custom prompt: https://python.langchain.com/docs/modules/chains/popular/vector_db_qa
# make it conversational: https://python.langchain.com/docs/modules/chains/popular/chat_vector_db

# run the QA model
while True:
    query = input("Ask a question >>> ")
    answer = qa.run(query)
    print(answer)