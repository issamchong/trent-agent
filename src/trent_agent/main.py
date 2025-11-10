#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from trent_agent.crew import TrentAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year),
        # Example user query for product recommendations
        'user_query': 'I need a lightweight laptop for video editing and programming on a budget of $1000'
    }
    
    try:
        TrentAgent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        TrentAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TrentAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        TrentAgent().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_firebase(collection: str = "products", operation: str = "query"):
    """
    Run the crew with Firebase operations.
    
    Args:
        collection (str): The Firebase collection to operate on (default: "products")
        operation (str): The operation to perform (default: "query")
                        Options: "query", "create", "read", "update", "delete"
    """
    inputs = {
        'firebase_collection': collection,
        'firebase_operation': operation,
        'current_year': str(datetime.now().year)
    }
    # You can also provide a `user_query` to run the recommend_products_task behavior
    # Example:
    # inputs['user_query'] = 'looking for noise-cancelling wireless earbuds with long battery life'

    try:
        TrentAgent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running Firebase operation: {e}")
