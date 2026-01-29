import os
from fastmcp import FastMCP
from github import Github
from dotenv import load_dotenv

# Load keys
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("❌ Error: GITHUB_TOKEN not found in .env")

mcp = FastMCP("GitHubServer")
g = Github(token)

@mcp.tool()
def list_files(repo_name: str, path: str = "") -> str:
    """
    Lists files in a specific directory of a GitHub repo.
    Args:
        repo_name: "owner/repo" (e.g., 'pallets/flask')
        path: Folder path (leave empty "" for root)
    """
    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        # Handle case where path points to a file, not a dir
        if not isinstance(contents, list):
            return f"Error: {path} is a file, not a directory."
            
        file_list = []
        for c in contents:
            type_label = "[DIR]" if c.type == "dir" else "[FILE]"
            file_list.append(f"{type_label} {c.path}")
        return "\n".join(file_list)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file(repo_name: str, file_path: str) -> str:
    """Reads the content of a specific file."""
    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(file_path)
        return contents.decoded_content.decode("utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run()