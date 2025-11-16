from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from trent_agent.tools import FirebaseReadOnlyTool

@CrewBase
class TrentAgent():
    """TrentAgent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

  
    @agent
    def firebase_agent(self) -> Agent:
        # Configure Gemini LLM (using 2.5 Flash as requested)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Set environment variable for LiteLLM (required for Gemini)
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        
        # Use gemini-2.5-flash with prefix as requested
        # LiteLLM format: gemini/gemini-{version}-{model}
        gemini_llm = LLM(
            model="gemini/gemini-2.5-flash",
            api_key=gemini_api_key
        )
        
        return Agent(
            config=self.agents_config['firebase_agent'], # type: ignore[index]
            verbose=False,
            tools=[FirebaseReadOnlyTool()],
            llm=gemini_llm
        )



    @task
    def greet_user_task(self) -> Task:
        """Task to greet the user in Arabic when the app starts."""
        return Task(
            config=self.tasks_config['greet_user_task'], # type: ignore[index]
        )

    @task
    def query_products_task(self) -> Task:
        return Task(
            config=self.tasks_config['query_products_task'], # type: ignore[index]
        )

    @task
    def recommend_products_task(self) -> Task:
        """Task to recommend products based on a user query."""
        return Task(
            config=self.tasks_config['recommend_products_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TrentAgent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=False,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
