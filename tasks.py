from crewai import Task
from agents import researcher, analyst, writer, reviewer
from database import get_research_history

def get_relevant_history(query):
    try:
        history = get_research_history()
        relevant = []
        query_words = [w.lower() for w in query.split() if len(w) > 3]
        for item in history[-10:]:
            past_query = item['query'].lower()
            if any(word in past_query for word in query_words):
                snippet = item['report'][:400]
                relevant.append(f"Previous research on '{item['query']}':\n{snippet}")
        return '\n\n'.join(relevant[:2]) if relevant else ""
    except:
        return ""

def create_tasks(query, pdf_content=""):
    memory_context = get_relevant_history(query)

    memory_section = ""
    if memory_context:
        memory_section = f"--- MEMORY: Related past research ---\n{memory_context}\n--- END MEMORY ---\n"

    pdf_section = ""
    if pdf_content:
        pdf_section = f"--- PDF CONTENT ---\n{pdf_content}\n--- END PDF ---\n"
    else:
        pdf_section = "Search the web for relevant information."

    research_task = Task(
        description=f"""Research this topic thoroughly: {query}

{memory_section}

{pdf_section}

Find 3-5 credible sources with full URLs.
Note key facts, statistics, and insights from each source.
Identify the target audience and scope of this topic.""",
        expected_output="A detailed list of findings with sources, URLs, target audience and scope",
        agent=researcher
    )

    analysis_task = Task(
        description=f"""Analyse the research findings on: {query}
Identify:
1. The purpose and objective of this research
2. Target audience
3. Scope and boundaries
4. Top 5 key themes and insights
5. Important statistics and facts
6. Methodology used to gather information""",
        expected_output="A structured analysis with purpose, audience, scope, themes and methodology",
        agent=analyst,
        context=[research_task]
    )

    writing_task = Task(
        description=f"""Write a comprehensive professional research report on: {query}
Use EXACTLY this structure:

## Cover
Title: [Report Title]
Topic: {query}
Date: [Today's Date]

## Table of Contents
1. Executive Summary
2. Purpose and Scope
3. Introduction
4. Methodology
5. Key Findings
6. Detailed Analysis
7. Data and Statistics
8. Conclusion and Recommendations
9. References

## Executive Summary
(3-4 sentence overview)

## Purpose and Scope
Research Objective: (clear question being answered)
Target Audience: (who this report is for)
Scope: (what is included)
Out of Scope: (what is excluded)

## Introduction
(Background and context)

## Methodology
Sources Used: (list databases, websites, tools)
Research Approach: (how research was conducted)
Limitations: (any limitations)

## Key Findings
(Bullet points of top discoveries)

## Detailed Analysis
(In-depth discussion with evidence and citations)

## Data and Statistics
(Key numbers, percentages, market data)

## Conclusion and Recommendations
Conclusion: (summary)
Recommendations:
1. (first recommendation)
2. (second recommendation)
3. (third recommendation)

## References
* [Source Name] - [Full URL]
* [Source Name] - [Full URL]

Use formal language and cite sources inline.""",
        expected_output="A complete professional research report with ALL sections filled",
        agent=writer,
        context=[analysis_task]
    )

    review_task = Task(
        description=f"""Review and polish the research report on: {query}
Check ALL sections are present and complete.
Ensure References section has URLs.
Ensure Data and Statistics section has real numbers.
Return the final polished version with ALL sections intact.""",
        expected_output="A final polished research report with all sections and references",
        agent=reviewer,
        context=[writing_task]
    )

    return [research_task, analysis_task, writing_task, review_task]