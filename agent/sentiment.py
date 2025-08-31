from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Optional
import logging

class State(TypedDict):
    transcript: str
    topic: Optional[str]
    goal: Optional[str]
    success: Optional[str]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Sentiment:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-sonnet-4-20250514")

        def extract_topic(state: State):
            """Extract the topic of the transcript"""

            logging.info(f"Extract topic {state}")

            msg = self.llm.invoke(f"""
            The followng text represents a call transcript between a call center for an electronics store and a customer.
            Extract the reason for the call.  Examples are: Return, Purchase, Technical Issue - Would Not Boot, Technical Issue - Network Dropouts, etc.
            You can come up with new reasons for the call, but keep it under one sentence.

            {state['transcript']}
            """)

            return {"topic": msg.content}

        def determine_goal(state: State):
            """Determine the goal of the customer"""

            print(f'State is {state}')

            msg = self.llm.invoke(f"""
            The followng text represents a call transcript between a call center for an electronics store and a customer.

            <transcript>
            {state['transcript']}
            </transcript>

            The topic of the call is {state['topic']}

            Come up with one sentence about what the goal of the customer is during this call.  What would make them happy?
            """)

            return {"goal": msg.content}

        def evaluate_success(state: State):
            """Determine whether the outcome of the call for the customer was successful"""

            msg = self.llm.invoke(f"""
              The followng text represents a call transcript between a call center for an electronics store and a customer.

              <transcript>
              {state['transcript']}
              </transcript>

              The topic of the call is {state['topic']}

              The goal of the customer is {state['goal']}

              Evaluate how well this goal was met by outputting one of the following 3 values: Yes, Partial, No.  Only output a single word.
              """)

            return {"success": msg.content}

        workflow = StateGraph(State)

        workflow.add_node("extract_topic", extract_topic)
        workflow.add_node("determine_goal", determine_goal)
        workflow.add_node("evaluate_success", evaluate_success)

        workflow.add_edge(START, "extract_topic")
        workflow.add_edge("extract_topic", "determine_goal")
        workflow.add_edge("determine_goal", "evaluate_success")
        workflow.add_edge("evaluate_success", END)

        self.chain = workflow.compile()


    def analyze(self, transcript):
        logger.info("Starting analyze")
        state = self.chain.invoke({"transcript": transcript})
        logger.info(f"Returned state {state}")
        return state