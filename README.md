# Modal Docs Bot

A Chat bot built on top of OpenAI and Pinecone to provide a chat interface with the docs of Modal Labs. 

# Process

* Scraped data from Modal Labs' documentation (https://modal.com/docs/examples) using an Apify actor: https://apify.com/apify/website-content-crawler

* Used this data to create a text file for each url.

* Added each text file to a Pinecone vector database using the Canopy CLI: https://github.com/pinecone-io/canopy
