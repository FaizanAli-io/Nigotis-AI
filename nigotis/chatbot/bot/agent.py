from openai import OpenAI
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI as LlamaOpenAI

from .tools import filter_by_date


class BaseAgent:
    def __init__(self):
        self.client = OpenAI()

    def get_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=800,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content


class LlamaAgent:
    def __init__(self, mapper):
        Settings.llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0)

        toolkit = self.define_toolkit(mapper)

        self.agent = ReActAgent.from_tools(
            tools=toolkit,
            verbose=True,
            system_prompt=(
                "The chatbot should take a stepwise approach to the task at hand. "
                "1. First, determine if any data retrieval is necessary based on the user's query. "
                "2. After retrieving data, analyze whether any filtering or further processing is required. "
                "3. Finally, provide a detailed and verbose output of the resultant data. "
                "Be mindful to avoid redundant data retrieval and ensure that filtration is applied only when needed."
            ),
        )

    def define_toolkit(self, mapper):
        toolkit = [
            FunctionTool.from_defaults(
                fn=func,
                name=func.__name__,
                description=f"Use {func.__name__} to retrieve relevant data.",
            )
            for func in [
                mapper.get_customers,
                mapper.get_products,
                mapper.get_invoices,
                mapper.get_expenses,
                mapper.get_incomes,
                mapper.get_assets,
            ]
        ]

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

        toolkit.append(filter_tool)

        return toolkit

    def get_response(self, query):
        try:
            return self.agent.chat(query).response
        except Exception as e:
            return f"Error during execution: {str(e)}"
