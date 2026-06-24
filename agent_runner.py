import os
import json
import operator
from typing import TypedDict, Annotated
from dotenv import load_dotenv

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AnyMessage
from langgraph.graph import StateGraph, START, END

# Load environment variables securely
load_dotenv()
os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ.get("ENDPOINT", "")
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

# Initialize the Azure OpenAI Model
model = init_chat_model(
    "azure_openai:gpt-4o",
    azure_deployment="gpt-4o",
    temperature=0.2,
    max_tokens=1500,
    max_retries=2,
    timeout=30,
)

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    compiled_context: dict

def profiling_node(state: AgentState):
    """
    The core LLM reasoning node. Translates the mathematical telemetry into 
    strategic, persona-driven career advice.
    """
    context = state['compiled_context']
    persona = context.get('evaluation_persona', 'Default')
    
    # 1. Assign dynamic behavioral instructions based on the UI selection
    if "Enterprise" in persona:
        persona_instructions = "You are an Elite Enterprise Engineering Recruiter. Demand high open-source impact, rigorous consistency, and production-ready tech stacks. Be highly critical of disorganized or lone-wolf behavior."
    elif "Hackathon" in persona:
        persona_instructions = "You are a Hackathon Judge. Praise their breadth of tools, rapid experimentation, and teamwork. Forgive small dips in consistency; focus on speed, breadth, and collaboration."
    elif "Startup" in persona:
        persona_instructions = "You are a Startup Founder evaluating a founding engineer. Look for 'get-it-done' full-stack breadth, good management/documentation habits, and the ability to ship multiple projects. Focus on velocity and autonomy."
    else:
        persona_instructions = "You are a balanced, objective Technical Assessor. Provide a well-rounded, objective review of their consistency, teamwork, and technical depth."

    # 2. Compile the Master System Prompt
    system_prompt = f"""You are a Technical Career Architect and Senior Code Auditor.
Your task is to ingest a candidate's structured GitHub analytics payload and produce a highly accurate, strategic developer profile.

EVALUATION PERSONA:
{persona_instructions}

Strict Evaluation Directives:
1. Primary Tech Stack: Identify their core languages based on frequency and recent projects.
2. Deduced Role: Analyze their footprint to deduce their focus (e.g., Full-Stack, AI/ML, DevOps, Frontend).
3. Actionable Roadmap: Give 2-3 specific recommendations to optimize their sub-optimal metrics. Align these strictly with your persona context!

METRIC DEFINITIONS (DO NOT HALLUCINATE MEANINGS):
- 'Consistency': Frequency and steady spread of commits across 12 months.
- 'Community': Collaboration specifically measured via commit ratios on multi-contributor repositories.
- 'Technology': Breadth (number of distinct languages) and depth (frequency of use).
- 'Management': Code maintainability measured by README ratios and profile completeness.
- 'Advanced': Open-source impact measured by active commits pushed to famous upstream repositories.

OUTPUT FORMAT:
Return clean, professional Markdown. 
Sections must include: Executive Summary, Core Technical Profiling, Score Diagnostics, Next-Action Roadmap."""

    # 3. Strip the heavy math breakdowns to save LLM tokens (The UI handles the math explainers)
    llm_context = {
        "user_target": context.get("user_target"),
        "bio": context.get("bio"),
        "hard_metrics": {
            "final_score": context.get("hard_metrics", {}).get("final_score"),
            "category_scores": context.get("hard_metrics", {}).get("category_scores")
        },
        "narrative_context": context.get("narrative_context")
    }

    human_content = f"Please evaluate the following compiled profile context:\n\n{json.dumps(llm_context, indent=4)}"
    
    # 4. Invoke the LLM
    response = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_content)
    ])
    
    return {"messages": [response]}

def run_ai_auditor(compiled_context: dict) -> str:
    """
    Public entry point for the Streamlit UI to trigger the AI Agent.
    Builds the LangGraph pipeline, executes it, and returns the markdown string.
    """
    # Define the execution graph
    workflow = StateGraph(AgentState)
    workflow.add_node("profiler", profiling_node)
    workflow.add_edge(START, "profiler")
    workflow.add_edge("profiler", END)
    
    agent_pipeline = workflow.compile()

    # Initialize State and Run
    initial_state = {"messages": [], "compiled_context": compiled_context}
    
    try:
        output_state = agent_pipeline.invoke(initial_state)
        final_markdown = output_state["messages"][-1].content
        return final_markdown
    except Exception as e:
        return f"**Error executing AI Agent:** {str(e)}\n\nPlease check your API keys and network connection."