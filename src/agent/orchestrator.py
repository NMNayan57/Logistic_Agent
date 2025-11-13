"""
Agent orchestrator for LangChain-based logistics planning.

This module sets up the LangChain AgentExecutor with OpenAI GPT-4
and all available tools.
"""

import time
from typing import Dict, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage

from src.tools import ALL_TOOLS
from src.agent.prompts import SYSTEM_PROMPT, HUMAN_PROMPT_TEMPLATE
from src.config import get_settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class LogisticsAgent:
    """
    Logistics planning agent powered by LangChain and OpenAI GPT-4.

    This agent orchestrates specialized tools to solve vehicle routing
    problems through natural language interactions.
    """

    def __init__(self):
        """Initialize the logistics agent with tools and LLM."""
        self.settings = get_settings()
        self.agent_executor = self._create_agent_executor()
        logger.info("Logistics agent initialized successfully")

    def _create_agent_executor(self) -> AgentExecutor:
        """
        Create and configure the LangChain agent executor.

        Returns:
            Configured AgentExecutor instance
        """
        logger.info("Creating agent executor...")

        # Initialize OpenAI LLM
        llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=self.settings.openai_temperature,
            api_key=self.settings.openai_api_key,
            request_timeout=60
        )

        logger.info(f"LLM initialized: {self.settings.openai_model}")

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", HUMAN_PROMPT_TEMPLATE),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create agent with OpenAI functions
        agent = create_openai_functions_agent(
            llm=llm,
            tools=ALL_TOOLS,
            prompt=prompt
        )

        logger.info(f"Agent created with {len(ALL_TOOLS)} tools")

        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            verbose=self.settings.debug,
            max_iterations=self.settings.max_agent_iterations,
            max_execution_time=self.settings.agent_timeout,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )

        logger.info("Agent executor created successfully")
        return agent_executor

    def ask(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language query.

        Args:
            query: User's natural language question
            context: Optional context dictionary (fuel prices, etc.)
            chat_history: Optional conversation history

        Returns:
            Dictionary with response and metadata:
            {
                "response": str,              # Agent's response text
                "tools_called": List[str],    # Tools that were invoked
                "execution_time": float,      # Time taken in seconds
                "iterations": int,            # Number of reasoning steps
                "success": bool,              # Whether query was successful
                "intermediate_steps": list    # Detailed execution trace
            }
        """
        logger.info(f"Processing query: {query[:100]}...")

        start_time = time.time()

        try:
            # Prepare context string
            context_str = ""
            if context:
                context_str = "\n**Additional Context:**\n"
                for key, value in context.items():
                    context_str += f"- {key}: {value}\n"

            # Prepare input
            agent_input = {
                "query": query,
                "context": context_str,
                "chat_history": chat_history or []
            }

            # Execute agent
            result = self.agent_executor.invoke(agent_input)

            execution_time = time.time() - start_time

            # Extract tools called
            tools_called = []
            if result.get("intermediate_steps"):
                for step in result["intermediate_steps"]:
                    if hasattr(step[0], 'tool'):
                        tools_called.append(step[0].tool)

            # Build response
            response = {
                "response": result.get("output", ""),
                "tools_called": tools_called,
                "execution_time": execution_time,
                "iterations": len(result.get("intermediate_steps", [])),
                "success": True,
                "intermediate_steps": result.get("intermediate_steps", [])
            }

            logger.info(
                f"Query completed in {execution_time:.2f}s, "
                f"{len(tools_called)} tools called"
            )

            return response

        except Exception as e:
            execution_time = time.time() - start_time

            logger.error(f"Agent execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())

            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "tools_called": [],
                "execution_time": execution_time,
                "iterations": 0,
                "success": False,
                "error": str(e),
                "intermediate_steps": []
            }

    def get_available_tools(self) -> list:
        """
        Get list of available tool names.

        Returns:
            List of tool names
        """
        return [tool.name for tool in ALL_TOOLS]

    def reset_conversation(self):
        """Reset conversation history."""
        logger.info("Conversation history reset")
        # Note: LangChain agents are stateless by default
        # This method is here for potential future state management


# Singleton instance for the application
_agent_instance: Optional[LogisticsAgent] = None


def get_agent() -> LogisticsAgent:
    """
    Get singleton logistics agent instance.

    Returns:
        LogisticsAgent instance

    Example:
        >>> agent = get_agent()
        >>> response = agent.ask("Route 10 deliveries with 2 vehicles")
        >>> print(response["response"])
    """
    global _agent_instance

    if _agent_instance is None:
        logger.info("Creating new agent instance")
        _agent_instance = LogisticsAgent()

    return _agent_instance


def reload_agent() -> LogisticsAgent:
    """
    Reload agent (useful for configuration changes).

    Returns:
        New LogisticsAgent instance
    """
    global _agent_instance
    logger.info("Reloading agent instance")
    _agent_instance = LogisticsAgent()
    return _agent_instance
