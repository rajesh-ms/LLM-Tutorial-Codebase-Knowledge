import dotenv
import os
import argparse
from flow import create_tutorial_flow

dotenv.load_dotenv()

DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "*Dockerfile",
    "*Makefile", "*.yaml", "*.yml",
}

DEFAULT_EXCLUDE_PATTERNS = {
    "assets/*", "data/*", "images/*", "public/*", "static/*", "temp/*",
    "*docs/*",
    "*venv/*",
    "*.venv/*",
    "*test*",
    "*tests/*",
    "*examples/*",
    "v1/*",
    "*dist/*",
    "*build/*",
    "*experimental/*",
    "*deprecated/*",
    "*misc/*",
    "*legacy/*",
    ".git/*", ".github/*", ".next/*", ".vscode/*",
    "*obj/*",
    "*bin/*",
    "*node_modules/*",
    "*.log"
}

AZURE_SAAS_MODULES = [
    "Saas.Admin",
    "Saas.Application",
    "Saas.Identity",
    "Saas.Lib",
    "Saas.SignupAdministration",
]

def main():
    parser = argparse.ArgumentParser(description="Generate a tutorial for a GitHub codebase or local directory.")

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo", help="URL of the public GitHub repository.")
    source_group.add_argument("--dir", help="Path to local directory.")

    parser.add_argument("-n", "--name", help="Project name (optional, derived from repo/directory if omitted).")
    parser.add_argument("-t", "--token", help="GitHub personal access token (optional, reads from GITHUB_TOKEN env var if not provided).")
    parser.add_argument("-o", "--output", default="output", help="Base directory for output (default: ./output).")
    parser.add_argument("-i", "--include", nargs="+", help="Include file patterns (e.g. '*.py' '*.js'). Defaults to common code files if not specified.")
    parser.add_argument("-e", "--exclude", nargs="+", help="Exclude file patterns (e.g. 'tests/*' 'docs/*'). Defaults to test/build directories if not specified.")
    parser.add_argument("-s", "--max-size", type=int, default=100000, help="Maximum file size in bytes (default: 100000, about 100KB).")
    parser.add_argument("--language", default="english", help="Language for the generated tutorial (default: english)")
    parser.add_argument("--no-cache", action="store_true", help="Disable LLM response caching (default: caching enabled)")
    parser.add_argument("--max-abstractions", type=int, default=10, help="Maximum number of abstractions to identify (default: 10)")

    args = parser.parse_args()

    github_token = None
    if args.repo:
        github_token = args.token or os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GitHub token provided. You might hit rate limits for public repositories.")

    for module in AZURE_SAAS_MODULES:
        repo_url = f"{args.repo}/tree/main/src/{module}"
        output_dir = os.path.join(args.output, module)

        shared = {
            "repo_url": repo_url,
            "local_dir": None,
            "project_name": f"{args.name}-{module}" if args.name else module,
            "github_token": github_token,
            "output_dir": output_dir,
            "include_patterns": set(args.include) if args.include else DEFAULT_INCLUDE_PATTERNS,
            "exclude_patterns": set(args.exclude) if args.exclude else DEFAULT_EXCLUDE_PATTERNS,
            "max_file_size": args.max_size,
            "language": args.language,
            "use_cache": not args.no_cache,
            "max_abstraction_num": args.max_abstractions,
            "files": [],
            "abstractions": [],
            "relationships": {},
            "chapter_order": [],
            "chapters": [],
            "final_output_dir": None
        }

        print(f"Starting tutorial generation for: {repo_url} in {args.language.capitalize()} language")
        print(f"LLM caching: {'Disabled' if args.no_cache else 'Enabled'}")

        tutorial_flow = create_tutorial_flow()
        tutorial_flow.run(shared)

if __name__ == "__main__":
    main()
