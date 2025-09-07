from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os
from pydantic import BaseModel, Field
from typing import Literal
from typing_extensions import Annotated
from langchain.tools.retriever import create_retriever_tool
import logging

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class ComplianceState(TypedDict):
    topic: Annotated[str, Field(description="The topic of the call")]
    summary: Annotated[str, Field(description="A summary of the call")]
    context: Annotated[str, Field(description="Policy documents about the topic")]
    compliance: Annotated[str, Field(description="How well this complies with the company's policies")]

class Compliance:
    def __init__(self):
        pc = Pinecone(os.environ["PINECONE_API_KEY"])
        index_name = "capstone-call-center"
        index = pc.Index(index_name)

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)

        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 2, "score_threshold": 0.3},
        )

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        llm = ChatAnthropic(model="claude-sonnet-4-20250514", api_key=api_key)

        workflow = StateGraph(ComplianceState)

        def get_relevant_documents(state: ComplianceState):
            try:
                print(f"Compliance State is {state}")
                documents = retriever.invoke(state['topic'])
                print(f"Retrieved documents {documents}")
                return {"context": documents}
            except Exception as e:
                print(f"Error retrieving documents: {e}")
                return {"context": []}

        def evaluate_compliance(state: ComplianceState):
            msg = llm.invoke(f"""
            The following text represents a summary of a call transcript between a call center for an electronics store and a customer.

            <transcript>
            {state['summary']}
            </transcript>

            The topic of the call is {state['topic']}

            The following are some documents indicating the company's policies on this topic:

            <policies>
            {state['context']}
            </policies

            Evaluate how well the agent followed these policies
            """)

            return {"compliance": msg.content}

        # Define the nodes we will cycle between
        workflow.add_node("get_relevant_documents", get_relevant_documents)
        workflow.add_node("evaluate_compliance", evaluate_compliance)

        workflow.add_edge(START, "get_relevant_documents")
        workflow.add_edge("get_relevant_documents", "evaluate_compliance")
        workflow.add_edge("get_relevant_documents", END)

        # Compile
        self.graph = workflow.compile()
        logger.info(f"Compiled graph is {self.graph}")

    def analyze(self, summary, topic):
        logger.info("Starting analyze")
        state = self.graph.invoke({"summary": summary, "topic": topic})
        return state['compliance']