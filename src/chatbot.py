import os
from dotenv import load_dotenv
from llama_index.llms.gemini import Gemini
from llama_index.core.settings import Settings
from src.data_loader import get_index

# Load environment variables from .env file
load_dotenv()

def get_chat_engine():
    """
    Initializes and returns a LlamaIndex chat engine configured with the Gemini LLM.

    This function performs the following steps:
    1. Loads the Google API key from the environment variables.
    2. Sets up the Gemini LLM with the specified model ("models/gemini-pro").
    3. Configures the LlamaIndex settings to use the Gemini LLM.
    4. Retrieves the vector store index using the get_index() function.
    5. Creates and returns a chat engine from the index.

    Returns:
        QueryEngine: The initialized chat engine.
    """
    # Check if the Google API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Google API key not found. Please set it in the .env file.")

    # Set up the LLM
    llm = Gemini(model="models/gemini-2.5-flash")

    # Configure LlamaIndex settings
    Settings.llm = llm
    Settings.chunk_size = 512
    Settings.chunk_overlap = 20

    # Get the index
    index = get_index()
    # Create a chat/query engine. Different llama-index versions expose
    # different APIs, so adapt at runtime and return a small adapter
    # that guarantees a `stream_chat(prompt)` method returning an
    # object with a `response_gen` iterable (what `app.py` expects).
    engine = None
    try:
        engine = index.as_chat_engine(streaming=True)
    except Exception:
        try:
            engine = index.as_query_engine(streaming=True)
        except Exception:
            engine = index.as_query_engine()

    class ChatEngineAdapter:
        def __init__(self, engine):
            self._engine = engine

        def stream_chat(self, prompt):
            # If the underlying engine already supports stream_chat, use it.
            if hasattr(self._engine, "stream_chat"):
                return self._engine.stream_chat(prompt)

            # Try query with common streaming kwargs.
            for kw in ("streaming", "stream", "stream_mode"):
                try:
                    resp = self._engine.query(prompt, **{kw: True})
                    break
                except TypeError:
                    continue
                except Exception:
                    # If the engine raised a runtime error, fall back below.
                    resp = None
                    break
            else:
                # No streaming support: perform a normal query.
                resp = self._engine.query(prompt)

            # Normalize response to have `response_gen`.
            if hasattr(resp, "response_gen"):
                return resp

            # If response has `response` or `text`, yield that as single token.
            text = None
            if hasattr(resp, "response"):
                text = resp.response
            elif hasattr(resp, "text"):
                text = resp.text
            elif isinstance(resp, str):
                text = resp
            else:
                text = str(resp)

            class _SingleResp:
                def __init__(self, t):
                    self.response_gen = iter([t])

            return _SingleResp(text)

    return ChatEngineAdapter(engine)
