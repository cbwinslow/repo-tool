"""
Main entry point for RepoTool
"""
from repo_tool.tui.app import RepoToolApp

def main():
    """Run the RepoTool application"""
    app = RepoToolApp()
    app.run()

if __name__ == "__main__":
    main()

