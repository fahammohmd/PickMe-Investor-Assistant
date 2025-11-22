import os
import hashlib
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import shutil

# Directory where the data is stored
DATA_DIR = "Data"
# Directory where the index is stored
STORAGE_DIR = "storage"

def get_data_hash():
    """
    Calculates a hash based on the contents of the DATA_DIR.
    The hash is based on filenames, modification times, and file sizes.
    """
    hasher = hashlib.md5()
    files = []
    for root, _, filenames in os.walk(DATA_DIR):
        for fn in sorted(filenames):
            if fn.startswith('.'): # Ignore hidden files like .DS_Store
                continue
            path = os.path.join(root, fn)
            files.append(path)

    if not files:
        return None

    for path in sorted(files):
        # Add filename, modification time, and size to the hash
        file_stat = os.stat(path)
        hasher.update(path.encode())
        hasher.update(str(file_stat.st_mtime).encode())
        hasher.update(str(file_stat.st_size).encode())

    return hasher.hexdigest()

def get_index(model_name="all-MiniLM-L6-v2"):
    """
    Loads or creates a LlamaIndex VectorStoreIndex with a HuggingFace embedding.
    The index is automatically rebuilt if the contents of the Data directory change.
    """
    # Initialize embedding model
    embed_model = HuggingFaceEmbedding(model_name=model_name)
    Settings.embed_model = embed_model # Set the embed_model in settings

    hash_path = os.path.join(STORAGE_DIR, "data_hash.txt")
    current_hash = get_data_hash()
    
    # Check if a valid index and hash file exist
    if os.path.exists(hash_path):
        with open(hash_path, "r") as f:
            stored_hash = f.read()
        if stored_hash == current_hash:
            print(f"Data has not changed. Loading existing index from '{STORAGE_DIR}'.")
            storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
            index = load_index_from_storage(storage_context)
            print("Index loaded successfully.")
            return index

    print("Data has changed or index is not found. Rebuilding index.")
    
    # If hashes differ or no hash is stored, rebuild
    if os.path.exists(STORAGE_DIR):
        shutil.rmtree(STORAGE_DIR) # Clean up old index
    os.makedirs(STORAGE_DIR)
    
    # Load the documents from the data directory
    try:
        documents = SimpleDirectoryReader(DATA_DIR, recursive=True).load_data()
    except ValueError:
        print(f"No readable files found in '{DATA_DIR}'.")
        return None # Return None if no documents are found
    
    if not documents:
        print(f"No documents were loaded from '{DATA_DIR}'.")
        return None

    # Create the index from the documents
    index = VectorStoreIndex.from_documents(documents)
    
    # Persist the index and the new hash to disk
    index.storage_context.persist(persist_dir=STORAGE_DIR)
    with open(hash_path, "w") as f:
        f.write(current_hash)
    print("Index rebuilt and persisted.")
        
    return index