FROM python:3.11-slim
WORKDIR /app
RUN pip install pydantic langchain-community langgraph
COPY ./app ./app
# Agents are python scripts right now, but could be exposed via FastAPI. We'll run them as a dummy long-running process for now.
CMD ["tail", "-f", "/dev/null"]
