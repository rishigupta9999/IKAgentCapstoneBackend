from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Summarizer:
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.llm = ChatAnthropic(model="claude-sonnet-4-20250514", api_key=api_key)
        self.fallback_llm = ChatAnthropic(model="claude-3-7-sonnet-latest", api_key=api_key)

    def _invoke_with_fallback(self, prompt):
        """Invoke LLM with fallback to Claude 3.5 Sonnet on error"""
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            logging.warning(f"Claude 4 failed: {e}. Falling back to Claude 3.5 Sonnet")
            return self.fallback_llm.invoke(prompt)

    def analyze(self, transcript):
        logger.info("Starting analyze")
        response = self._invoke_with_fallback(f"""
        The following text represents a call transcript between a call center for an electronics store and a customer.
        Generate a concise summary that should be no more than 3 sentences.  It should allow the reader to quickly
        get the reason for the call, actions taken by the call center agent, and outcome
        
        {transcript}
        """)

        return response.content