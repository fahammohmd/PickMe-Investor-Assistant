# PickMe Investor Assistant

## Project Overview

This project is a Python-based chatbot application named "PickMe Investor Assistant". It's designed to answer questions about documents related to "PickMe" and assist with investment research and decision-making. The application uses a Retrieval-Augmented Generation (RAG) architecture and provides additional tools for valuation, stock analysis, and portfolio optimization.

The core technologies used are:
-   **Streamlit:** For building the interactive web-based chat interface and other analytical tools.
-   **LlamaIndex:** As the data framework for building the RAG pipeline. It handles data loading, indexing, and querying.
-   **Google Gemini:**
    *   The `gemini-2.5-flash` model is used as the Language Model (LLM) for the main chatbot in the "PickMe AI Assistant" page.
    *   The `gemini-2.0-flash` model is used for generating interpretations on the "Valuation", "Stock Analysis", and "Portfolio Optimization" pages. (Note: The code uses `gemini-2.5-flash` for the LLM. If you want to change it to `gemini-pro`, you would need to modify `src/chatbot.py`.)
-   **HuggingFace Embeddings:** The `all-MiniLM-L6-v2` model is used to generate embeddings for the documents and user queries.
-   **Pandas, NumPy, Plotly, Matplotlib, SciPy:** For data analysis, visualization, and scientific computing in the valuation, stock analysis, and portfolio optimization sections.
-   **python-docx, docx2txt:** For reading `.docx` documents.

The application works by:
1.  Loading documents from the `Data/` directory.
2.  Creating a vector index of the documents and storing it in the `storage/` directory for persistence. The index is automatically rebuilt if the data in `Data/` changes.
3.  When a user asks a question via the "PickMe AI Assistant", the application queries the index to find relevant document chunks.
4.  The retrieved context and the user's question are then passed to the Gemini LLM to generate a conversational answer.
5.  Other pages (Valuation, Stock Analysis, Portfolio Optimization) provide tools for financial analysis and visualization.

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
    This will start a local web server, and you can interact with the chatbot in your browser. The first time you run it, it will create and save the document index, which might take a few moments depending on the amount of data in the `Data/` directory.

## Development Conventions

*   **Code Structure:** The main application logic is separated into different modules:
    *   `app.py`: The main Streamlit application file that handles the overall page configuration and introduces the application.
    *   `Home.py`: The home page of the Streamlit application.
    *   `pages/`: Contains separate Python files for each distinct page or feature of the Streamlit application (e.g., AI Assistant, Valuation, Stock Analysis, Portfolio Optimization).
    *   `src/`: Contains core backend logic:
        *   `src/chatbot.py`: Contains the logic for setting up the LlamaIndex chat engine and configuring the Gemini LLM.
        *   `src/data_loader.py`: Manages loading documents from the `Data/` directory, creating, and persisting the vector index. It includes logic to rebuild the index only when data changes.
        *   `src/data_utils.py`: (Assumed) Contains utility functions for data processing or manipulation.
        *   `src/valuation_logic.py`: (Assumed) Contains the business logic for the valuation page.
*   **Data:** All source documents for the chatbot (e.g., research reports, investment theses) should be placed in the `Data/` directory. The `data_loader.py` script will recursively read files from this directory.
*   **Indexing:** The LlamaIndex vector index is stored and persisted in the `storage/` directory. If you want to force a re-index of the data (e.g., after adding new documents and the automatic hashing mechanism doesn't trigger a rebuild, or for debugging), you can delete this `storage/` directory. The application will automatically create a new index the next time it starts.
*   **Dependencies:** Project dependencies are managed in the `requirements.txt` file. If you add new libraries, make sure to add them to this file.
*   **Environment Variables:** Sensitive information like API keys are managed via a `.env` file at the project root.
