from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
import json
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv
load_dotenv()

#Shared State
class DebateState(TypedDict):
    """The shared state that flows through our agent graph"""
    decision: str
    context: str
    orchestrator_plan: str
    optimist_case: str
    devil_case: str
    risk_assessment: str
    research_queries: List[str]
    research_evidence: str
    final_verdict: str
    confidence: float

#Prompts for each Agent Node
ORCHESTRATOR_PROMPT = """You are a strategic decision analyst. Break down this decision into 3-5 key evaluation dimensions. 
Decision: {decision}
Context: {context}
Output a JSON with keys: "dimensions" (list), "research_topics" (list of strings to investigate)."""

OPTIMIST_PROMPT = """You are an optimistic strategist. Build the strongest possible case FOR this decision.
Decision: {decision}
Context: {context}
Dimensions: {dimensions}
Focus on opportunities, benefits, and upside potential. Be specific and compelling."""

DEVIL_PROMPT = """You are a skeptical devil's advocate. Destroy this decision with brutal logic.
Decision: {decision}
Context: {context}
Dimensions: {dimensions}
Focus on hidden flaws, opportunity costs, and why this will fail. Be ruthless."""

RISK_PROMPT = """You are a risk analyst. Identify concrete risks and mitigation strategies.
Decision: {decision}
Context: {context}
Dimensions: {dimensions}
Output structured risks with probability and impact scores."""

JUDGE_PROMPT = """You are a wise judge. Synthesize these arguments into a final verdict.
Decision: {decision}
Context: {context}
Optimist Case: {optimist_case}
Devil Case: {devil_case}
Risk Assessment: {risk_assessment}
Research Evidence: {research_evidence}
Provide:
1. Verdict (PROCEED/PROCEED WITH CAUTION/DON'T PROCEED)
2. Confidence Score (0-100)
3. Key Deciding Factors (bullet points)
4. Recommended Next Steps
5. Critical Assumptions to Validate
Output as JSON with keys: verdict, confidence, factors, next_steps, assumptions."""

RESEARCH_SYNTHESIS_PROMPT = """You are a meticulous research curator. 
I am providing you with raw search results scraped from the web.
Your task is to extract only the meaningful, factual information and strip out all website boilerplate (like 'Log in', 'Subscribe', author names, navigation menus, and dates).

Write a clean, highly readable executive summary of the findings.
- Organize the findings logically.
- Use bolding and bullet points for readability.
- Cite the source titles where relevant.
- Do NOT include any website garbage text.

Raw Search Data:
{raw_evidence}"""

#Tools
def get_research_tool():
    """Web search tool for domain research"""
    return TavilySearchResults(max_results=3)

#Agent Nodes
def orchestrator_agent(state: DebateState, config: RunnableConfig) -> Dict[str, Any]:
    """Analyzes decision and creates evaluation framework"""

    #Forcing Groq into native JSON Mode
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        response_format={"type": "json_object"} 
    )

    prompt = ChatPromptTemplate.from_template(ORCHESTRATOR_PROMPT)
    
    #Attaching JsonOutputParser to the end of the chain
    chain = prompt | llm | JsonOutputParser()
    
    #The response comes back cleanly parsed as a Python dict automatically
    analysis = chain.invoke({
        "decision": state["decision"],
        "context": state.get("context", "No additional context provided")
    })
    
    return {
        "orchestrator_plan": json.dumps(analysis["dimensions"]),
        "research_queries": analysis["research_topics"]
    }

def optimist_agent(state: DebateState, config: RunnableConfig) -> Dict[str, Any]:
    """Builds the positive case"""
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7)

    prompt = ChatPromptTemplate.from_template(OPTIMIST_PROMPT)
    chain = prompt | llm
    
    response = chain.invoke({
        "decision": state["decision"],
        "context": state.get("context", ""),
        "dimensions": state["orchestrator_plan"]
    })
    
    return {"optimist_case": response.content}

def devil_agent(state: DebateState, config: RunnableConfig) -> Dict[str, Any]:
    """Builds the negative case"""
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7)
    prompt = ChatPromptTemplate.from_template(DEVIL_PROMPT)
    chain = prompt | llm
    
    response = chain.invoke({
        "decision": state["decision"],
        "context": state.get("context", ""),
        "dimensions": state["orchestrator_plan"]
    })
    
    return {"devil_case": response.content}

