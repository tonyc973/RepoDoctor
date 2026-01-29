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

# --- SAFETY LIMITS ---
MAX_FILE_ZS = 20000  # Max characters to read per file
IGNORED_EXTENSIONS = {'.lock', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.zip'}
IGNORED_FILES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'composer.lock'}

@mcp.tool()
def list_files(repo_name: str, path: str = "") -> str:
    """
    Lists files in a specific directory.
    Args:
        repo_name: "owner/repo"
        path: Folder path (leave empty "" for root)
    """
    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(path)
        
        if not isinstance(contents, list):
            return f"Error: {path} is a file, not a directory."
            
        file_list = []
        for c in contents:
            # Skip massive lock files in the listing itself to discourage agents
            if c.name in IGNORED_FILES:
                continue
                
            type_label = "[DIR]" if c.type == "dir" else "[FILE]"
            file_list.append(f"{type_label} {c.path}")
            
        return "\n".join(file_list)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def read_file(repo_name: str, file_path: str) -> str:
    """
    Reads a file. Truncates if too large.
    Args:
        repo_name: "owner/repo"
        file_path: Path to file
    """
    # 1. Pre-check extension
    _, ext = os.path.splitext(file_path)
    if ext in IGNORED_EXTENSIONS or os.path.basename(file_path) in IGNORED_FILES:
        return f"Error: I cannot read {file_path} because it is a binary or lock file."

    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(file_path)
        
        # 2. Decode
        raw_content = contents.decoded_content.decode("utf-8")
        
        # 3. SAFETY TRUNCATION
        if len(raw_content) > MAX_FILE_ZS:
            preview =raw_content[:MAX_FILE_ZS]
            return f"{preview}\n\n... [TRUNCATED: File too large. Only first {MAX_FILE_ZS} chars shown] ..."
            
        return raw_content
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run()