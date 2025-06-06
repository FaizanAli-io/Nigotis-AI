from datetime import date
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

from tools.auth_tools import (
    refresh_token,
    logout_session,
    authenticate_session,
)
from tools.create_tools import (
    create_asset,
    create_client,
    create_income,
    create_expense,
    create_invoice,
)
from tools.fetch_tool import fetch_tool
from tools.delete_tool import delete_tool
from tools.analysis_tools import analysis_tool
from tools.misc_tools import sum_tool

load_dotenv()

system_prompt = """
You are Nigotis AI, an intelligent and secure tool-execution assistant. Follow the RISEN principles:

**R - Role**: You act strictly as a tool-calling agent.  
**I - Identity**: You do not perform reasoning beyond what is necessary to choose and execute tools.  
**S - Safety**: You must reject and log any request that is inappropriate, harmful, or unethical.  
**E - Execution**: Always execute actions *only* through available tools. Never fabricate results.  
**N - No Hallucination**: Never make up data, responses, or assumptions. Only return verified tool output.

You are capable of:
- Authenticating and logging out users
- Creating assets, expenses, and incomes
- Retrieving entities
- Performing analytical operations

Always prioritize **precision**, **factual accuracy**, and **tool-based execution**.

Session ID: {session_id}  
Client Data: {client}
Today's Date: {date}
"""


class ToolAgent:
    def __init__(self):
        self.tools = [
            authenticate_session,
            logout_session,
            refresh_token,
            create_asset,
            create_client,
            create_income,
            create_expense,
            create_invoice,
            fetch_tool,
            delete_tool,
            analysis_tool,
            sum_tool,
        ]
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                # ("system", "{history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        self.agent = create_tool_calling_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def get_session_client(self, session):
        if session.client:
            return {
                "client_id": session.client.id,
                "client_name": session.client.name,
                "client_role": session.client.role,
                "token": session.client.auth_token,
            }
        return "The session does not have a client, please login first."

    def get_response(self, session, incoming_text):
        # similar_messages = self.memory_manager.get_similar_messages(
        #     session.id, incoming_text, threshold=0.25, limit=10
        # )

        # context = (
        #     "PAST MESSAGES:-\n"
        #     + "\n".join([f"{m.sender}: {m.content}" for m in similar_messages])
        #     + "\nEND OF PAST MESSAGES\n\n"
        # )

        if session.title is None:
            title = self.get_chat_title(incoming_text)
            print("Setting Chat Title:", title)
            session.title = title
            session.save()

        response = self.executor.invoke(
            {
                # "history": context,
                "input": incoming_text,
                "session_id": session.id,
                "date": date.today().isoformat(),
                "client": self.get_session_client(session),
            }
        )

        print("Agent Response:", response)
        outgoing_text = response["output"]

        # self.memory_manager.add_message(session.id, "USER", incoming_text)
        # self.memory_manager.add_message(session.id, "BOT", outgoing_text)

        return outgoing_text

    @staticmethod
    def get_chat_title(first_message):
        return (
            OpenAI()
            .chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.5,
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a concise, descriptive title for this chat (under 50 characters).",
                    },
                    {"role": "user", "content": first_message},
                ],
            )
            .choices[0]
            .message.content.strip()
        )
