import os
import sys
import json
from typing import Literal
from typing_extensions import TypedDict, Annotated
import operator

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph import StateGraph, START, END

import tool
import scraper
from dotenv import load_dotenv

load_dotenv()
os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ.get("ENDPOINT")
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

model = init_chat_model(
    "azure_openai:gpt-4o",
    azure_deployment="gpt-4o",
    temperature=0.2,
    max_tokens=1200,
    max_retries=2,
    timeout=30,
)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    compiled_context: dict

def profiling_node(state: AgentState):
    system_prompt = (
        "You are an elite Technical Career Architect and Senior Code Auditor.\n"
        "Your task is to ingest a candidate's structured GitHub analytics payload and produce a highly "
        "accurate, strategic developer profile.\n\n"
        "Strict Evaluation Directives:\n"
        "1. Identify 'primary_techstack': Intersect high-frequency languages with the tooling in recent projects.\n"
        "2. Infer 'job-role': Analyze velocity and architectures to deduce focus (e.g., AI/ML, Full-Stack, IoT).\n"
        "3. Provide Actionable Score Optimization: Give 2-3 specific recommendations based on sub-optimal metrics.\n\n"
        "CRITICAL - METRIC DEFINITIONS:\n"
        "You MUST base your advice strictly on what these metrics actually measure mathematically. Do not invent meanings:\n"
        "- 'Consistency': Measures the frequency and spread of commits across the last 12 months.\n"
        "- 'Community': Measures collaboration, specifically the user's commit ratio on multi-contributor repositories.\n"
        "- 'Technology': Measures the breadth (number of languages) and depth (frequency of use) of the tech stack.\n"
        "- 'Management': Measures documentation habits, specifically the ratio of repositories with README files.\n"
        "- 'Advanced': STRICTLY measures open-source engagement. It evaluates the stars/forks of upstream repositories the user has forked AND pushed commits to. It does NOT mean advanced coding techniques.\n\n"
        "Formatting Output:\n"
        "Deliver response in clean Markdown with clear headings. Sections: Executive Summary, Core Technical Profiling, "
        "Score Diagnostics Breakdown, Next-Action Roadmap."
    )
    human_content = f"Please evaluate the following compiled profile context:\n\n{json.dumps(state['compiled_context'], indent=4)}"
    
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content)
    ])
    return {"messages": [response]}

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <github_profile_url_or_username>")
        sys.exit(1)

    target_input = sys.argv[1]
    
    print(f"[*] Extracting telemetry directly from GitHub for: {target_input}...")
    raw_data = scraper.run_scraper(target_input)
    
    if "error" in raw_data:
        print(f"Error: {raw_data['error']}")
        sys.exit(1)

    print("[*] Telemetry extracted. Compiling Agent Context...")
    compiled_context = tool.compile_payload_from_memory(raw_data)

    workflow = StateGraph(AgentState)
    workflow.add_node("profiler", profiling_node)
    workflow.add_edge(START, "profiler")
    workflow.add_edge("profiler", END)
    agent_pipeline = workflow.compile()

    print(f"[*] Dispatching Agent...\n" + "="*50 + "\n")
    initial_state = {"messages": [], "compiled_context": compiled_context}
    output_state = agent_pipeline.invoke(initial_state)
    print(output_state["messages"][-1].content)

if __name__ == "__main__":
    main()