# gpt_model.py

import time
import os
import logging
from typing import Any, Dict, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv
from openai._types import NOT_GIVEN, NotGiven
from pydantic import BaseModel

logger = logging.getLogger(__name__)
load_dotenv(override=True)

class GPTModel:
    """
    Manages interactions with the GPT model (Azure OpenAI).
    """

    def __init__(self):
        """
        Initializes the GPTModel with Azure OpenAI client.
        """
        #logger.debug("Initializing GPTModel with AzureOpenAI client.")
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview",
        )

    def generate_response(
        self,
        system_instruction: str,
        user_instruction: str,
        response_format: BaseModel | NotGiven = NOT_GIVEN,
        temperature: float = 0.2,
        max_retries: int = 3,
        response_format_flag: bool = False,
    ) -> Dict[str, Any]:
        """
        Generates a response from the GPT model based on the provided prompts.
        """
        logger.info("Generating GPT response with system_instruction and user_instruction.")
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        if user_instruction:
            messages.append({"role": "user", "content": user_instruction})
            
        retries = 0
        while retries < max_retries:
            try:
                logger.debug(f"GPT call attempt {retries + 1}/{max_retries}.")
                if response_format_flag:
                    structured_response = self.client.beta.chat.completions.parse(
                        model="docs-dev-struct-4o",  
                        messages=messages,
                        response_format=response_format,
                        timeout=60,
                    )
                    logger.debug("Successfully parsed structured response from GPT.")
                    return structured_response.choices[0].message.parsed
                else:
                    response = self.client.beta.chat.completions.parse(
                        model="docs-dev-struct-4o",  
                        messages=messages,
                    )
                    logger.debug("Successfully got raw text response from GPT.")
                    return response.choices[0].message.content

            except TimeoutError:
                retries += 1
                time.sleep(2 ** retries)  # Exponential backoff
                logger.warning(f"TimeoutError: Retrying... Attempt {retries}/{max_retries}")
            except Exception as e:
                logger.error(f"GPT model error on attempt {retries + 1}: {e}")
                raise e

        logger.error("GPT model request timed out after maximum retries.")
        raise Exception("Request timed out after multiple retries.")
