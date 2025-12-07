from outils import chunk_report
import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,SystemMessage
from prompts import summarize_chunk_instructions,report_test, rittenhouse_synthesis_instructions
from langchain_core.prompts import ChatPromptTemplate
import time
from classes_langchain import Chunk,ReportBlocks
from typing import List, Optional
from langchain_core.runnables import RunnableLambda


load_dotenv()
GEMINI_API=os.getenv('GEMINI_API')
DIRECTORY=os.getenv('DIRECTORY')
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",api_key=GEMINI_API,max_retries=1)
# llm=ChatOllama(model="llama2-uncensored:latest")

def split_and_map_chunks(text):
    chunks=chunk_report(text)
    return [{"chunk":e,}for e in chunks]


def make_map_runnable():
    structured_llm =llm.with_structured_output(Chunk)
    prompt = ChatPromptTemplate.from_messages([
        ("system",summarize_chunk_instructions),
        ("human","{chunk}")
    ])

    return prompt| structured_llm

def reduce_input(analyses:List[Chunk]):
    return {"analyses":[a.model_dump()]for a in analyses}

def make_reduce_runnable():
    structured_llm = llm.with_structured_output(ReportBlocks)
    reduce_prompt = ChatPromptTemplate.from_messages([
        (
            "system",rittenhouse_synthesis_instructions
        ),
        (
            "human","here are the chunks {analyses}"
        )
    ])
    prepare = RunnableLambda(reduce_input)
    return prepare | reduce_prompt | structured_llm

def build_pipeline():
    splitter = RunnableLambda(split_and_map_chunks)
    map_runnable = make_map_runnable()
    parallel_map= map_runnable.map()
    reduce_runnable = make_reduce_runnable()
    pipeline = splitter | parallel_map | reduce_runnable

    return pipeline

# pipeline = build_pipeline()
# final_report : ReportBlocks = pipeline.invoke(report_test)

# print(final_report.model_dump(indent=2))



dict_chunks = chunk_report(report_test)
structured_llm=llm.with_structured_output(Chunk)

responses=[]
idx = 0
for i in dict_chunks:
    response = structured_llm.invoke(
        [
            SystemMessage(content=summarize_chunk_instructions),
            HumanMessage(content=i)
        ]
    )
    responses.append({"chunk_index":idx,
                      "chunk":response.chunk})
    idx+=1
    time.sleep(40)
    print("response chunk: ",response.chunk)


response2 = llm.invoke(
    [
        SystemMessage(content=rittenhouse_synthesis_instructions),
        HumanMessage(content=f"here is the report: {responses}")
    ]
)

print(response2.content)

