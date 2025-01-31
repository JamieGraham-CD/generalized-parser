
from pydantic import BaseModel, Field
from typing import Literal, Any, Dict, Optional
from dotenv import load_dotenv
import os
from langfuse.openai import AzureOpenAI
from pydantic import BaseModel
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
import pandas as pd
import re
from models.gpt_model import GPTModel
import json
from bs4 import BeautifulSoup

load_dotenv()

class Parser():
    """
    A class for parsing and extracting structured information from raw HTML or text data.

    The `Parser` class is designed to process unstructured or semi-structured data, such as
    HTML content, and extract meaningful information based on predefined rules or patterns.
    It supports cleaning, transforming, and organizing data for downstream applications.

    Attributes:
        input_dict (dict): A dictionary of inputs to the Parser 

    Methods:
        __init__(preserve_tags=None, remove_whitespace=True, custom_patterns=None):
            Initializes the parser with optional configurations for tag preservation,
            whitespace removal, and custom patterns.
            
        parse_to_dict(html: str) -> dict:
            Parses the input HTML and extracts predefined fields into a dictionary format.

        clean_text(text: str) -> str:
            Cleans raw text by normalizing whitespace, removing unwanted characters,
            and applying other text-cleaning logic.

        run(self) -> dict:
            Main orchestration function for the parsing.
    """
    def __init__(self,input_dict:dict):
        """
        Initializes the Parser class.
        """
        self.input_dict = input_dict

        
    def clean_html(self,html: Optional[str]) -> str:
        """
        Cleans an HTML string by removing all tags except <a> tags and extracting plain text.

        Args:
            html (Optional[str]): The input HTML string to be cleaned. If None, returns an empty string.

        Returns:
            str: The cleaned text, preserving <a> tags while removing other HTML tags and extraneous whitespace.
        """
        try:
            if html is None:
                return ''
            
            # Parse the HTML content
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove all tags except <a> by iterating through tags
            for tag in soup.find_all(True):  # Finds all tags in the HTML
                if tag.name != 'a':
                    tag.unwrap()  # Remove the tag but keep its content
            
            # Get the cleaned HTML with <a> tags preserved
            cleaned_html = str(soup)
            
            # Clean up whitespace and empty lines
            cleaned_html = "\n".join([line.strip() for line in cleaned_html.splitlines() if line.strip()])
            cleaned_html = re.sub(r'\s{2,}', ' ', cleaned_html)  # Replace extra spaces with a single space

        except Exception as e:
            # Handle parsing or processing errors
            cleaned_html = ''
            print(f"Error during HTML cleaning: {e}")
        
        return cleaned_html

    def run(self) -> dict:
        """
        Executes the parsing and response generation process using the provided input instructions and LLM.

        This method performs the following steps:
        1. Cleans and preprocesses the user input by removing unnecessary HTML content.
        2. Retrieves the system instructions for the task.
        3. Defines the structured output format expected from the response.
        4. Uses the specified language model (LLM) to generate a structured response based on the instructions.
        5. Converts and returns the generated response as a dictionary.

        Returns:
            dict: The generated response in a structured format, as defined by the `structured_output_class`.

        Workflow:
            - The `user_instructions` field is cleaned using the `clean_html` method.
            - The `system_instructions`, `structured_output_class`, and `llm` (language model) are retrieved from the `input_dict`.
            - The `generate_response` method of the model generates a response based on the instructions.
            - The response is formatted as a dictionary by calling the `model_dump` method.

        Example Usage:
            Assuming `self.input_dict` is structured as follows:
            ```
            {
                'user_input': "<p>Hello, how can I...</p>",
                'system_instructions': "Parse and classify the following...",
                'structured_output_class': ResponseFormatClass,
                'llm': language_model_instance
            }
            ```
            Calling `run()` will:
            - Clean `user_input` to plain text.
            - Use the language model to generate a structured response.
            - Return the response as a dictionary.
        """

        # Step 1: Clean and preprocess the user input to remove unnecessary HTML content
        user_instructions = self.clean_html(self.input_dict['user_input'])

        # Step 1a: Save cleaned input
        with open(f"./intermediate/{self.input_dict['id']}_cleaned_input.txt","w") as file:
            file.write(user_instructions)
        
        # Step 2: Retrieve the system instructions to define the task for the LLM
        system_instructions = self.input_dict['system_instructions']

        # Step 3: Specify the structured output format expected from the LLM response
        response_format = self.input_dict['structured_output_class']

        # Step 4: Retrieve the language model (LLM) instance to generate the response
        model = self.input_dict['llm']

        # Step 5: Generate the response using the LLM with the provided instructions, user input, and output format
        response = model.generate_response(
            system_instructions,
            user_instructions,
            response_format,
            response_format_flag=True
        )

        # Step 6: Convert the response into a dictionary format for further use
        response = response.model_dump()

        return response

