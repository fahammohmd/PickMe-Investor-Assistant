import os
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Directory where the data is stored
DATA_DIR = "Data"
# Directory where the index is stored
STORAGE_DIR = "storage"

def get_index(model_name="all-MiniLM-L6-v2"):
    """
    Loads or creates a LlamaIndex VectorStoreIndex with a HuggingFace embedding.

    Args:
        model_name (str): HuggingFace model name for embeddings.

    Returns:
        VectorStoreIndex: The loaded or newly created index.
    """
    # Initialize embedding model
    embed_model = HuggingFaceEmbedding(model_name=model_name)

    if not os.path.exists(STORAGE_DIR):
        print(f"Storage directory '{STORAGE_DIR}' not found. Creating a new index.")
        os.makedirs(STORAGE_DIR)
        
        # Load the documents from the data directory (search subfolders)
        try:
            documents = SimpleDirectoryReader(DATA_DIR, recursive=True).load_data()
        except ValueError as e:
            # More helpful error for the common "no files" case
            files = []
            for root, _, filenames in os.walk(DATA_DIR):
                for fn in filenames:
                    files.append(os.path.join(root, fn))
            print(f"No readable files found in '{DATA_DIR}'. Found: {files}")
            raise
        
        # Create the index from the documents using the HuggingFace embedder
        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        
        # Persist the index to disk
        index.storage_context.persist(persist_dir=STORAGE_DIR)
        print("Index created and persisted.")
    else:
        print(f"Loading index from '{STORAGE_DIR}'.")
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        # Load the existing index using the same embedder
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        print("Index loaded successfully.")
        
    return index
