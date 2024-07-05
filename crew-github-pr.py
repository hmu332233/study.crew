import os
from crewai import Agent, Task, Crew, Process
from github import Github
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_MODEL_NAME"]="gpt-4o"

# GitHub setup
github_token = os.getenv('GITHUB_TOKEN')
g = Github(github_token)
repo = g.get_repo("hmu332233/playground.github-action")  # Replace with your repo

# Function to get PR details
def get_pr_details(pr_number):
    pr = repo.get_pull(pr_number)
    files = pr.get_files()
    diff = ""
    for file in files:
        diff += f"File: {file.filename}\n"
        diff += f"Diff:\n{file.patch}\n\n"
    return {
        "title": pr.title,
        "description": pr.body,
        "diff": diff
    }

# Function to get PR details
def get_pr_details(pr_number):
    pr = repo.get_pull(pr_number)
    files = pr.get_files()
    diff = ""
    for file in files:
        diff += f"File: {file.filename}\n"
        diff += f"Diff:\n{file.patch}\n\n"
    return {
        "title": pr.title,
        "description": pr.body,
        "diff": diff
    }

# Define Agents
code_quality_expert = Agent(
    name="Code Quality Expert",
    role="Analyzes code for best practices, readability, and maintainability",
    backstory="Senior developer with years of experience in code reviews and maintaining large codebases",
    goal="Ensure the code adheres to best practices and is easily maintainable",
    verbose=True
)

security_expert = Agent(
    name="Security Expert",
    role="Identifies potential security vulnerabilities in the code",
    backstory="Cybersecurity specialist with a focus on secure coding practices",
    goal="Identify and suggest fixes for any security issues in the code",
    verbose=True
)

performance_expert = Agent(
    name="Performance Expert",
    role="Analyzes code for performance bottlenecks and optimization opportunities",
    backstory="Software engineer specializing in high-performance computing and optimization techniques",
    goal="Identify performance issues and suggest optimizations",
    verbose=True
)

architecture_expert = Agent(
    name="Architecture Expert",
    role="Evaluates the overall design and architecture of the code",
    backstory="Senior software architect with experience in designing large-scale systems",
    goal="Ensure the code follows good architectural principles and fits well with the existing system",
    verbose=True
)

javascript_expert = Agent(
    name="JavaScript Expert",
    role="Analyzes JavaScript code for best practices and modern patterns",
    backstory="Senior JavaScript developer with expertise in modern frameworks and ECMAScript standards",
    goal="Ensure JavaScript code is efficient, follows best practices, and uses modern patterns. Also, guide developers to use global.debug instead of console.log",
    verbose=True
)

review_summarizer = Agent(
    name="Review Summarizer",
    role="Compiles and summarizes all review feedback",
    backstory="Technical writer with experience in creating concise and actionable summaries",
    goal="Create a clear, concise summary of all review feedback for the PR author",
    verbose=True
)

# Create Crew
def create_pr_review_crew(pr_number):
    pr_details = get_pr_details(pr_number)
    
    tasks = [
        Task(
            description=f"Review this Pull Request:\n\nTitle: {pr_details['title']}\n\nDescription: {pr_details['description']}\n\nDiff:\n{pr_details['diff']}\n\nFocus on code quality, readability, and maintainability. Provide detailed feedback.",
            agent=code_quality_expert,
            expected_output="A detailed review of code quality, readability, and maintainability aspects of the PR."
        ),
        Task(
            description=f"Review this Pull Request:\n\nTitle: {pr_details['title']}\n\nDescription: {pr_details['description']}\n\nDiff:\n{pr_details['diff']}\n\nFocus on identifying potential security vulnerabilities. Provide detailed feedback.",
            agent=security_expert,
            expected_output="A comprehensive security analysis of the PR, highlighting potential vulnerabilities and suggesting fixes."
        ),
        Task(
            description=f"Review this Pull Request:\n\nTitle: {pr_details['title']}\n\nDescription: {pr_details['description']}\n\nDiff:\n{pr_details['diff']}\n\nFocus on performance implications and optimization opportunities. Provide detailed feedback.",
            agent=performance_expert,
            expected_output="A detailed performance review of the PR, identifying bottlenecks and suggesting optimizations."
        ),
        Task(
            description=f"Review this Pull Request:\n\nTitle: {pr_details['title']}\n\nDescription: {pr_details['description']}\n\nDiff:\n{pr_details['diff']}\n\nEvaluate the overall design and architecture. Provide detailed feedback.",
            agent=architecture_expert,
            expected_output="An architectural review of the PR, assessing its alignment with system design principles and suggesting improvements."
        ),
        Task(
            description=f"Review this Pull Request:\n\nTitle: {pr_details['title']}\n\nDescription: {pr_details['description']}\n\nDiff:\n{pr_details['diff']}\n\nFocus on JavaScript best practices, modern patterns, and efficiency. Specifically, recommend using global.debug instead of console.log. Provide detailed feedback.",
            agent=javascript_expert,
            expected_output="A detailed review of JavaScript code, focusing on best practices, modern patterns, and the use of global.debug instead of console.log."
        ),
        Task(
            description="Compile and summarize all the feedback from the other experts. Create a concise, actionable summary for the PR author.",
            agent=review_summarizer,
            expected_output="A concise summary of all expert reviews, providing actionable feedback for the PR author."
        )
    ]
    
    return Crew(
        agents=[code_quality_expert, security_expert, javascript_expert, review_summarizer],
        tasks=tasks,
        process=Process.sequential
    )

# Main execution
if __name__ == "__main__":
    pr_number = 6  # Replace with the actual PR number
    pr_review_crew = create_pr_review_crew(pr_number)
    result = pr_review_crew.kickoff()
    
    print("Final Review Summary:")
    print(result)

    # Optionally, you could post this summary back to the GitHub PR
    # pr = repo.get_pull(pr_number)
    # pr.create_issue_comment(result)