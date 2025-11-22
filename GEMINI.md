# GEMINI.md

## Project Overview

This project is a Python-based chatbot application named "PickMe Investor Assistant". It's designed to answer questions about documents related to "PickMe". The application uses a Retrieval-Augmented Generation (RAG) architecture.

The core technologies used are:
- **Streamlit:** For building the interactive web-based chat interface.
- **LlamaIndex:** As the data framework for building the RAG pipeline. It handles data loading, indexing, and querying.
- **Google Gemini:** The `gemini-2.5-flash` model is used as the Language Model (LLM) for generating responses.
- **HuggingFace Embeddings:** The `all-MiniLM-L6-v2` model is used to generate embeddings for the documents and user queries.

The application works by:
1. Loading documents from the `Data/` directory.
2. Creating a vector index of the documents and storing it in the `storage/` directory for persistence.
3. When a user asks a question, the application queries the index to find relevant document chunks.
4. The retrieved context and the user's question are then passed to the Gemini LLM to generate a conversational answer.

## Building and Running the Project

To run this application, follow these steps:

1.  **Install Dependencies:**
    Make sure you have Python installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Up Environment Variables:**
    The application requires a Google API key to use the Gemini model. Create a file named `.env` in the root of the project and add your API key like this:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

3.  **Run the Application:**
    Once the dependencies are installed and the environment variable is set, you can run the Streamlit application with the following command:
    ```bash
    streamlit run app.py
    ```
    This will start a local web server, and you can interact with the chatbot in your browser. The first time you run it, it will create and save the document index, which might take a few moments.

## Development Conventions

*   **Code Structure:** The main application logic is separated into different modules within the `src/` directory:
    *   `app.py`: The main Streamlit application file that handles the user interface.
    *   `src/chatbot.py`: Contains the logic for setting up the LlamaIndex chat engine and configuring the Gemini LLM.
    *   `src/data_loader.py`: Manages loading documents, creating, and persisting the vector index.
*   **Data:** All source documents for the chatbot should be placed in the `Data/` directory. The `data_loader.py` script will recursively read files from this directory.
*   **Indexing:** The vector index is stored in the `storage/` directory. If you want to re-index the data (e.g., after adding new documents), you can delete this directory. The application will automatically create a new index the next time it starts.
*   **Dependencies:** Project dependencies are managed in the `requirements.txt` file. If you add new libraries, make sure to add them to this file.
