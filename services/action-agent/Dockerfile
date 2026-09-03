FROM python:3.11-slim
WORKDIR /app
RUN pip install pydantic langchain-community langgraph
COPY ./app ./app
CMD ["tail", "-f", "/dev/null"]
