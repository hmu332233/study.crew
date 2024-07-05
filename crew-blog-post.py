import os
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_MODEL_NAME"]="gpt-4o"

from crewai import Crew, Agent, Task, Process
from crewai_tools import SerperDevTool
search_tool = SerperDevTool()

# 역할과 도구를 가진 에이전트 정의
researcher = Agent(
  role='Senior Researcher',
  goal='Uncover groundbreaking technologies in {topic}',
  verbose=True,
  memory=True,
  backstory=(
    "Driven by curiosity, you're at the forefront of"
    "innovation, eager to explore and share knowledge that could change"
    "the world."
  ),
  tools=[search_tool],
  allow_delegation=True
)

# Creating a writer agent with custom tools and delegation capability
writer = Agent(
  role='Writer',
  goal='Narrate compelling tech stories about {topic}',
  verbose=True,
  memory=True,
  backstory=(
    "With a flair for simplifying complex topics, you craft"
    "engaging narratives that captivate and educate, bringing new"
    "discoveries to light in an accessible manner."
  ),
  tools=[search_tool],
  allow_delegation=False
)

# 한국어 번역가 에이전트 정의
translator = Agent(
  role='Translator',
  goal='Translate the final report into Korean',
  verbose=True,
  memory=True,
  backstory=(
    "Fluent in both English and Korean, you have a knack for translating"
    "technical content accurately while maintaining readability and nuance."
  ),
  tools=[],
  allow_delegation=False
)

# Research task
research_task = Task(
  description=(
    "Identify the next big trend in {topic}."
    "Focus on identifying pros and cons and the overall narrative."
    "Your final report should clearly articulate the key points,"
    "its market opportunities, and potential risks."
  ),
  expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
  tools=[search_tool],
  agent=researcher,
)

# Writing task with language model configuration
write_task = Task(
  description=(
    "Compose an insightful article on {topic}."
    "Focus on the latest trends and how it's impacting the industry."
    "This article should be easy to understand, engaging, and positive."
  ),
  expected_output='A 4 paragraph article on {topic} advancements formatted as markdown.',
  tools=[search_tool],
  agent=writer,
  async_execution=False,
  output_file='new-blog-post.md'  # Example of output customization
)

# 번역 작업 정의
translate_task = Task(
  description=(
    "Translate the final report and article into Korean."
    "Ensure that the translation maintains the original meaning and readability."
  ),
  expected_output='한국어 번역 블로그 포스트',
  tools=[],
  agent=translator,
  async_execution=False,
  input_files=['new-blog-post.md']
)

# 기술 중심의 팀 구성
crew = Crew(
  agents=[researcher, writer, translator],
  tasks=[research_task, write_task, translate_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

# 작업 실행 프로세스 시작
result = crew.kickoff(inputs={'topic': 'gpt5에 대한 소식'})
print(result)