def risk_agent(state: DebateState, config: RunnableConfig) -> Dict[str, Any]:
    """Identifies and quantifies risks"""
    llm = ChatGroq(
    model="llama-3.3-70b-versatile",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7)
    prompt = ChatPromptTemplate.from_template(RISK_PROMPT)
    chain = prompt | llm
    
    response = chain.invoke({
        "decision": state["decision"],
        "context": state.get("context", ""),
        "dimensions": state["orchestrator_plan"]
    })
    
    return {"risk_assessment": response.content}

def research_agent(state: DebateState, config: RunnableConfig) -> Dict[str, Any]:
    """Gathers external evidence and uses an LLM to synthesize a clean briefing"""
    search = get_research_tool()
    raw_evidence = []
    
    #Gathering the raw, messy data from Tavily
    for query in state["research_queries"]:
        try:
            results = search.invoke(query)
            raw_evidence.append(f"--- Search Query: {query} ---\n{json.dumps(results)}")
        except Exception as e:
            raw_evidence.append(f"Search for '{query}' failed: {str(e)}")
            
    raw_evidence_str = "\n\n".join(raw_evidence)
    
    #Using the LLM to clean up the garbage text and write a neat summary
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3 
    )
    
    prompt = ChatPromptTemplate.from_template(RESEARCH_SYNTHESIS_PROMPT)
    chain = prompt | llm
    
    response = chain.invoke({
        "raw_evidence": raw_evidence_str
    })
    
    return {"research_evidence": response.content}

def judge_agent(state: DebateState, config: RunnableConfig) -> Dict[str, Any]:
    """Synthesizes final verdict"""
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        response_format={"type": "json_object"} 
    ) 
    
    prompt = ChatPromptTemplate.from_template(JUDGE_PROMPT)
    
    #Attach JsonOutputParser here as well
    chain = prompt | llm | JsonOutputParser()
    
    verdict = chain.invoke({
        "decision": state["decision"],
        "context": state.get("context", ""),
        "optimist_case": state["optimist_case"],
        "devil_case": state["devil_case"],
        "risk_assessment": state["risk_assessment"],
        "research_evidence": state["research_evidence"]
    })
    
    return {
        "final_verdict": json.dumps(verdict, indent=2),
        "confidence": verdict["confidence"]
    }

#Constructing the Graph
def build_debate_graph() -> StateGraph:
    """Builds the LangGraph workflow"""
    workflow = StateGraph(DebateState)
    
    #Adding nodes
    workflow.add_node("orchestrator", orchestrator_agent)
    workflow.add_node("optimist", optimist_agent)
    workflow.add_node("devil", devil_agent)
    workflow.add_node("risk_analyst", risk_agent)
    workflow.add_node("researcher", research_agent)
    workflow.add_node("judge", judge_agent)
    
    #Define flow: orchestrator -> parallel debate -> research -> judge
    workflow.set_entry_point("orchestrator")
    workflow.add_edge("orchestrator", "optimist")
    workflow.add_edge("orchestrator", "devil")
    workflow.add_edge("orchestrator", "risk_analyst")
    workflow.add_edge("optimist", "researcher")
    workflow.add_edge("devil", "researcher")
    workflow.add_edge("risk_analyst", "researcher")
    workflow.add_edge("researcher", "judge")
    workflow.add_edge("judge", END)
    
    return workflow.compile()

#Main execution function
def run_decision_debate(decision: str, context: str = "") -> DebateState:
    """Execute the full debate team on a decision"""
    graph = build_debate_graph()
    
    initial_state: DebateState = {
        "decision": decision,
        "context": context,
        "orchestrator_plan": "",
        "optimist_case": "",
        "devil_case": "",
        "risk_assessment": "",
        "research_queries": [],
        "research_evidence": "",
        "final_verdict": "",
        "confidence": 0.0
    }
    
    final_state = graph.invoke(initial_state)
    return final_state

#to visualize the graph structure
def visualize_graph():
    """Generate and save graph visualization"""
    graph = build_debate_graph()
    png_data = graph.get_graph().draw_mermaid_png()
    
    with open("debate_architecture.png", "wb") as f:
        f.write(png_data)
    print("Graph saved to debate_architecture.png")

if __name__ == "__main__":
    visualize_graph()