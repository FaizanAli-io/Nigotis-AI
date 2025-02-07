from openai import OpenAI
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI as LlamaOpenAI

from .tools import (
    ENTITIES,
    fetch_data,
    filter_by_date,
)


class BaseAgent:
    def __init__(self):
        self.client = OpenAI()

    def get_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.75,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content


class LlamaAgent:
    def __init__(self, mapper):
        Settings.llm = LlamaOpenAI(
            temperature=0,
            max_retries=2,
            max_tokens=2048,
            model="gpt-4o-mini",
        )

        toolkit = self.define_toolkit(mapper)

        self.agent = ReActAgent.from_tools(
            tools=toolkit,
            verbose=True,
           system_prompt=(
               "The chatbot should take a stepwise approach to the task at hand. "
               "1. First, determine if any data retrieval is necessary based on the user's query. "
               "2. After retrieving data, analyze whether any filtering or further processing is required. "
               "3. Finally, provide a detailed and verbose output of the resultant data. "
                "Be mindful to avoid redundant data retrieval and ensure that filtration is applied only when needed. Respond strictly in English."
           ),


        )

    def define_toolkit(self, mapper):
        fetch_data_tool = FunctionTool.from_defaults(
            fn=lambda entity: fetch_data(mapper, entity),
            name="fetch_data",
            description=f"Use this to retrieve data for an entity. Available entities: {', '.join(ENTITIES)}.",
        )

        filter_tool = FunctionTool.from_defaults(
            fn=filter_by_date,
            name="filter_by_date",
            description=(
                "Use this to filter an array of data by a given date in the format 'dd-mm-yyyy'. "
                "Specify 'after' to include dates on or after the given date, 'before' to include dates before it, "
                "or 'range' to include dates between a start and end date. "
                "It checks for 'date' or 'issueDate' properties in array elements."
            ),
        )

        return [fetch_data_tool, filter_tool]

    def get_response(self, query):
        try:
            return self.agent.chat(query).response
        except Exception as e:
            return f"Error during execution: {str(e)}"
