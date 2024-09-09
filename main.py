import ollama
import feedparser
import chromadb
import time
rss_feed_link = "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
feed = feedparser.parse(rss_feed_link)
print('Fetching RSS feed data', end="")
for i in range(5):
    print('.', end="", flush=True)  # Show loading dots
print('\n')

print('Scanning news')
entries = feed.entries
documents = []
metadatas = []
ids = []

print('Processing news started', end=" ")
for entry in entries:
    print('.', end=" ", flush=True)
    title = entry.title
    link = entry.link
    content = entry.summary
    tags = ", ".join([t['term']for t in entry.tags])
    documents.append(f'#{title}\n @{content}\n')
    metadatas.append({"title":title,"link":link,"tags":tags})
    ids.append(link)  

print("Storing news")
client = chromadb.Client()
collection = client.get_or_create_collection('vector_collection')
collection.add(
    documents = documents,
    metadatas = metadatas,
    ids=ids
)
prompt = ''
while prompt != 'exit':
    prompt = input("Enter your context , Type 'exit' to exit :  ")
    if prompt == 'exit':
        print('Exiting', end=" ")
        for i in range(5):
            print('.', end=" ", flush=True)
            time.sleep(.1)
        break
    result = collection.query(
        query_texts = [prompt],
        n_results = 5
    )
    context = result['documents']
    query = input(f"Enter your query for context {prompt} :  ")
    response = ollama.chat(
        model='phi3',
        messages=[
            {
                "role":"system",
                "content":f"Answer the question on the news feed given here only.The news feed content is : \n\n  {context}\n\n"
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    print(response['message']['content'])

# response = ollama.generate(model='phi3',prompt='expalin quantam computing')
# print(response['response'])