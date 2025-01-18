from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool


class Agent:
    def __init__(self, mapper):
        toolkit = [
            FunctionTool.from_defaults(fn=func)
            for func in [
                mapper.map_customers,
                mapper.map_products,
                mapper.map_invoices,
                mapper.map_income,
                mapper.map_expenses,
                mapper.map_assets,
            ]
        ]

        load_dotenv()
        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0)
        self.agent = ReActAgent.from_tools(toolkit, verbose=True)

    def get_response(self, query):
        return self.agent.chat(query)
