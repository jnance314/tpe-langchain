# load the necessary modules
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# add the api keys!
# ------

# load the documents from a google drive folder
folder_id = "YOUR_FOLDER_ID"
loader = GoogleDriveLoader(folder_id=folder_id, recursive=False) # recursive=True will load all subfolders
docs = loader.load() 

# split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"])

# create the retriever
texts = text_splitter.split_documents(docs)
embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(texts, embeddings)
retriever = db.as_retriever()
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# create the QA model
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

# for fun, you can try a different chain type and custom prompt: https://python.langchain.com/docs/modules/chains/popular/vector_db_qa
# make it conversational: https://python.langchain.com/docs/modules/chains/popular/chat_vector_db

# run the QA model
while True:
    query = input("My query: What's the purpose of the program?")
    answer = qa.run(query)
    print(answer)