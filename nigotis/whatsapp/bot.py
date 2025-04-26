from langchain_openai import ChatOpenAI

from langchain.agents import AgentExecutor, create_tool_calling_agent

from langchain_core.prompts import ChatPromptTemplate

from tools.auth_tools import authenticate_session, logout_session, refresh_token
from tools.create_tools import create_asset, create_expense, create_income
from tools.fetch_tools import fetch_tool
from tools.analysis_tools import analysis_tool

from dotenv import load_dotenv

load_dotenv()


def get_session_token(session):
    print(session)
    if session.client and session.client.auth_token:
        return session.client.auth_token
    return "The session does not have a client, please login first."


def get_agent():
    tools = [
        authenticate_session,
        logout_session,
        refresh_token,
        create_asset,
        create_expense,
        create_income,
        fetch_tool,
        analysis_tool,
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are Nigotis AI, a powerful tool calling bot, you can carry out a variety of functions.
You can authenticate users, logout users, create assets, expenses, and incomes, retrieve various entities, and perform analytical operations by interacting with available tools.
Always use tools when taking actions on behalf of the user.
Session ID is {session_id}, and Auth Token is {token}.""",
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


def get_bot_response(session, incoming_text):
    agent = get_agent()

    response = agent.invoke(
        {
            "input": incoming_text,
            "session_id": session.id,
            "token": get_session_token(session),
        }
    )

    print("Agent Response:", response)

    return response
