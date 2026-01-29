import asyncio
import os
import sys
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

load_dotenv()

# --- LOCAL TOOL: SAVE THE REPORT ---
# We define this locally because we want to save the file on YOUR machine,
# not on the GitHub server.
async def save_report(content: str) -> str:
    """Saves the final analysis to a local file named IMPROVEMENTS.md"""
    try:
        with open("IMPROVEMENTS.md", "w", encoding="utf-8") as f:
            f.write(content)
        return "SUCCESS: Report saved to IMPROVEMENTS.md"
    except Exception as e:
        return f"Error saving report: {e}"

async def main():
    # 1. GET USER INPUT
    repo_name = input("Enter the GitHub Repository to analyze (e.g. pallets/flask): ").strip()
    if not repo_name:
        print("Please enter a valid repo name.")
        return

    print(f"\n🩺 Initializing Repo Doctor for: {repo_name}...")

    # 2. CONNECT TO MCP SERVER (The "Eyes")
    server_params = StdioServerParams(command="python", args=["github_server.py"])
    
    try:
        remote_tools = await mcp_server_tools(server_params)
        # We combine remote tools (GitHub) with our local tool (Save File)
        all_tools = remote_tools + [save_report]
    except Exception as e:
        print(f"❌ Could not connect to MCP Server: {e}")
        return

    # 3. DEFINE AGENTS
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    # Agent 1: The Navigator
    # Responsible for exploring the file tree and finding the "meat" of the code.
    navigator = AssistantAgent(
        name="Navigator",
        model_client=model_client,
        tools=all_tools,
        system_message=f"""
        You are a Repository Navigator.
        1. Start by listing files in '{repo_name}' using `list_files`.
        2. Identify the core logic files (look for main.py, app.py, src/, or lib/).
        3. Tell the Analyst specifically which 1-2 files to read and why.
        """
    )

    # Agent 2: The Analyst
    # Responsible for reading code, finding bugs, and saving the report.
    analyst = AssistantAgent(
        name="Analyst",
        model_client=model_client,
        tools=all_tools,
        system_message=f"""
        You are a Senior Code Reviewer.
        1. Read the files identified by the Navigator using `read_file` (repo is '{repo_name}').
        2. Critically analyze the code for:
           - Logic bugs
           - Security risks (hardcoded keys, injection flaws)
           - Performance issues
        3. Construct a detailed Markdown report.
        4. Call `save_report` to save it as IMPROVEMENTS.md.
        5. AFTER saving, say "TERMINATE".
        """
    )

    # 4. RUN THE TEAM
    team = RoundRobinGroupChat(
        participants=[navigator, analyst], 
        termination_condition=TextMentionTermination("TERMINATE"),
        max_turns=12
    )

    print("\n🚀 Agents launched! Monitoring progress...\n")
    
    await Console(team.run_stream(task=f"Analyze {repo_name} and produce a report."))

    # 5. FINAL CHECK
    if os.path.exists("IMPROVEMENTS.md"):
        print("\n✅ DONE! Open 'IMPROVEMENTS.md' to see the results.")
    else:
        print("\n❌ finished, but 'IMPROVEMENTS.md' was not found.")

if __name__ == "__main__":
    asyncio.run(main())