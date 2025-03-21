from github import Github
import datetime
import os

# Secure way to load GitHub token from an environment variable
TOKEN = os.getenv("GITHUB_TOKEN")  # Make sure to set this variable before running the script
TIME_WINDOW = 365  # Default: 1 year

def get_repositories():
    """Reads the list of repositories from masterRepoList.txt"""
    with open("masterRepoList.txt", "r") as file:
        return [line.strip() for line in file.readlines()]

def fetch_stale_branches(repo, gh):
    """Fetches branches older than the specified time window."""
    try:
        repository = gh.get_repo(repo)
        branches = repository.get_branches()
        stale_branches = []
        
        one_year_ago = datetime.datetime.now() - datetime.timedelta(days=TIME_WINDOW)
        for branch in branches:
            commit = repository.get_branch(branch.name).commit
            commit_date = commit.commit.author.date.replace(tzinfo=None)
            if commit_date < one_year_ago:
                stale_branches.append(branch.name)
        
        return stale_branches
    except Exception as e:
        print(f"Error fetching branches for {repo}: {e}")
        return []

def delete_branches(repo, stale_branches, gh):
    """Deletes user-approved stale branches from the repository."""
    repository = gh.get_repo(repo)
    for branch in stale_branches:
        print(f"Deleting branch: {branch}")
        repository.get_git_ref(f'heads/{branch}').delete()
    
    print("Deletion complete.")

def generate_summary(repo, stale_branches):
    """Generates a summary of deleted branches."""
    with open("summary.txt", "a") as file:
        file.write(f"Repo: {repo}\n")
        file.write(f"Deleted Branches: {', '.join(stale_branches)}\n\n")

def main():
    """Main function to execute repo cleanup."""
    if not TOKEN:
        print("Error: GitHub Token is missing. Set it using 'export GITHUB_TOKEN=your_token' or 'setx GITHUB_TOKEN your_token'")
        return

    gh = Github(TOKEN)
    repos = get_repositories()
    
    for repo in repos:
        print(f"Processing {repo}")
        stale_branches = fetch_stale_branches(repo, gh)
        if not stale_branches:
            print(f"No stale branches in {repo}")
            continue
        
        print(f"Stale branches in {repo}: {', '.join(stale_branches)}")
        confirm = input("Do you want to delete these branches? (yes/no): ")
        
        if confirm.lower() == "yes":
            delete_branches(repo, stale_branches, gh)
            generate_summary(repo, stale_branches)
    
    print("Summary generated in summary.txt")

if __name__ == "__main__":
    main()
