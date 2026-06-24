import os
import sys
import json
from typing import Literal
from typing_extensions import TypedDict, Annotated
import operator
from dotenv import load_dotenv

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph import StateGraph, START, END

import tool
import scraper

# Load environment variables securely
load_dotenv()
os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ.get("ENDPOINT", "")
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
    # 1. Extract the active persona
    persona = state['compiled_context'].get('evaluation_persona', 'Default')
    
    # 2. Assign dynamic behavioral instructions
    persona_instructions = ""
    if persona == "The Enterprise Recruiter":
        persona_instructions = "You are evaluating this candidate for a strict enterprise engineering role. Praise high open-source impact, rigorous consistency, and production-ready tech stacks. Be critical of disorganized or low-value repos."
    elif persona == "The Hackathon Judge":
        persona_instructions = "You are evaluating this candidate for a fast-paced hackathon. Praise their breadth of tools, rapid experimentation, and teamwork/collaboration. Forgive small dips in consistency."
    elif persona == "The Startup Founder":
        persona_instructions = "You are evaluating this candidate as a potential founding engineer. Look for 'get-it-done' full-stack breadth, good management/documentation habits, and the ability to ship multiple projects."
    else:
        persona_instructions = "You are evaluating this candidate as a balanced, objective Technical Assessor. Provide a well-rounded review of their consistency, teamwork, and technical depth."

    # 3. Compile the System Prompt
    system_prompt = f"""You are an elite Technical Career Architect and Senior Code Auditor.
Your task is to ingest a candidate's structured GitHub analytics payload and produce a highly accurate, strategic developer profile.

EVALUATION PERSONA CONTEXT:
{persona_instructions}

Strict Evaluation Directives:
1. Identify 'primary_techstack': Intersect high-frequency languages with the tooling in recent projects.
2. Infer 'job-role': Analyze velocity and architectures to deduce focus (e.g., AI/ML, Full-Stack, IoT).
3. Provide Actionable Score Optimization: Give 2-3 specific recommendations based on sub-optimal metrics. Align these recommendations with your persona context!

CRITICAL - METRIC DEFINITIONS:
You MUST base your advice strictly on what these metrics actually measure mathematically. Do not invent meanings:
- 'Consistency': Measures the frequency and spread of commits across the last 12 months.
- 'Community': Measures collaboration, specifically the user's commit ratio on multi-contributor repositories.
- 'Technology': Measures the breadth (number of languages) and depth (frequency of use) of the tech stack.
- 'Management': Measures documentation habits, specifically the ratio of repositories with README files.
- 'Advanced': STRICTLY measures open-source engagement. It evaluates the stars/forks of upstream repositories the user has forked AND pushed commits to.

Formatting Output:
Deliver response in clean Markdown with clear headings. Sections: Executive Summary, Core Technical Profiling, Score Diagnostics Breakdown, Next-Action Roadmap."""

    # We format the context into a string, but we exclude the heavy "breakdowns" dictionary 
    # to save LLM tokens (the LLM doesn't need to see the raw sigma/variance math).
    llm_context = {
        "user_target": state['compiled_context']["user_target"],
        "bio": state['compiled_context']["bio"],
        "hard_metrics": {
            "final_score": state['compiled_context']["hard_metrics"]["final_score"],
            "category_scores": state['compiled_context']["hard_metrics"]["category_scores"]
        },
        "narrative_context": state['compiled_context']["narrative_context"]
    }

    human_content = f"Please evaluate the following compiled profile context:\n\n{json.dumps(llm_context, indent=4)}"
    
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