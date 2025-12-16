from llama_index.llms.openai import OpenAI

from .config import settings

if settings.enable_langfuse:
    from langfuse.openai import OpenAI as OpenAIClient
else:
    from openai import OpenAI as OpenAIClient

openai_client = OpenAIClient(api_key=settings.openai_api_key, max_retries=settings.openai_max_retries)
llm = OpenAI(
    client=openai_client,
    model=settings.default_llm,
    temperature=settings.llm_temperature,
    max_retries=settings.openai_max_retries,
)
