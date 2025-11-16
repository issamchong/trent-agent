from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from trent_agent.tools import FirebaseReadOnlyTool

@CrewBase
class TrentAgent():
    """TrentAgent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

  
    @agent
    def firebase_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['firebase_agent'], # type: ignore[index]
            verbose=False,
            tools=[FirebaseReadOnlyTool()]
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
