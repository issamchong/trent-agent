#!/usr/bin/env python
import sys
import warnings
import re

from datetime import datetime

from trent_agent.crew import TrentAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# RTL direction markers
RLE = '\u202B'  # Right-to-Left Embedding
PDF = '\u202C'  # Pop Directional Formatting

def ensure_rtl_formatting(text):
    """
    Ensure Arabic text has RTL direction markers for proper right-to-left display.
    """
    if not text:
        return text
    
    # Check if text contains Arabic characters
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    
    # If text contains Arabic but doesn't start with RLE, add RTL markers
    if arabic_pattern.search(text) and not text.startswith(RLE):
        # Wrap the entire text with RTL markers
        return f"{RLE}{text}{PDF}"
    
    return text

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    print("🚀 Starting Trent Agent...")
    print("="*60)
    
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year),
        # Example user query for product recommendations
        'user_query': 'I need a lightweight laptop for video editing and programming on a budget of $1000'
    }
    
    try:
        print("📋 Initializing crew...")
        crew = TrentAgent().crew()
        print("✅ Crew initialized")
        print("🔄 Running tasks...\n")
        
        result = crew.kickoff(inputs=inputs)
        # Print the final result so user can see the agent's response
        if result:
            print("\n" + "="*60)
            print("Agent Response:")
            print("="*60)
            # CrewAI returns a CrewOutput object with various attributes
            if hasattr(result, 'raw'):
                # Print raw output with RTL formatting
                output = str(result.raw)
                print(ensure_rtl_formatting(output))
            elif hasattr(result, 'tasks_output'):
                # Print each task's output with RTL formatting
                for task_output in result.tasks_output:
                    if task_output:
                        print(ensure_rtl_formatting(str(task_output)))
            elif hasattr(result, 'tasks'):
                # Print task results with RTL formatting
                for task in result.tasks:
                    if hasattr(task, 'output') and task.output:
                        print(ensure_rtl_formatting(str(task.output)))
            # Print raw result if it's a string with RTL formatting
            elif isinstance(result, str):
                print(ensure_rtl_formatting(result))
            # Print the result object's string representation
            else:
                # Try to get any useful information from the result
                print(f"Result type: {type(result)}")
                print(f"Result attributes: {dir(result)}")
                if hasattr(result, '__dict__'):
                    print(f"Result dict: {result.__dict__}")
                print(str(result))
            print("="*60 + "\n")
        else:
            print("\n⚠ No output received from the crew.\n")
            print("This might indicate that the tasks completed but produced no output.")
            print("Check your task configurations in tasks.yaml\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
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
