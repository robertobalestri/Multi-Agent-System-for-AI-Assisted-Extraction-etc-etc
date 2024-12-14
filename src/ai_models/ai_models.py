from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv
import os
from enum import Enum


try:
    from src.utils.logger_utils import setup_logging
    load_dotenv(override=True)

    # Set up logging
    logger = setup_logging(__name__)
except:
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    load_dotenv(override=True)



# Global variables to store LLM instances
_intelligent_llm = None
_cheap_llm = None

#define enum for LLM types
class LLMType(Enum):
    INTELLIGENT = "intelligent"
    CHEAP = "cheap"

def _initialize_llm(intelligent_or_cheap: LLMType) -> AzureChatOpenAI:
    """
    Initialize and return an instance of AzureChatOpenAI LLM.

    Args:
        intelligent_or_cheap (str): Specify whether to initialize the 'intelligent' or 'cheap' LLM.

    Returns:
        AzureChatOpenAI: An instance of the AzureChatOpenAI LLM.
    """
    try:
        if intelligent_or_cheap == LLMType.INTELLIGENT:
            return AzureChatOpenAI(
                deployment_name=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME_INTELLIGENT"),
                model=os.getenv("AZURE_OPENAI_LLM_MODEL_NAME_INTELLIGENT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                temperature=0.2,
            )
        elif intelligent_or_cheap == LLMType.CHEAP:
            return AzureChatOpenAI(
                deployment_name=os.getenv("AZURE_OPENAI_LLM_DEPLOYMENT_NAME_CHEAP"),
                model=os.getenv("AZURE_OPENAI_LLM_MODEL_NAME_CHEAP"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.getenv("AZURE_OPENAI_API_ENDPOINT"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                temperature=0.2,
            )
        else:
            raise ValueError(f"Invalid LLM type: {intelligent_or_cheap}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise

def get_llm(intelligent_or_cheap: LLMType) -> AzureChatOpenAI:
    """
    Get the initialized LLM instance. If not initialized, initialize it first.

    Args:
        intelligent_or_cheap (LLMType): Specify whether to get the 'intelligent' or 'cheap' LLM.

    Returns:
        AzureChatOpenAI: An instance of the AzureChatOpenAI LLM.
    """
    global _intelligent_llm, _cheap_llm


    #Metti tutto cheap per i test
    if os.getenv("ONLY_CHEAP_LLM") == "true":
        intelligent_or_cheap = LLMType.CHEAP


    if intelligent_or_cheap == LLMType.INTELLIGENT:
        if _intelligent_llm is None:
            _intelligent_llm = _initialize_llm(LLMType.INTELLIGENT)
        return _intelligent_llm
    elif intelligent_or_cheap == LLMType.CHEAP:
        if _cheap_llm is None:
            _cheap_llm = _initialize_llm(LLMType.CHEAP)
        return _cheap_llm
    else:
        raise ValueError(f"Invalid LLM type: {intelligent_or_cheap}")

def get_embedding_model():
    return CohereEmbeddings(
        model="Cohere-embed-v3-english",
        cohere_api_key=os.getenv("AZURE_COHERE_EMBEDDING_API_KEY"),
        base_url=os.getenv("AZURE_COHERE_EMBEDDING_API_ENDPOINT"),
    )
    
    
def test_llm():
    llm = get_llm(LLMType.CHEAP)
    print(llm)
    print(llm.invoke("Hello, how are you?"))


def test_embedding():
    embedding = get_embedding_model()
    print(embedding.embed_query("Hello, how are you?"))
    
if __name__ == "__main__":
    #test_llm()
    test_embedding()