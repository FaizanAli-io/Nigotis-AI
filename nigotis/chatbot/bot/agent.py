from openai import OpenAI
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI as LlamaOpenAI


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
        toolkit = [
            FunctionTool.from_defaults(fn=func)
            for func in [
                mapper.get_customers,
                mapper.get_products,
                mapper.get_invoices,
                mapper.get_income,
                mapper.get_expenses,
                mapper.get_assets,
            ]
        ]

        Settings.llm = LlamaOpenAI(model="gpt-4o-mini", temperature=0)
        self.agent = ReActAgent.from_tools(toolkit, verbose=True)

    def get_response(self, query):
        return self.agent.chat(query).response
