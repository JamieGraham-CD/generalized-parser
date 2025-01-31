from models.gpt_model import GPTModel
from StructuredOutput.PydanticClasses import ParserResponse
from parser import Parser
import pandas as pd
import pprint

def main(input_dict:dict) -> dict:
	"""
	Main entry point to codebase .
	"""
	# Initialize parser
	parser_instance = Parser(input_dict)

	# Run main orchestrating method of parser
	output = parser_instance.run()

	# Print output
	pprint.pprint(output)

	# Save output as DataFrame
	output = pd.DataFrame([output])

	# Output to CSV
	output.to_csv("output.csv")

	return output



# Initialize LLM
model = GPTModel()

# Read scraped input
with open("./inputs/andover_scrape_input.txt","r") as file:
	test_scrape_html = file.read()

# Read system prompt
with open("./prompts/system_prompt.txt","r") as file:
	system_instructions = file.read()

# Load Parser input dictionary with structured output, llm, system instructions and user input.
input_dict = {
	"llm":model,
	"structured_output_class":ParserResponse,
	"system_instructions":system_instructions,
	"user_input":test_scrape_html,
	"id":"andover"
}

main(input_dict)