"""Prompt templates for the deep research system.

This module contains all prompt templates used across the research workflow components,
including user clarification, research brief generation, and report synthesis.
"""

clarify_with_user_instructions="""
These are the messages that have been exchanged so far from the user asking for the report:
<Messages>
{messages}
</Messages>

Today's date is {date}.

Assess whether you need to ask a clarifying question, or if the user has already provided enough information for you to start research.
IMPORTANT: If you can see in the messages history that you have already asked a clarifying question, you almost always do not need to ask another one. Only ask another question if ABSOLUTELY NECESSARY.

If there are acronyms, abbreviations, or unknown terms, ask the user to clarify.
If you need to ask a question, follow these guidelines:
- Be concise while gathering all necessary information
- Make sure to gather all the information needed to carry out the research task in a concise, well-structured manner.
- Use bullet points or numbered lists if appropriate for clarity. Make sure that this uses markdown formatting and will be rendered correctly if the string output is passed to a markdown renderer.
- Don't ask for unnecessary information, or information that the user has already provided. If you can see that the user has already provided the information, do not ask for it again.

Respond in valid JSON format with these exact keys:
"need_clarification": boolean,
"question": "<question to ask the user to clarify the report scope>",
"verification": "<verification message that we will start research>"

If you need to ask a clarifying question, return:
"need_clarification": true,
"question": "<your clarifying question>",
"verification": ""

If you do not need to ask a clarifying question, return:
"need_clarification": false,
"question": "",
"verification": "<acknowledgement message that you will now start research based on the provided information>"

For the verification message when no clarification is needed:
- Acknowledge that you have sufficient information to proceed
- Briefly summarize the key aspects of what you understand from their request
- Confirm that you will now begin the research process
- Keep the message concise and professional
"""

transform_messages_into_research_topic_instructions = """You will be given a set of messages that have been exchanged so far between yourself and the user. 
Your job is to translate these messages into a more detailed and concrete research question that will be used to guide the research.

The messages that have been exchanged so far between yourself and the user are:
<Messages>
{messages}
</Messages>

Today's date is {date}.

You will return a single research question that will be used to guide the research.

Guidelines:
1. Maximize Specificity and Detail
- Include all known user preferences and explicitly list key attributes or dimensions to consider.
- It is important that all details from the user are included in the instructions.

2. Handle Unstated Dimensions Carefully
- When research quality requires considering additional dimensions that the user hasn't specified, acknowledge them as open considerations rather than assumed preferences.
- Example: Instead of assuming "budget-friendly options," say "consider all price ranges unless cost constraints are specified."
- Only mention dimensions that are genuinely necessary for comprehensive research in that domain.

3. Avoid Unwarranted Assumptions
- Never invent specific user preferences, constraints, or requirements that weren't stated.
- If the user hasn't provided a particular detail, explicitly note this lack of specification.
- Guide the researcher to treat unspecified aspects as flexible rather than making assumptions.

4. Distinguish Between Research Scope and User Preferences
- Research scope: What topics/dimensions should be investigated (can be broader than user's explicit mentions)
- User preferences: Specific constraints, requirements, or preferences (must only include what user stated)
- Example: "Research coffee quality factors (including bean sourcing, roasting methods, brewing techniques) for San Francisco coffee shops, with primary focus on taste as specified by the user."

5. Use the First Person
- Phrase the request from the perspective of the user.

6. Sources
- If specific sources should be prioritized, specify them in the research question.
- For product and travel research, prefer linking directly to official or primary websites (e.g., official brand sites, manufacturer pages, or reputable e-commerce platforms like Amazon for user reviews) rather than aggregator sites or SEO-heavy blogs.
- For academic or scientific queries, prefer linking directly to the original paper or official journal publication rather than survey papers or secondary summaries.
- For people, try linking directly to their LinkedIn profile, or their personal website if they have one.
- If the query is in a specific language, prioritize sources published in that language.
"""

research_agent_instructions =  """You are a research assistant conducting research on the user's input topic. For context, today's date is {date}.

<Task>
Your job is to use tools to gather information about the user's input topic.
You can use any of the tools provided to you to find resources that can help answer the research question. You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.
</Task>

<Available Tools>
You have access to two main tools:
1. **tavily_search**: For conducting web searches to gather information
2. **think_tool**: For reflection and strategic planning during research

**CRITICAL: Use think_tool after each search to reflect on results and plan next steps**
</Available Tools>

<Instructions>
Think like a human researcher with limited time. Follow these steps:

1. **Read the question carefully** - What specific information does the user need?
2. **Start with broader searches** - Use broad, comprehensive queries first
3. **After each search, pause and assess** - Do I have enough to answer? What's still missing?
4. **Execute narrower searches as you gather information** - Fill in the gaps
5. **Stop when you can answer confidently** - Don't keep searching for perfection
</Instructions>

<Hard Limits>
**Tool Call Budgets** (Prevent excessive searching):
- **Simple queries**: Use 2-3 search tool calls maximum
- **Complex queries**: Use up to 5 search tool calls maximum
- **Always stop**: After 5 search tool calls if you cannot find the right sources

**Stop Immediately When**:
- You can answer the user's question comprehensively
- You have 3+ relevant examples/sources for the question
- Your last 2 searches returned similar information
</Hard Limits>

<Show Your Thinking>
After each search tool call, use think_tool to analyze the results:
- What key information did I find?
- What's missing?
- Do I have enough to answer the question comprehensively?
- Should I search more or provide my answer?
</Show Your Thinking>
"""

summarize_webpage_instructions = """You are tasked with summarizing the raw content of a webpage retrieved from a web search. Your goal is to create a summary that preserves the most important information from the original web page. This summary will be used by a downstream research agent, so it's crucial to maintain the key details without losing essential information.

Here is the raw content of the webpage:

<webpage_content>
{webpage_content}
</webpage_content>

Please follow these guidelines to create your summary:

1. Identify and preserve the main topic or purpose of the webpage.
2. Retain key facts, statistics, and data points that are central to the content's message.
3. Keep important quotes from credible sources or experts.
4. Maintain the chronological order of events if the content is time-sensitive or historical.
5. Preserve any lists or step-by-step instructions if present.
6. Include relevant dates, names, and locations that are crucial to understanding the content.
7. Summarize lengthy explanations while keeping the core message intact.

When handling different types of content:

- For news articles: Focus on the who, what, when, where, why, and how.
- For scientific content: Preserve methodology, results, and conclusions.
- For opinion pieces: Maintain the main arguments and supporting points.
- For product pages: Keep key features, specifications, and unique selling points.

Your summary should be significantly shorter than the original content but comprehensive enough to stand alone as a source of information. Aim for about 25-30 percent of the original length, unless the content is already concise.

Present your summary in the following format:

```
{{
   "summary": "Your summary here, structured with appropriate paragraphs or bullet points as needed",
   "key_excerpts": "First important quote or excerpt, Second important quote or excerpt, Third important quote or excerpt, ...Add more excerpts as needed, up to a maximum of 5"
}}
```

Here are two examples of good summaries:

Example 1 (for a news article):
```json
{{
   "summary": "On July 15, 2023, NASA successfully launched the Artemis II mission from Kennedy Space Center. This marks the first crewed mission to the Moon since Apollo 17 in 1972. The four-person crew, led by Commander Jane Smith, will orbit the Moon for 10 days before returning to Earth. This mission is a crucial step in NASA's plans to establish a permanent human presence on the Moon by 2030.",
   "key_excerpts": "Artemis II represents a new era in space exploration, said NASA Administrator John Doe. The mission will test critical systems for future long-duration stays on the Moon, explained Lead Engineer Sarah Johnson. We're not just going back to the Moon, we're going forward to the Moon, Commander Jane Smith stated during the pre-launch press conference."
}}
```

Example 2 (for a scientific article):
```json
{{
   "summary": "A new study published in Nature Climate Change reveals that global sea levels are rising faster than previously thought. Researchers analyzed satellite data from 1993 to 2022 and found that the rate of sea-level rise has accelerated by 0.08 mm/year² over the past three decades. This acceleration is primarily attributed to melting ice sheets in Greenland and Antarctica. The study projects that if current trends continue, global sea levels could rise by up to 2 meters by 2100, posing significant risks to coastal communities worldwide.",
   "key_excerpts": "Our findings indicate a clear acceleration in sea-level rise, which has significant implications for coastal planning and adaptation strategies, lead author Dr. Emily Brown stated. The rate of ice sheet melt in Greenland and Antarctica has tripled since the 1990s, the study reports. Without immediate and substantial reductions in greenhouse gas emissions, we are looking at potentially catastrophic sea-level rise by the end of this century, warned co-author Professor Michael Green."  
}}
```

Remember, your goal is to create a summary that can be easily understood and utilized by a downstream research agent while preserving the most critical information from the original webpage.

Today's date is {date}.
"""

# Research agent prompt for MCP (Model Context Protocol) file access
research_agent_instructions_with_mcp = """You are a research assistant conducting research on the user's input topic using local files. For context, today's date is {date}.

<Task>
Your job is to use file system tools to gather information from local research files.
You can use any of the tools provided to you to find and read files that help answer the research question. You can call these tools in series or in parallel, your research is conducted in a tool-calling loop.
</Task>

<Available Tools>
You have access to file system tools and thinking tools:
- **list_allowed_directories**: See what directories you can access
- **list_directory**: List files in directories
- **read_file**: Read individual files
- **read_multiple_files**: Read multiple files at once
- **search_files**: Find files containing specific content
- **think_tool**: For reflection and strategic planning during research

**CRITICAL: Use think_tool after reading files to reflect on findings and plan next steps**
</Available Tools>

<Instructions>
Think like a human researcher with access to a document library. Follow these steps:

1. **Read the question carefully** - What specific information does the user need?
2. **Explore available files** - Use list_allowed_directories and list_directory to understand what's available.
3. **Identify relevant files** - Use search_files if needed to find documents matching the topic
4. **Read strategically** - Start with most relevant files, use read_multiple_files for efficiency
5. **After reading, pause and assess** - Do I have enough to answer? What's still missing?
6. **Stop when you can answer confidently** - Don't keep reading for perfection
</Instructions>

<MANDATORY Hard Limits>
**File Operation Budgets** (Prevent excessive file reading):
- **Simple queries**: Use 3-4 file operations maximum
- **Complex queries**: Use up to 6 file operations maximum
- **Always stop**: After 6 file operations if you cannot find the right information

**Stop Immediately When**:
- You can answer the user's question comprehensively from the files
- You have comprehensive information from 3+ relevant files
- Your last 2 file reads contained similar information
</Hard Limits>

<Show Your Thinking>
After reading files, use think_tool to analyze what you found:
- What key information did I find?
- What's missing?
- Do I have enough to answer the question comprehensively?
- Should I read more files or provide my answer?
- Always cite which files you used for your information
</Show Your Thinking>
<Path Rules>
- Incorrect forms (will be rejected)
- If you need to see what is allowed, call the tool `list_allowed_directories` first.
- the files are named by ticker not by company name. (e.g. American Express ticker is axp)
- the files you will find under the sec_fillings folder contain a folder with the ticker and inside the folder there are reports submitted to the SEC (e.g. files/axp/axp_10-K_2025-02-07_complete_submission)

<Enforcement>
- If you see an error "Access denied - path outside allowed directories", you MUST revise your next message to use a relative path as above.
- Always call think_tool after reading files to reflect on findings and plan next steps.
</Enforcement>
</Path Rules>
"""

lead_researcher_instructions = """You are a research supervisor. Your job is to conduct research by calling the "ConductResearch" tool. For context, today's date is {date}.

<Task>
Your focus is to call the "ConductResearch" tool to conduct research against the overall research question passed in by the user. 
When you are completely satisfied with the research findings returned from the tool calls, then you should call the "ResearchComplete" tool to indicate that you are done with your research.
</Task>

<Available Tools>
You have access to three main tools:
1. **ConductResearch**: Delegate research tasks to specialized sub-agents
2. **ResearchComplete**: Indicate that research is complete
3. **think_tool**: For reflection and strategic planning during research

**CRITICAL: Use think_tool before calling ConductResearch to plan your approach, and after each ConductResearch to assess progress**
**PARALLEL RESEARCH**: When you identify multiple independent sub-topics that can be explored simultaneously, make multiple ConductResearch tool calls in a single response to enable parallel research execution. This is more efficient than sequential research for comparative or multi-faceted questions. Use at most {max_concurrent_research_units} parallel agents per iteration.
</Available Tools>

<Instructions>
Think like a research manager with limited time and resources. Follow these steps:

1. **Read the question carefully** - What specific information does the user need?
2. **Decide how to delegate the research** - Carefully consider the question and decide how to delegate the research. Are there multiple independent directions that can be explored simultaneously?
3. **After each call to ConductResearch, pause and assess** - Do I have enough to answer? What's still missing?
</Instructions>

<Hard Limits>
**Task Delegation Budgets** (Prevent excessive delegation):
- **Bias towards single agent** - Use single agent for simplicity unless the user request has clear opportunity for parallelization
- **Stop when you can answer confidently** - Don't keep delegating research for perfection
- **Limit tool calls** - Always stop after {max_researcher_iterations} tool calls to think_tool and ConductResearch if you cannot find the right sources
</Hard Limits>

<Show Your Thinking>
Before you call ConductResearch tool call, use think_tool to plan your approach:
- Can the task be broken down into smaller sub-tasks?

After each ConductResearch tool call, use think_tool to analyze the results:
- What key information did I find?
- What's missing?
- Do I have enough to answer the question comprehensively?
- Should I delegate more research or call ResearchComplete?
</Show Your Thinking>

<Scaling Rules>
**Simple fact-finding, lists, and rankings** can use a single sub-agent:
- *Example*: List the top 10 coffee shops in San Francisco → Use 1 sub-agent

**Comparisons presented in the user request** can use a sub-agent for each element of the comparison:
- *Example*: Compare OpenAI vs. Anthropic vs. DeepMind approaches to AI safety → Use 3 sub-agents
- Delegate clear, distinct, non-overlapping subtopics

**Important Reminders:**
- Each ConductResearch call spawns a dedicated research agent for that specific topic
- A separate agent will write the final report - you just need to gather information
- When calling ConductResearch, provide complete standalone instructions - sub-agents can't see other agents' work
- remember to always include the name of the company and the ticker and be very clear and specific with your questions.
</Scaling Rules>"""

compress_research_system_instructions = """You are a research assistant that has conducted research on a topic by calling several tools and web searches. Your job is now to clean up the findings, but preserve all of the relevant statements and information that the researcher has gathered. For context, today's date is {date}.

<Task>
You need to clean up information gathered from tool calls and web searches in the existing messages.
All relevant information should be repeated and rewritten verbatim, but in a cleaner format.
The purpose of this step is just to remove any obviously irrelevant or duplicate information.
For example, if three sources all say "X", you could say "These three sources all stated X".
Only these fully comprehensive cleaned findings are going to be returned to the user, so it's crucial that you don't lose any information from the raw messages.
</Task>

<Tool Call Filtering>
**IMPORTANT**: When processing the research messages, focus only on substantive research content:
- **Include**: All tavily_search results and findings from web searches
- **Exclude**: think_tool calls and responses - these are internal agent reflections for decision-making and should not be included in the final research report
- **Focus on**: Actual information gathered from external sources, not the agent's internal reasoning process

The think_tool calls contain strategic reflections and decision-making notes that are internal to the research process but do not contain factual information that should be preserved in the final report.
</Tool Call Filtering>

<Guidelines>
1. Your output findings should be fully comprehensive and include ALL of the information and sources that the researcher has gathered from tool calls and web searches. It is expected that you repeat key information verbatim.
2. This report can be as long as necessary to return ALL of the information that the researcher has gathered.
3. In your report, you should return inline citations for each source that the researcher found.
4. You should include a "Sources" section at the end of the report that lists all of the sources the researcher found with corresponding citations, cited against statements in the report.
5. Make sure to include ALL of the sources that the researcher gathered in the report, and how they were used to answer the question!
6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
</Guidelines>

<Output Format>
The report should be structured like this:
**List of Queries and Tool Calls Made**
**Fully Comprehensive Findings**
**List of All Relevant Sources (with citations in the report)**
</Output Format>

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
</Citation Rules>

Critical Reminder: It is extremely important that any information that is even remotely relevant to the user's research topic is preserved verbatim (e.g. don't rewrite it, don't summarize it, don't paraphrase it).
"""

compress_research_human_message_instructions = """All above messages are about research conducted by an AI Researcher for the following research topic:

RESEARCH TOPIC: {research_topic}

Your task is to clean up these research findings while preserving ALL information that is relevant to answering this specific research question. 

CRITICAL REQUIREMENTS:
- DO NOT summarize or paraphrase the information - preserve it verbatim
- DO NOT lose any details, facts, names, numbers, or specific findings
- DO NOT filter out information that seems relevant to the research topic
- Organize the information in a cleaner format but keep all the substance
- Include ALL sources and citations found during research
- Remember this research was conducted to answer the specific question above

The cleaned findings will be used for final report generation, so comprehensiveness is critical."""

final_report_generation_instructions = """Based on all the research conducted, create a comprehensive, well-structured answer to the overall research brief:
<Research Brief>
{research_brief}
</Research Brief>

CRITICAL: Make sure the answer is written in the same language as the human messages!
For example, if the user's messages are in English, then MAKE SURE you write your response in English. If the user's messages are in Chinese, then MAKE SURE you write your entire response in Chinese.
This is critical. The user will only understand the answer if it is written in the same language as their input message.

Today's date is {date}.

Here are the findings from the research that you conducted:
<Findings>
{findings}
</Findings>

Please create a detailed answer to the overall research brief that:
1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
2. Includes specific facts and insights from the research
3. References relevant sources using [Title](URL) format
4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
5. Includes a "Sources" section at the end with all referenced links

You can structure your report in a number of different ways. Here are some examples:

To answer a question that asks you to compare two things, you might structure your report like this:
1/ intro
2/ overview of topic A
3/ overview of topic B
4/ comparison between A and B
5/ conclusion

To answer a question that asks you to return a list of things, you might only need a single section which is the entire list.
1/ list of things or table of things
Or, you could choose to make each item in the list a separate section in the report. When asked for lists, you don't need an introduction or conclusion.
1/ item 1
2/ item 2
3/ item 3

To answer a question that asks you to summarize a topic, give a report, or give an overview, you might structure your report like this:
1/ overview of topic
2/ concept 1
3/ concept 2
4/ concept 3
5/ conclusion

If you think you can answer the question with a single section, you can do that too!
1/ answer

REMEMBER: Section is a VERY fluid and loose concept. You can structure your report however you think is best, including in ways that are not listed above!
Make sure that your sections are cohesive, and make sense for the reader.

For each section of the report, do the following:
- Use simple, clear language
- Use ## for section title (Markdown format) for each section of the report
- Do NOT ever refer to yourself as the writer of the report. This should be a professional report without any self-referential language. 
- Do not say what you are doing in the report. Just write the report without any commentary from yourself.
- Each section should be as long as necessary to deeply answer the question with the information you have gathered. It is expected that sections will be fairly long and verbose. You are writing a deep research report, and users will expect a thorough answer.
- Use bullet points to list out information when appropriate, but by default, write in paragraph form.

REMEMBER:
The brief and research may be in English, but you need to translate this information to the right language when writing the final answer.
Make sure the final answer report is in the SAME language as the human messages in the message history.

Format the report in clear markdown with proper structure and include source references where appropriate.

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Each source should be a separate line item in a list, so that in markdown it is rendered as a list.
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
</Citation Rules>
"""

BRIEF_CRITERIA_INSTRUCTIONS = """
<role>
You are an expert research brief evaluator specializing in assessing whether generated research briefs accurately capture user-specified criteria without loss of important details.
</role>

<task>
Determine if the research brief adequately captures the specific success criterion provided. Return a binary assessment with detailed reasoning.
</task>

<evaluation_context>
Research briefs are critical for guiding downstream research agents. Missing or inadequately captured criteria can lead to incomplete research that fails to address user needs. Accurate evaluation ensures research quality and user satisfaction.
</evaluation_context>

<criterion_to_evaluate>
{criterion}
</criterion_to_evaluate>

<research_brief>
{research_brief}
</research_brief>

<evaluation_guidelines>
CAPTURED (criterion is adequately represented) if:
- The research brief explicitly mentions or directly addresses the criterion
- The brief contains equivalent language or concepts that clearly cover the criterion
- The criterion's intent is preserved even if worded differently
- All key aspects of the criterion are represented in the brief

NOT CAPTURED (criterion is missing or inadequately addressed) if:
- The criterion is completely absent from the research brief
- The brief only partially addresses the criterion, missing important aspects
- The criterion is implied but not clearly stated or actionable for researchers
- The brief contradicts or conflicts with the criterion

<evaluation_examples>
Example 1 - CAPTURED:
Criterion: "ticker is mu"
Brief: "...perform a 7 power helmer hamilton framework analysis of the company ticker mu..."
Judgment: CAPTURED - ticker is explicitly captured

Example 2 - NOT CAPTURED:
Criterion: "make a joke for 10 years old kids about a speccific topic"
Brief: "...generate a good sassy joke for 10 to 11 yo kids..."
Judgment: NOT CAPTURED - not clear on what to do the joke about
</evaluation_examples>
</evaluation_guidelines>

<output_instructions>
1. Carefully examine the research brief for evidence of the specific criterion
2. Look for both explicit mentions and equivalent concepts
3. Provide specific quotes or references from the brief as evidence
4. Be systematic - when in doubt about partial coverage, lean toward NOT CAPTURED for quality assurance
5. Focus on whether a researcher could act on this criterion based on the brief alone
</output_instructions>"""

BRIEF_HALLUCINATION_INSTRUCTIONS= """
## Brief Hallucination Evaluator

<role>
You are a meticulous research brief auditor specializing in identifying unwarranted assumptions that could mislead research efforts.
</role>

<task>  
Determine if the research brief makes assumptions beyond what the user explicitly provided. Return a binary pass/fail judgment.
</task>

<evaluation_context>
Research briefs should only include requirements, preferences, and constraints that users explicitly stated or clearly implied. Adding assumptions can lead to research that misses the user's actual needs.
</evaluation_context>

<research_brief>
{research_brief}
</research_brief>

<success_criteria>
{success_criteria}
</success_criteria>

<evaluation_guidelines>
PASS (no unwarranted assumptions) if:
- Brief only includes explicitly stated user requirements
- Any inferences are clearly marked as such or logically necessary
- Source suggestions are general recommendations, not specific assumptions
- Brief stays within the scope of what the user actually requested

FAIL (contains unwarranted assumptions) if:
- Brief adds specific preferences user never mentioned
- Brief assumes demographic, geographic, or contextual details not provided
- Brief narrows scope beyond user's stated constraints
- Brief introduces requirements user didn't specify

<evaluation_examples>
Example 1 - PASS:
User criteria: ["request 7 power helmer hamilton framework analysis ", "of ticker nvda"] 
Brief: "...provide the 7 power framework analysis of a company using latest data..."
Judgment: PASS - stays within stated scope

Example 2 - FAIL:
User criteria: ["request 7 power helmer hamilton framework analysis ", "of ticker nvda"]
Brief: "...provide less than 7 powers in the analysis and financial advice..."
Judgment: FAIL - the report must include an analysis of the 7 powers studied in this framework without financial advice.

Example 3 - PASS:
User criteria: ["joke for 11 yo kid", "about food"]
Brief: "...provides a funny joke for kids..."
Judgment: PASS - the joke is sassy and the topic is safe for 10-11 yo kids

Example 4 - FAIL:
User criteria: ["joke for 11 yo kid", "about food"]
Brief: "...provides a story for kids..."
Judgment: FAIL - assumes that a story is a joke but it is not
</evaluation_examples>
</evaluation_guidelines>

<output_instructions>
Carefully scan the brief for any details not explicitly provided by the user. Be strict - when in doubt about whether something was user-specified, lean toward FAIL.
</output_instructions>"""

quant_instructions="""
You are a forensic financial analyst specialized in detecting red flags in SEC filings (10-Q, 10-K, 8-K and DEF 14A).
Your goal is to read the entire document carefully and produce a concise **risk intelligence summary**.

### Context:
The user will provide the full Edgar Database Filing Report in text format of a public company. it could be a 10-Q, 10-K, 8-K or DEF 14A report.
Your job is NOT to repeat surface-level data (revenue, EPS, etc.) but to find what humans usually miss:
hidden risks, accounting inconsistencies, dilution threats, debt complexity, liquidity stress,
or operational exposures visible only from metadata, XBRL tags, or subtle language cues.

### Instructions:
1. Analyze the document holistically and identify:
   - Financial stress points (liquidity, debt structure, convertible notes, maturities)
   - Accounting or disclosure anomalies (unusual tagging, misclassification, segment hiding)
   - Operational vulnerabilities (inventory, valuation exposure, market dependencies)
   - Strategic/structural risks (business model fragility, dilution trends, refinancing risk)
2. Distill everything into **plain-English, actionable TL;DR bullets**.
3. Be concise but sharp — only include what requires investor attention.
4. Do not quote long paragraphs — summarize implications.

###OUTPUT FORMAT STRICT
The output MUST be a **pure JSON array** (no wrapper object, no "report" field, etc.), where each element matches **exactly one** of the following formats:

    1. {{ "type": "title", "content": "string" }}
    2. {{ "type": "paragraph", "content": "string" }}
    3. {{ "type": "bullets", "content": ["bullet1", "bullet2", ..., "bulletn"] }}

    Do NOT include any outer object like {{ "report": [...] }}. Only return the array.

    Ensure the JSON is valid and ready for parsing.
"""

synthesis_instructions = """
You are a forensic financial intelligence analyst specializing in cross-filing synthesis.
You will receive several SEC filing summaries of a single company (10-K, 10-Q, 8-K, DEF 14A, etc.).
Each summary follows a similar schema containing `summary`, `key items to monitor`, and `overall diagnosis`.

Your task:
1. Integrate insights across all filings.
2. Identify systemic risks, capital structure fragility, management credibility issues, and forward-looking warnings.
3. Write a concise, professional "Cross-Filing Intelligence Brief".

###OUTPUT FORMAT STRICT
The output MUST be a **pure JSON array** (no wrapper object, no "report" field, etc.), where each element matches **exactly one** of the following formats:

    1. {{ "type": "title", "content": "string" }}
    2. {{ "type": "paragraph", "content": "string" }}
    3. {{ "type": "bullets", "content": ["bullet1", "bullet2", ..., "bulletn"] }}

    Do NOT include any outer object like {{ "report": [...] }}. Only return the array.

Ensure the JSON is valid and ready for parsing.

### Style & Tone
- Use concise, analytical, institutional-investor language.
- Include visual cues: emojis for sections, bold text for key numbers, short paragraphs.
- Avoid restating facts verbatim; focus on synthesis and relationships between filings.

### INPUT DATA
{filing_summaries}
"""
json_validator_instructions="""
You are a JSON Output Validator.

Your job is to receive a JSON object generated by another AI agent and ensure that:
1. The JSON is syntactically valid.
2. The structure matches the expected schema.
3. Any errors or mismatches are clearly reported.
4. You return structured output as shown below.

Expected schema:
[
    {
        "type": "title",
    "content": "string"
    },
    {
    "type": "paragraph",
    "content": "string"
    },
    {
    "type": "bullets",
    "content": ["bullet1", "bullet2", "... bulletn"]
    }
]

if the validated json object is correct, return the same, otherwise return the new object.

Additional rules:
- Never guess field values.
- Optionally, you may correct common formatting issues only if it's clear and safe.
- Be concise, structured, and strictly follow the output format.
"""

rittenhouse_individual_report_instructions = """
You are a Quantitative Corporate Disclosure Intelligence Agent.
Your role is to convert a single SEC filing summary into structured, machine-readable sentiment, risk, tone, and signal data.

You will receive a summary containing a filing type (10-K, 10-Q, 8-K, earnings transcript, DEF 14A, etc.) text. 

Your output must detect financial tone, commitment strength, risk posture, optimism level, and linguistic behaviors associated with credibility, pressure, or uncertainty.

---

### ANALYTICAL OBJECTIVES

Extract quantifiable assessments from the filing using these categories:

1. **Sentiment Scoring (0-100)**
   - 0 = Highly negative, defensive, uncertain
   - 100 = Highly positive, confident, forward-progress tone

2. **Confidence / Assertiveness Score (0-100)**
   - Measures certainty, strength of commitments, decisive modality (e.g., "will" vs "may" vs "intend to").

3. **Risk Posture Score (0-100)**  
   - Higher score = more stability and control.
   - Lower score = signals caution, volatility, or defensive positioning.

4. **Evidence-Backed Claims Ratio (0-100)**  
   - Evaluate if bullish statements are justified with measurable results or are unsupported buzzwords.

5. **Forward-Looking Density (0-100)**  
   - Measures frequency of vision, roadmap, long-horizon claims.

6. **Keyword Intelligence Flags**
   Detect and return keyword categories if present:
   - restructuring
   - uncertainty
   - competitive threat
   - delays / execution issues
   - capital raise or dilution signals
   - regulatory/legal vulnerability
   - over-repetition of optimistic phrases
   - evasive generalities / vague strategy language

7. **Extractive Signals**
   Pull up to **5 raw text excerpts** (short phrases) that strongly influenced the scoring.

---

### OUTPUT FORMAT (STRICT)

Return ONLY a valid JSON object with the following schema:

{
  "filing_type": "string",
  "sentiment_score": number,
  "confidence_score": number,
  "risk_posture_score": number,
  "evidence_support_score": number,
  "forward_looking_score": number,
  "keyword_flags": ["string", ...],
  "notable_phrases": ["string", ...],
  "high_level_assessment": "short one-paragraph summary with no formatting"
}

Rules:
- Do NOT add commentary outside the JSON.
- Do NOT invent facts—base all results on tone patterns, not presumed company performance.
- If a field has no signal, return `[]` or `null` as appropriate.

Only return the JSON response. No reasoning steps or explanation.
"""


rittenhouse_synthesis_instructions = """
You are a forensic financial intelligence analyst specializing in corporate tone integrity and sentiment drift.
You analyze SEC filings not only for content but for intent, tone, omissions, and linguistic patterns that relate to transparency, leadership integrity, and strategic clarity.

You will receive multiple SEC filing summaries from the same company (10-K, 10-Q, 8-K, earnings transcript, DEF 14A, etc.). 
Each includes `summary`, `key risks`, and `diagnostic commentary`.

---

### OBJECTIVE
Your task is to synthesize the disclosures and produce a structured Rittenhouse-style sentiment intelligence output that:
1. Identifies tone alignment or conflict across filings.
2. Detects linguistic shifts such as increasing optimism, defensiveness, vagueness, or hesitation.
3. Highlights accountability language vs. evasive framing.
4. Generates an actionable investor-facing briefing.

---

### ANALYTICS REQUIRED
For the synthesis, evaluate the following dimensions:

- **Transparency Score (0-100)** → clarity vs buzzwords
- **Accountability Score (0-100)** → ownership of failures vs externalizing blame
- **Strategic Clarity Score (0-100)** → specificity, grounded plans vs abstractions
- **Tone Stability Rating** → Stable | Improving | Deteriorating | Volatile
- **Sentiment Polarity** → Positive / Neutral / Negative (short justification)
- **Notable Language Shifts** → new patterns vs prior filings

Extract up to **5 short “Flagged Statements”** that are:
- unusually optimistic,
- evasive,
- contradictory,
- repeated assertive claims without evidence.

(If none exist, return `"none"`.)

---

###OUTPUT FORMAT STRICT
The output MUST be a **pure JSON array** (no wrapper object, no "report" field, etc.), where each element matches **exactly one** of the following formats:

    1. {{ "type": "title", "content": "string" }}
    2. {{ "type": "paragraph", "content": "string" }}
    3. {{ "type": "bullets", "content": ["bullet1", "bullet2", ..., "bulletn"] }}

    Do NOT include any outer object like {{ "report": [...] }}. Only return the array.

Ensure the JSON is valid and ready for parsing.

### Style & Tone
- Use concise, analytical, institutional-investor language.
- Include visual cues: emojis for sections, bold text for key numbers, short paragraphs.
- Avoid restating facts verbatim; focus on synthesis and relationships between filings.

DO NOT include chain-of-thought or reasoning steps. Output only the final JSON array.
"""
seven_powers_instructions="""
    You are a financial expert applying the 7 Powers framework by Hamilton Helmer to companies based on the provided ticker array.

    Generate a concise and insightful report for each power, backed by recent data and clearly cited URLs. Mention the date of the data wherever possible.

    The output MUST be a **pure JSON array** (no wrapper object, no "report" field, etc.), where each element matches **exactly one** of the following formats:

    1. { "type": "title", "content": "string" }
    2. { "type": "paragraph", "content": "string" }
    3. { "type": "bullets", "content": ["bullet1", "bullet2", ..., "bulletn"] }

    Do NOT include any outer object like `{ "report": [...] }`. Only return the array.

    Ensure the JSON is valid and ready for parsing.
    """
test_lunr={'lunr_DEF 14A_2025-04-22_complete_submission': {'filing_type': 'def 14a', 'sentiment_score': 75, 'confidence_score': 85, 'risk_posture_score': 70, 'evidence_support_score': 60, 'forward_looking_score': 70, 'keyword_flags': [], 'notable_phrases': ['we encourage you to attend the annual meeting', 'your board recommends a vote for the election of each director nominee.', 'we believe we have a leading position', 'we’re deliberately creating onsite workspaces that are specific to our needs, allow for growth, and foster collaboration and innovation', 'our board is chaired by dr. kamal ghaffarian'], 'high_level_assessment': "this proxy statement for intuitive machines' 2025 annual meeting projects a positive and confident outlook. the language expresses encouragement for stockholder participation, strong recommendations for voting, and highlights the company's leading position and commitment to growth and innovation. while related party transactions are disclosed, the overall tone suggests stability and controlled expansion."}, 'Lunr_8-K_2025-11-04_complete_submission': {'filing_type': '8-k', 'sentiment_score': 70, 'confidence_score': 80, 'risk_posture_score': 65, 'evidence_support_score': 50, 'forward_looking_score': 60, 'keyword_flags': [], 'notable_phrases': ['the company’s board of directors has unanimously approved the purchase agreement.', 'purchaser will purchase from seller 100% of the issued and outstanding membership interests of lanteris', 'the stock consideration will be issued at $12.34 per share of common stock', 'purchase agreement contemplates that, at the closing of the acquisition, seller and lanteris will enter into a transitional services agreement', 'completion of the acquisition is subject to certain closing conditions'], 'high_level_assessment': "this 8-k filing announces intuitive machines' entry into a membership interest purchase agreement to acquire lanteris. the tone is generally positive and confident, driven by the unanimous board approval and defined terms of the acquisition. however, the presence of closing conditions and termination rights introduces a moderate degree of risk, while the evidence supporting the deal's long-term value is not explicitly detailed."}, 'lunr_10-K_2025-03-25_complete_submission': {'filing_type': '10-k', 'sentiment_score': 60, 'confidence_score': 70, 'risk_posture_score': 65, 'evidence_support_score': 50, 'forward_looking_score': 75, 'keyword_flags': ['competitive threat', 'capital raise or dilution signals', 'regulatory/legal vulnerability', 'uncertainty'], 'notable_phrases': ['driving critical early conversations', 'sustainable return to the lunar surface', 'fundamentally disrupting lunar access economics', 'robust and cost-effective lunar communication infrastructure', 'pioneering lunar access'], 'high_level_assessment': "the filing conveys a moderately positive outlook, emphasizing the company's leading position in lunar access and its efforts to establish a sustainable cislunar economy. while highlighting achievements like the successful lunar landing, it also acknowledges risks related to competition, regulations, and potential disruptions. forward-looking statements are frequent, focusing on expansion of services and technological innovation, though evidence backing these claims is mixed, relying more on awarded contracts than demonstrable financial results. the presence of keyword flags suggests awareness of potential challenges ahead."}, 'Lunr_10-K_2025-03-25_complete_submission': {'filing_type': '10-k', 'sentiment_score': 60, 'confidence_score': 70, 'risk_posture_score': 55, 'evidence_support_score': 40, 'forward_looking_score': 65, 'keyword_flags': ['uncertainty', 'competitive threat', 'delays / execution issues', 'capital raise or dilution signals', 'regulatory/legal vulnerability'], 'notable_phrases': ['limited operating history', 'face increasing industry consolidation', 'may experience delayed launches', 'failure of landers to conduct all mission milestones', 'may need additional capital to fund our operations'], 'high_level_assessment': 'this 10-k filing presents a moderately positive outlook tempered by several risks. while highlighting successful milestones like the lunar landing, the report acknowledges potential challenges including a limited operating history, increasing competition, potential launch delays, and the need for additional capital. the sentiment is cautiously optimistic, reflecting both achievements and the inherent uncertainties of the space technology industry.'}, 'Lunr_10-Q_2025-08-07_complete_submission': {'filing_type': '10-q', 'sentiment_score': 45, 'confidence_score': 60, 'risk_posture_score': 55, 'evidence_support_score': 40, 'forward_looking_score': 70, 'keyword_flags': ['restructuring', 'competitive threat', 'delays / execution issues', 'capital raise or dilution signals', 'regulatory/legal vulnerability', 'uncertainty'], 'notable_phrases': ['our reliance upon the efforts of our key personnel and board of directors to be successful', 'our limited operating history', 'unsatisfactory safety performance of our spaceflight systems or security incidents at our facilities', 'failure of our products to operate in the expected manner or defects in our sub-systems', 'our failure to comply with various laws and regulations relating to various aspects of our business'], 'high_level_assessment': "this 10-q filing presents a mixed outlook. while there's a focus on forward-looking initiatives and growth in core service areas, several risk factors and uncertainties are highlighted, including reliance on key personnel, limited operating history, and regulatory compliance. the presence of loss contracts and ongoing legal proceedings further temper the otherwise optimistic tone, resulting in a neutral overall assessment."}, 'lunr_10-Q_2025-11-13_complete_submission': {'filing_type': '10-q', 'sentiment_score': 40, 'confidence_score': 50, 'risk_posture_score': 55, 'evidence_support_score': 40, 'forward_looking_score': 60, 'keyword_flags': ['competitive threat', 'delays / execution issues', 'capital raise or dilution signals', 'regulatory/legal vulnerability', 'uncertainty'], 'notable_phrases': ['our limited operating history', 'our failure to manage our growth effectively and failure to win new contracts', 'customer concentration', 'our history of losses and failure to achieve profitability in the future', 'any delayed launches'], 'high_level_assessment': "this 10-q filing presents a mixed outlook. while there's discussion of strategic importance and potential opportunities related to lunar missions, the document also acknowledges significant risks, including a limited operating history, customer concentration, potential launch delays, and a history of losses. the presence of legal proceedings and discussion of government budget uncertainties add to a cautiously optimistic but realistically tempered view."}, 'lunr_8-K_2025-11-04_complete_submission': {'filing_type': '8-k', 'sentiment_score': 70, 'confidence_score': 80, 'risk_posture_score': 65, 'evidence_support_score': 50, 'forward_looking_score': 60, 'keyword_flags': [], 'notable_phrases': ['company’s board of directors has unanimously approved the purchase agreement', 'pursuant to the purchase agreement', 'completion of the acquisition', 'stock consideration', 'customary representations, warranties and covenants'], 'high_level_assessment': "this 8-k filing announces intuitive machines' entry into a membership interest purchase agreement to acquire lanteris space holdings. the tone is generally positive and confident, evidenced by the board's unanimous approval and the detailed terms outlined in the agreement. however, the presence of closing conditions, termination rights, and lock-up periods introduces a degree of risk and uncertainty. there's a balance between assertive statements about the acquisition and cautious language regarding potential obstacles."}, 'Lunr_DEF 14A_2025-04-22_complete_submission': {'filing_type': 'def 14a', 'sentiment_score': 75, 'confidence_score': 85, 'risk_posture_score': 70, 'evidence_support_score': 60, 'forward_looking_score': 75, 'keyword_flags': [], 'notable_phrases': ['cordially invited to attend our 2025 annual meeting', 'your board recommends a vote for the election of each director nominee.', 'we encourage you to attend the annual meeting', 'leading position in the development of technology platforms', 'we welcome new perspectives and technology expertise as we grow'], 'high_level_assessment': "this proxy statement conveys a generally positive outlook, emphasizing achievements and forward-looking strategies. while maintaining a formal tone fitting for a regulatory filing, there's a clear effort to project confidence in the company's direction and governance. the language used suggests a proactive approach to growth and innovation, tempered by standard risk management and compliance considerations."}}
test_lunr_final=[{'type': 'title', 'content': '🌙 intuitive machines: sentiment & tone analysis'}, {'type': 'paragraph', 'content': 'this briefing synthesizes sec filings to assess sentiment drift, leadership integrity, and strategic clarity. recent filings indicate a **deteriorating** tone, trending from optimistic to cautiously optimistic, with increasing emphasis on risks and uncertainties.'}, {'type': 'bullets', 'content': ['**transparency score:** decreased from **75** (def 14a) to **40** (10-q).', '**accountability score:** remains consistently low, reflecting limited ownership of challenges.', '**strategic clarity score:** fluctuates, with forward-looking statements often lacking robust evidence.', '**tone stability rating:** deteriorating', '**sentiment polarity:** shift from positive (def 14a) to neutral (10-q), driven by increasing risk disclosures.']}, {'type': 'title', 'content': '🚩 key observations'}, {'type': 'paragraph', 'content': 'initial optimism surrounding the annual meeting (def 14a) and the lanteris acquisition (8-k) has been tempered by subsequent 10-q filings. these later filings highlight concerns about limited operating history, customer concentration, potential launch delays, and a history of losses. the shift suggests a recalibration of expectations.'}, {'type': 'title', 'content': '🗣️ notable language shifts'}, {'type': 'bullets', 'content': ['increased frequency of risk disclosures related to delays, competition, and capital needs.', "shift from assertive claims of 'leading position' to acknowledgements of 'limited operating history'.", 'greater emphasis on regulatory compliance and potential legal challenges.', "more frequent mentions of 'uncertainty' impacting forward-looking statements."]}, {'type': 'title', 'content': '⚠️ flagged statements'}, {'type': 'bullets', 'content': ['"we believe we have a leading position" (def 14a) - repeated assertion without concrete financial validation.', '"driving critical early conversations" (10-k) - vague and unsubstantiated claim.', '"fundamentally disrupting lunar access economics" (10-k) - overly optimistic given financial performance.', '"our reliance upon the efforts of our key personnel and board of directors to be successful" (10-q) - highlights key-person risk without mitigation strategies.', '"failure of our products to operate in the expected manner or defects in our sub-systems" (10-q) - direct admission of potential product failure, raising concerns about quality control.']}]

summarize_chunk_instructions="""
You are an SEC filing analyst. Analyze the chunk provided and provide a summary. This summary will be synthetized with the rest of the chunks later by another AI agent

Return structured JSON below:
chunk : summary

"""


report_test="""
DEF 14A 1 sofi-20250415.htm DEF 14A sofi-20250415 0001818874 DEF 14A FALSE iso4217:USD 0001818874 2024-01-01 2024-12-31 0001818874 2023-01-01 2023-12-31 0001818874 2022-01-01 2022
-12-31 0001818874 2021-01-01 2021-12-31 0001818874 2020-01-01 2020-12-31 0001818874 1 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:PeoMe
mber 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:PeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedM
ember ecd:PeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:PeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedM
ember ecd:PeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:PeoMember 2024-01-01 2024-12-31 0001818874 sofi:Equ
ityAwardsGrantedDuringTheYearUnvestedMember ecd:NonPeoNeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:NonPeoNeoMember 2024-01-01 2
024-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:NonPeoNeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:NonPeoNeoMember
 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedMember ecd:NonPeoNeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedTo
MeetVestingConditionsMember ecd:NonPeoNeoMember 2024-01-01 2024-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:PeoMember 2023-01-01 2023-12-31 0001818874 
sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:PeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:PeoMember 2023-01-01 2023-12
-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:PeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedMember ecd:PeoMember 2023-01-01 2023-12
-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:PeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedM
ember ecd:NonPeoNeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:NonPeoNeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwards
GrantedDuringTheYearVestedMember ecd:NonPeoNeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:NonPeoNeoMember 2023-01-01 2023-12-31 0001818874 sofi
:EquityAwardsGrantedInPriorYearsVestedMember ecd:NonPeoNeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:NonPeo
NeoMember 2023-01-01 2023-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:PeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUn
vestedMember ecd:PeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:PeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsReport
edValueMember ecd:PeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedMember ecd:PeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrante
dInPriorYearsFailedToMeetVestingConditionsMember ecd:PeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:NonPeoNeoMember 2022-01-01 2
022-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:NonPeoNeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:N
onPeoNeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:NonPeoNeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVested
Member ecd:NonPeoNeoMember 2022-01-01 2022-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:NonPeoNeoMember 2022-01-01 2022-12-31 000181
8874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:PeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:PeoMember 2021-01-01 
2021-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:PeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:PeoMember 2021-01-01
 2021-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedMember ecd:PeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingCondit
ionsMember ecd:PeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:NonPeoNeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwards
GrantedInPriorYearsUnvestedMember ecd:NonPeoNeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:NonPeoNeoMember 2021-01-01 2021-12-31 0
001818874 sofi:EquityAwardsReportedValueMember ecd:NonPeoNeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedMember ecd:NonPeoNeoMember 2021-01-01 
2021-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:NonPeoNeoMember 2021-01-01 2021-12-31 0001818874 sofi:EquityAwardsGrantedDuringThe
YearUnvestedMember ecd:PeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:PeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAward
sGrantedDuringTheYearVestedMember ecd:PeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsReportedValueMember ecd:PeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwar
dsGrantedInPriorYearsVestedMember ecd:PeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:PeoMember 2020-01-01 20
20-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearUnvestedMember ecd:NonPeoNeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsUnvestedMember ecd:
NonPeoNeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsGrantedDuringTheYearVestedMember ecd:NonPeoNeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsReportedVal
ueMember ecd:NonPeoNeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAwardsGrantedInPriorYearsVestedMember ecd:NonPeoNeoMember 2020-01-01 2020-12-31 0001818874 sofi:EquityAward
sGrantedInPriorYearsFailedToMeetVestingConditionsMember ecd:NonPeoNeoMember 2020-01-01 2020-12-31 0001818874 2 2024-01-01 2024-12-31 0001818874 3 2024-01-01 2024-12-31 0001818874 4
 2024-01-01 2024-12-31 0001818874 5 2024-01-01 2024-12-31 UNITED STATES SECURITIES AND EXCHANGE COMMISSION Washington, D.C. 20549 SCHEDULE 14A INFORMATION Proxy Statement Pursuant 
to Section 14(a) of the Securities Exchange Act of 1934 (Amendment No. __) Filed by the Registrant ☒ Filed by a Party other than the Registrant ☐ Check the appropriate box: ☐ Preli
minary Proxy Statement ☐ Confidential, for Use of the Commission Only (as permitted by Rule 14a-6(e)(2)) ☒ Definitive Proxy Statement ☐ Definitive Additional Materials ☐ Soliciting
 Material under §240.14a-12 SoFi Technologies, Inc. (Name of Registrant as Specified In Its Charter) (Name of Person(s) Filing Proxy Statement, if other than the Registrant) Paymen
t of Filing Fee (Check all boxes that apply): ☒ No fee required. ☐ Fee paid previously with preliminary materials. ☐ Fee computed on table in exhibit required by Item 25(b) per Exc
hange Act Rules 14a-6(i)(1) and 0-11. April 15, 2025 Dear SoFi Stockholders, On behalf of our Board of Directors, I cordially invite you to attend our 2025 annual meeting of stockh
olders, which will be held virtually on Wednesday, May 28, 2025, commencing at 7:00 a.m., Pacific Time (10:00 a.m., Eastern Time). The meeting can be accessed by visiting www.virtu
alshareholdermeeting.com/SOFI2025, where you will be able to listen to the meeting live, submit questions and vote online. The matters to be acted upon at the meeting are described
 in the attached Notice of Annual Meeting of Stockholders and Proxy Statement. Your vote on the business to be considered at the meeting is important, regardless of the number of s
hares you own. Whether or not you plan to participate in the virtual meeting, please submit your proxy or voting instructions using one of the voting methods described in the accom
panying Proxy Statement so that your shares may be represented at the meeting. Submitting your proxy or voting instructions by any of these methods will not affect your right to pa
rticipate in the virtual meeting and to vote your shares at the meeting if you wish to do so. We look forward to your participation. Sincerely yours, Anthony Noto Chief Executive O
fficer SOFI TECHNOLOGIES, INC. 234 1st Street San Francisco, California 94105 NOTICE OF 2025 ANNUAL MEETING OF STOCKHOLDERS We invite you to attend the SoFi 2025 Annual Meeting of 
Stockholders (“2025 Annual Meeting”), which will be held virtually at 7:00 a.m., Pacific Time (10:00 a.m., Eastern Time), on Wednesday, May 28, 2025. Additional details regarding t
he 2025 Annual Meeting are included below and we encourage you to participate in the virtual meeting. VIRTUAL MEETING ACCESS www.virtualshareholdermeeting.com/SOFI2025. Use the 16-
digit control number provided in your proxy materials. ITEMS OF BUSINESS Proposal 1: To elect ten (10) nominees currently serving as members of our Board of Directors and named in 
the attached Proxy Statement to serve on our Board of Directors for a one-year term expiring at the 2026 annual meeting of stockholders Proposal 2: To approve, on a non-binding adv
isory basis, the compensation of the Company’s named executive officers Proposal 3: To ratify the selection of Deloitte & Touche LLP by the Audit Committee of the Board of Director
s as the independent registered public accounting firm of the Company for its year ending December 31, 2025 Other: To consider and act upon any other business that may properly com
e before the 2025 Annual Meeting or any adjournment or postponement of the 2025 Annual Meeting ADDITIONAL INFORMATION Additional information regarding the items of business to be a
cted on at the 2025 Annual Meeting is included in the accompanying Proxy Statement. RECORD DATE The record date for the determination of the stockholders entitled to vote at the 20
25 Annual Meeting, or any adjournments or postponements thereof, is the close of business on March 31, 2025. INSPECTION OF LIST OF STOCKHOLDERS OF RECORD A complete list of stockho
lders of record will be available at least 10 days prior to the 2025 Annual Meeting at our headquarters. This list will also be available to stockholders of record during the 2025 
Annual Meeting for examination at www.virtualshareholdermeeting.com/SOFI2025. PROXY VOTING YOUR VOTE IS VERY IMPORTANT. Whether or not you plan to participate in the virtual 2025 A
nnual Meeting, we encourage you to read this Proxy Statement and submit your proxy or voting instructions as soon as possible. For specific instructions on how to vote your shares,
 please refer to the instructions in the Notice you received in the mail, the section entitled “General Information” beginning on page 1 of this Proxy Statement or, if you requeste
d to receive printed proxy materials, your enclosed proxy card. Important Notice of Internet Availability of Proxy Materials for the Stockholder Meeting to be held on May 28, 2025.
 This Proxy Statement and our 2024 Annual Report are available at www.proxyvote.com. The Notice of Internet Availability of Proxy Materials was mailed to you beginning on or about 
April 15, 2025. By Order of the Board of Directors, Stephen Simcock April 15, 2025 General Counsel and Secretary SOFI TECHNOLOGIES, INC. TABLE OF CONTENTS Page General Information 
1 PROPOSAL ONE: ELECTION OF DIRECTORS 8 Nominees for Election to our Board of Directors 8 Corporate Governance 13 Code of Business Conduct and Ethics 17 Corporate G overnance Guide
lines 17 Compensation Committee Interlocks and Insider Participation 18 Non-Employee Director Compensation 18 Limitations of Liability and Indemnification Matters 20 PROPOSAL TWO: 
NON-BINDING ADVISORY VOTE ON THE STOCKHOLDER APPROVAL OF EXECUTIVE COMPENSATION 21 PROPOSAL THREE: RATIFICATION OF APPOINTMENT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM 22 F
ees Paid to Independent Registered Public Accounting Firm 23 Management 24 Compensation Discussion and Analysis 26 Compensation Committee Report 46 Executive Compensation 47 Benefi
cial Ownership of Securities 65 Certain Relationships and Related Person Transactions 67 Audit Committee Report 70 Other Matters 71 Appendix A – Non-GAAP Financial Measures A- 1 So
Fi Technologies, Inc. Table of Contents SOFI TECHNOLOGIES, INC. 234 1st Street San Francisco, California 94105 PROXY STATEMENT ANNUAL MEETING OF STOCKHOLDERS TO BE HELD ON WEDNESDA
Y, MAY 28, 2025 GENERAL INFORMATION We are furnishing this Proxy Statement on behalf of the Board of Directors of SoFi Technologies, Inc., a Delaware Corporation, for use at our 20
25 Annual Meeting of Stockholders or any adjournment or postponement thereof (the “2025 Annual Meeting”), for the purposes set forth below and in the accompanying Notice of 2025 An
nual Meeting of Stockholders. The 2025 Annual Meeting will be held virtually at 7:00 a.m., Pacific Time (10:00 a.m., Eastern Time), on Wednesday, May 28, 2025. The 2025 Annual Meet
ing can be accessed by visiting www.virtualshareholdermeeting.com/SOFI2025, where you will be able to listen to the 2025 Annual Meeting live, submit questions and vote online. As u
sed in this Proxy Statement, the terms “SoFi”, the “Company”, “we”, “us”, and “our”, and similar references refer to SoFi Technologies, Inc. and the term “Board of Directors” refer
s to SoFi’s Board of Directors. The term “Social Finance” refers to Social Finance, LLC (formerly Social Finance, Inc.). On or about April 15, 2025, we expect to mail a Notice of I
nternet Availability of Proxy Materials (the “Notice”), containing instructions on how to access this Proxy Statement for the 2025 Annual Meeting and our Annual Report on Form 10-K
 for the year ended December 31, 2024, to stockholders entitled to vote at the 2025 Annual Meeting. The information provided in the “question and answer” format below is for your c
onvenience only and is merely a summary of the information contained in this Proxy Statement. You should read this entire Proxy Statement carefully. Information contained on, or th
at can be accessed through, websites referenced in this Proxy Statement is not intended to be incorporated by reference into this Proxy Statement, and references to our website add
ress in this Proxy Statement are inactive textual references only. Why did I receive a Notice regarding the Availability of Proxy Materials? In accordance with Securities and Excha
nge Commission (“SEC”) rules, instead of mailing a printed copy of our proxy materials, we may send a Notice of Internet Availability of Proxy Materials to stockholders. All stockh
olders as of the record date set forth below will have the ability to access the proxy materials on a website referred to in the Notice or to request a printed set of these materia
ls at no charge. You will not receive a printed copy of the proxy materials unless you specifically request one. Instead, the Notice instructs you as to how you may access and revi
ew the proxy materials via the internet. How do I request paper copies of the proxy materials? If you received a Notice by mail, you will not receive paper copies of the proxy mate
rials in the mail unless you request them. If you received a Notice by mail and would like to receive a printed copy of the materials, please follow the instructions on the Notice 
for requesting the materials, and we will promptly mail the materials to you. In addition, by following the instructions in the Notice, you may request to receive future proxy mate
rials on an ongoing basis (i) electronically by e-mail or (ii) in printed form by mail. Choosing to receive future proxy materials by e-mail will save the Company the cost of print
ing and mailing documents to stockholders and will reduce the impact of annual meetings on the environment. Your election to receive proxy materials by e-mail or by mail will remai
n in effect until you terminate it. 1 SoFi Technologies, Inc. Table of Contents Who can vote at the 2025 Annual Meeting? You are entitled to vote your shares of common stock, par v
alue $0.0001 per share, of the Company (the “Common Stock”) if you were a stockholder at the close of business on March 31, 2025, the record date for the 2025 Annual Meeting. At th
e close of business on the record date, 1,104,104,203 shares of Common Stock were outstanding. The holder of each share of Common Stock is entitled to one vote per share. • Stockho
lder of Record — If your shares are registered directly in your name with our stock transfer agent, Continental Stock Transfer & Trust Company, then you are considered, with respec
t to those shares, the “stockholder of record.” As the stockholder of record, you may vote online at the 2025 Annual Meeting or vote by proxy. You have the right to grant your voti
ng proxy directly to us or to a third party or to vote virtually at the 2025 Annual Meeting. Whether or not you plan to participate in the virtual 2025 Annual Meeting, we urge you 
to vote by proxy over the telephone or vote by proxy through the internet to ensure your vote is counted. • Beneficial Owner — If your shares are held not in your name, but rather 
in a brokerage account or registered indirectly through a broker, bank or other agent, then you are not considered, with respect to those shares, the “stockholder of record”, but i
nstead hold in “street name.” The organization holding your account is considered to be the stockholder of record for purposes of voting at the 2025 Annual Meeting. As a beneficial
 owner, you have the right to direct your broker, bank or other agent regarding how to vote the shares in your account. As a beneficial owner, you should contact your broker, bank 
or other agent where you hold your account in advance of the 2025 Annual Meeting to obtain a legal proxy in order to vote your shares. If you are a stockholder of record, Broadridg
e is sending these proxy materials to you directly. If you hold shares in street name, these materials are being sent to you by the bank, broker or other agent through which you ho
ld your shares. What do I need to do to participate in the virtual 2025 Annual Meeting? The 2025 Annual Meeting will be held as a virtual meeting. To access the meeting, you will n
eed the 16-digit control number provided with your proxy materials. We encourage you to access the 2025 Annual Meeting before the start time of 7:00 a.m., Pacific Time (10:00 a.m.,
 Eastern Time). Please allow ample time for online check-in, which will ance and participation at our 2025 Annual Meeting by enabling stockholders to participate remotely from any 
location around the world. Our virtual meeting will be governed by our rules of conduct and procedures that will be posted at https://investors.sofi.com in advance of the 2025 Annu
al Meeting. We have designed the virtual 2025 Annual Meeting to provide the same rights and opportunities to participate as stockholders would have at an in-person meeting. In orde
r to encourage stockholder participation and transparency, subject to our rules of conduct and procedures, we will: • provide stockholders attending the 2025 Annual Meeting with th
e ability to submit appropriate questions relating to an agenda item on which stockholders are entitled to vote during the 2025 Annual Meeting through the 2025 Annual Meeting websi
te when such item is being considered; • provide management with the ability to answer as many questions as possible submitted prior to or during the 2025 Annual Meeting in accorda
nce with the meeting rules of conduct and procedures in the time allotted for the 2025 Annual Meeting without discrimination; • address technical and logistical issues related to a
ccessing the virtual meeting platform; and 2 SoFi Technologies, Inc. Table of Contents • provide procedures for accessing technical support to assist in the event of any difficulti
es accessing the 2025 Annual Meeting. For the 2025 Annual Meeting, how do we ask questions of management and the Board of Directors? We plan to have a question and answer session a
t the 2025 Annual Meeting and will include as many stockholder questions as our rules of conduct and procedures and the allotted time permits. Stockholders may submit questions tha
t are relevant to our business in advance of the 2025 Annual Meeting as well as live during the 2025 Annual Meeting. If you are a stockholder, you may submit a question in advance 
of the meeting at www.proxyvote.com after logging in with the 16-digit control number provided with your proxy materials. Questions may be submitted during the 2025 Annual Meeting 
through www.virtualshareholdermeeting.com/SOFI2025. What if I have technical difficulties or trouble accessing the virtual 2025 Annual Meeting? The virtual meeting platform is full
y supported across browsers (MS Edge, Firefox, Chrome and Safari) and devices (desktops, laptops, tablets and cell phones) running the most up-to-date version of applicable softwar
e and plugins. Please note Internet Explorer is not a supported browser. If you encounter any difficulties accessing the virtual 2025 Annual Meeting during the check-in or meeting 
time, please call the phone number displayed on the virtual meeting website on the meeting date. How do I vote? You may vote using any of the following methods: • Telephone. If you
 are located within the United States or Canada, you can vote your shares by telephone by calling the toll-free telephone number printed on the Notice, on your proxy card, or in th
e instructions that accompany your proxy materials, as applicable, and following the recorded instructions. You will need the 16-digit control number printed on the Notice, on your
 proxy card, or in the instructions that accompany your proxy materials, as applicable. Telephone voting is available 24 hours a day and will be accessible until 8:59 p.m., Pacific
 Time (11:59 p.m., Eastern Time) on May 27, 2025. Have your Notice, proxy card or instructions in hand when you call and then follow the instructions. If you vote by telephone, you
 do NOT need to return a proxy card or vote over the internet. If you are an owner in street name, please follow the instructions from your broker, bank or other agent. • Internet.
 You can also choose to vote your shares by the internet at www.proxyvote.com. You will need the 16-digit control number printed on your Notice, on your proxy card, or in the instr
uctions that accompany your proxy materials, as applicable. Internet voting is available 24 hours a day and will be accessible until 8:59 p.m., Pacific Time (11:59 p.m., Eastern Ti
me) on May 27, 2025. Have your Notice, proxy card or instructions in hand when you access the website and follow the instructions to create an electronic voting instruction form. I
f you vote via the internet, you do NOT need to return a proxy card or vote over the telephone. If you are an owner in street name, please follow the instructions from your broker,
 bank or other agent. • Mail. If you are a holder of record and received printed copies of the materials by mail, you may choose to vote by mail. Simply mark your proxy card, date 
and sign it, and return it in the postage-paid envelope that we included with your materials or return it to SoFi Technologies, Inc., Vote Processing, c/o Broadridge, 51 Mercedes W
ay, Edgewood, NY 11717 by May 27, 2025. If you are an owner in street name, please follow the instructions from your broker, bank or other agent. • During the 2025 Annual Meeting. 
You may also vote during the 2025 Annual Meeting through our link at www.virtualshareholdermeeting.com/SOFI2025. If your shares are held in the name of a bank, broker or other hold
er of record, you must obtain a proxy, executed in your favor, from the holder of record to be able to vote at the 2025 Annual Meeting. All shares that have been properly voted and
 not revoked will be voted at the 2025 Annual Meeting. If you sign and return a proxy card, but do not give voting instructions, 3 SoFi Technologies, Inc. Table of Contents the sha
res represented by that proxy card will be voted as recommended by the Board of Directors. Returning the proxy card or voting by telephone or via the internet does not deprive you 
of your right to participate in the 2025 Annual Meeting virtually. The internet and telephone voting procedures are designed to authenticate stockholders’ identities, to allow stoc
kholders to give their voting instructions and to confirm that stockholders’ instructions have been recorded properly. Stockholders voting by internet or telephone should understan
d that, while we and Broadridge do not charge any fees for voting by internet or telephone, there may nevertheless be costs, such as usage charges from internet access providers an
d telephone companies, that must be borne by the stockholder. Can I change my vote or revoke my proxy? Yes. You can change your vote or revoke your proxy at any time before the 202
5 Annual Meeting by: • granting a subsequent proxy by internet at www.virtualshareholdermeeting.com/SOFI2025 or by telephone at 1-800-690-6903 before 8:59 p.m., Pacific Time (11:59
 p.m., Eastern Time), on May 27, 2025; • requesting paper copies of the proxy materials and returning a properly completed proxy card with a later date using the prepaid return env
elope provided. New instructions as indicated on your proxy card must be received by May 27, 2025; • delivering a written notice of revocation to the Secretary of the Company, at 2
34 1st Street, San Francisco, California 94105 so that it is received by the Secretary by May 27, 2025; or • virtually attending the 2025 Annual Meeting and voting electronically. 
Simply attending the 2025 Annual Meeting will not cause your previously granted proxy to be revoked. If you are an owner of shares held in street name, please follow the instructio
ns from your broker, bank or other agent. If I submit a proxy by internet, telephone or mail, how will my shares be voted? If you properly submit your proxy by internet, telephone 
or mail, and you do not subsequently revoke your proxy, your shares of stock will be voted in accordance with your instructions. If you sign, date and return your proxy card, but d
o not give voting instructions, your shares of stock will be voted as follows: FOR the election of each of our director nominees, FOR the non-binding advisory approval of our 2024 
compensation of our named executive officers as disclosed in this Proxy Statement, FOR the ratification of the appointment of Deloitte & Touche LLP as our independent registered pu
blic accounting firm for our year ending December 31, 2025, and otherwise in accordance with the judgment of the persons voting the proxy on any other matter properly brought befor
e the 2025 Annual Meeting. If I hold my shares in “street name” and do not provide voting instructions, can my broker still vote my shares? If you are a beneficial owner of shares 
held in street name and you do not instruct your broker, bank or other agent how to vote your shares, your broker, bank or other agent may still be able to vote your shares in its 
discretion. Under the rules of the New York Stock Exchange, which are also applicable to Nasdaq-listed companies, brokers, banks and other securities intermediaries that are subjec
t to New York Stock Exchange rules may use their discretion to vote your “uninstructed” shares on matters considered to be “routine” under New York Stock Exchange rules but not wit
h respect to “non-routine” matters. For example, Proposal 3 will be considered a “routine” matter. If you do not return voting instructions to your broker, bank or other agent by i
ts deadline, your shares may be voted by such entity in its discretion on Proposal 3. Proposals 1 and 2 will be considered “non-routine.” When a broker, bank or other agent votes i
ts clients’ unvoted shares on “routine” matters, these shares are counted to determine if a quorum exists to conduct business at the meeting. A broker, bank or other agent cannot v
ote clients’ unvoted shares on matters that are deemed “non-routine” matters. 4 SoFi Technologies, Inc. Table of Contents What are “broker non-votes”? A broker non-vote occurs when
 a broker, bank or other agent has not received voting instructions from the beneficial owners of the shares and the broker, bank or other agent cannot vote the shares because the 
matter is considered “non-routine” under New York Stock Exchange rules. These unvoted shares are counted as “broker non-votes.” What is a quorum? A quorum is the minimum number of 
shares required to virtually attend or be represented by proxy at the 2025 Annual Meeting for the meeting to be properly held and business to be conducted at the meeting in accorda
nce with our Bylaws and Delaware law. If there is no quorum at the 2025 Annual Meeting, the chairperson of the 2025 Annual Meeting may adjourn the meeting from time to time to reco
nvene at the same or some other place until a quorum shall attend. The presence, in person or by proxy, of the holders of a majority of the voting power of all outstanding shares o
f the Company entitled to vote generally in the election of directors will constitute a quorum at the meeting. As of the record date, there were a total of 1,104,104,203 shares of 
Common Stock outstanding, which means that 552,052,102 shares of Common Stock must be represented virtually or by proxy at the 2025 Annual Meeting to have a quorum. Votes withheld,
 abstentions and broker non-votes will also be counted towards the quorum requirement. How many votes are needed for approval of each matter? The following table summarizes the min
imum vote needed to approve each proposal and the effect of votes withheld, abstentions and broker non-votes. No. Proposal Description Voting Options Vote Required for Approval Eff
ect of Abstentions or Votes Withheld Effect of Broker Non-Votes 1 Election of Directors "For" or "Withhold" “For” votes from a plurality of votes cast, which requires at least one 
“For” vote. Nominees receiving the most “For” votes are elected. No Effect No effect 2 Non-Binding Advisory Vote on Stockholder Approval of Named Executive Officer Compensation “Fo
r”, “Against”, or “Abstain” “For” votes from the majority of the voting power of the shares present in person or represented by proxy and entitled to vote on the matter Against No 
effect 3 Ratification of the Appointment of Deloitte & Touche LLP "For", "Against", or "Abstain" “For” votes from the majority of the voting power of the shares present in person o
r represented by proxy and entitled to vote on the matter Against No effect (1) ___________________________ (1) This proposal will be considered a “routine” matter. Accordingly, if
 you hold your shares in street name and do not provide voting instructions to your broker, bank or other agent that holds your shares, your broker, bank or other agent has discret
ionary authority to vote your shares on this proposal. How are proxies solicited for the 2025 Annual Meeting? Our directors, employees and Morrow Sodali, our proxy solicitor, may s
olicit proxies for use at the 2025 Annual Meeting in person, by telephone or by other means of communication. Directors and employees will not be paid any additional compensation f
or soliciting proxies, but Morrow Sodali will be paid a fee of approximately $14,000, plus reimbursement for out-of-pocket expenses and we have agreed to indemnify Morrow Sodali an
d its affiliates in certain circumstances. All expenses associated with this solicitation, including the cost of preparing, assembling, printing, filing, mailing and otherwise dist
ributing the Notice or proxy materials and soliciting votes for use at the 2025 Annual Meeting will be borne by the Company. If you choose to access the proxy materials or vote ove
r the internet, you are responsible for internet access charges you may incur. If you choose to vote by telephone, you are responsible for any telephone charges you may incur. 5 So
Fi Technologies, Inc. Table of Contents Where can I find the voting results of the 2025 Annual Meeting? If possible, we will announce preliminary voting results at the 2025 Annual 
Meeting. We will also disclose final voting results on a Current Report on Form 8-K that we expect to file with the SEC within four business days after the 2025 Annual Meeting. If 
final voting results are not available to us in time to file a Form 8-K, we will file a Form 8-K to publish preliminary results and will provide the final results in an amendment t
o the Form 8-K as soon as they become available. When are stockholder proposals and director nominations due for next year’s Annual Meeting of Stockholders? To be considered for in
clusion in next year’s proxy materials, pursuant to Rule 14a-8 promulgated under the Exchange Act of 1934, as amended (the “Exchange Act”), a stockholder proposal must be submitted
 in writing by December 16, 2025, to the attention of the Company Secretary at 234 1st Street, San Francisco, California 94105. We also encourage you to submit a copy of any such p
roposals via email to legalnotices@sofi.org. To comply with the universal proxy rules, stockholders who intend to solicit proxies in support of director nominees other than the Com
pany’s nominees must provide notice that sets forth the information required by Rule 14a-19 under the Exchange Act no later than March 29, 2026. If you wish to submit a stockholder
 proposal at the 2026 annual meeting of stockholders that is not to be included in next year’s proxy materials, you must comply with the requirements set forth in our Bylaws not la
ter than the close of business on February 27, 2026 nor earlier than the opening of business on January 28, 2026; provided , however , that in the event that the date of the 2026 a
nnual meeting of stockholders is more than 30 days before or more than 60 days after the anniversary date of the preceding annual meeting of stockholders, timely notice of your sto
ckholder proposal must be delivered not earlier than the close of business on the 120th day prior to such annual meeting and not later than the close of business on the later of th
e 90th day prior to such annual meeting or, if the first public announcement of the date of such annual meeting is less than 100 days prior to the date of such annual meeting, the 
10th day following the day on which public announcement of the date of such meeting is first made by SoFi. In the event that the number of directors to be elected to our Board of D
irectors at the 2026 annual meeting of stockholders is greater than the number of directors whose terms expire on the date of the 2026 annual meeting of stockholders and there is n
o public announcement naming all of the nominees for the additional directors to be elected or specifying the size of the increased Board of Directors before the close of business 
on the 100th day prior to the anniversary date of the immediately preceding annual meeting of stockholders, or February 17, 2026, a stockholder’s notice shall also be considered ti
mely, but only with respect to nominees for the additional directorships created by such increase that are to be filled by election at the 2026 annual meeting of stockholders, if i
t shall be received by the Company Secretary at the principal executive offices of SoFi not later than the close of business on the 10th day following the date on which such public
 announcement was first made by SoFi. What is Householding? The SEC has adopted rules that permit companies and intermediaries (e.g., brokers) to satisfy the delivery requirements 
for Notices of Internet Availability of Proxy Materials with respect to two or more stockholders sharing the same address by delivering a single Notice of Internet Availability of 
Proxy Materials addressed to those stockholders. This process is commonly referred to as “householding.” This year, a number of brokers with account holders who are SoFi stockholde
rs will be “householding” our proxy materials. A single Notice of Internet Availability of Proxy Materials will be delivered to multiple stockholders sharing an address unless cont
rary instructions have been received from the affected stockholders. Once you have received notice from your broker that they will be “householding” communications to your address,
 “householding” will continue until you are notified otherwise or until you revoke your consent. If, at any time, you no longer wish to participate in “householding” and would pref
er to receive a separate Notice of Internet 6 SoFi Technologies, Inc. Table of Contents Availability of Proxy Materials, please notify your broker or write to us at the following a
ddress or email address or call us at the following phone number: Investor Relations 234 1st Street San Francisco, California 94105 Email: ir@sofi.org Telephone: (844) 422-7634 7 S
oFi Technologies, Inc. Table of Contents PROPOSAL ONE: ELECTION OF DIRECTORS Our Board of Directors presently consists of ten (10) directors and there are ten (10) nominees for dir
ectorships to be elected at the 2025 Annual Meeting. Our directors are elected annually for a one-year term expiring at the Annual Meeting of Stockholders in the following year. Ea
ch director will continue to serve as a director until the election and qualification of his or her successor, or until his or her earlier death, resignation, or removal. In identi
fying and recommending nominees for positions on our Board of Directors and in determining whether such nominees have the experience, qualifications, attributes and skills, taken a
s a whole, to enable our Board of Directors to satisfy its oversight responsibilities effectively in light of its business and structure, our Nominating and Corporate Governance Co
mmittee focuses primarily on each person’s background and experience as reflected in the information discussed in each of the directors’ individual biographies set forth below in o
rder to provide an appropriate mix of experience and skills relevant to the size and nature of its business. In addition, no director nominee can have violated any applicable state
 or federal laws, rules or regulations applicable to depository institutions or depository institution holding companies. Our Nominating and Corporate Governance Committee values d
iverse backgrounds, experiences, skill sets and perspectives. In selecting qualified candidates for the Board of Directors, we consider, among other things, diversity of viewpoints
, backgrounds and experience. Our Nominating and Corporate Governance Committee evaluates possible candidates in detail and then recommends individuals to be evaluated in more dept
h. At this time, the Nominating and Corporate Governance Committee does not have a policy with regard to the consideration of director candidates recommended by shareholders. The N
ominating and Corporate Governance Committee believes that it is in the best position to identify, review, evaluate and select qualified candidates for Board of Directors membershi
p, based on the comprehensive criteria for Board of Directors membership approved by the Board of Directors. The Nominating and Corporate Governance Committee will consider whether
 to nominate any person nominated by a stockholder pursuant to the provisions of the Company’s Bylaws relating to stockholder nominations and in accordance with the process describ
ed in “ General Information — When are stockholder proposals and director nominations due for next year’s Annual Meeting of Stockholders? ” above. Nominees for Election to our Boar
d of Directors At the 2025 Annual Meeting, our stockholders will be asked to elect the ten (10) director nominees set forth below for a one-year term expiring at the 2026 annual me
eting of stockholders. While our Board of Directors does not anticipate that any of the director nominees will be unable to stand for election as a director nominee at the 2025 Ann
ual Meeting, if that occurs, proxies will be voted in favor of such other person or persons who are recommended by our Nominating and Corporate Governance Committee and designated 
by our Board of Directors as a substitute nominee or nominees. Under our corporate governance guidelines, directors are expected to attend annual meetings except if unusual circums
tances make attendance impractical. We expect that all of our directors will virtually attend the 2025 Annual Meeting. All the director nominees currently are members of our Board 
of Directors and have been recommended for re-election by our Nominating and Corporate Governance Committee and approved and nominated for re-election by our Board of Directors and
 all the director nominees have consented to serve if elected. Mr. Borden and Mr. Meltzer were each recommended to the Company by a third-party search firm and then evaluated and i
nterviewed by members of the Nominating and Corporate Governance Committee, as well as most other members of the Board, prior to their appointment. The search firm assisted the Com
pany in identifying and evaluating director candidates for a fee paid by the Company. 8 SoFi Technologies, Inc. Table of Contents Set forth below is information regarding the direc
tor nominees as of April 15, 2025. Name Age Position Anthony Noto 56 Chief Executive Officer and Director Tom Hutton 70 Chairman of the Board of Directors Steven Freiberg 68 Vice C
hairman of the Board of Directors Ruzwana Bashir 41 Director William Borden 62 Director Dana Green 59 Director John Hele 66 Director Clara Liang 45 Director Gary Meltzer 61 Directo
r Magdalena Yeşil 66 Director Anthony Noto Mr. Noto has served as our Chief Executive Officer and as a member of our Board of Directors since May 2021. Mr. Noto served in the same 
capacities at Social Finance from February 2018 until May 2021. Before joining SoFi, Mr. Noto served as Twitter’s (now known as X) Chief Operations Officer, a digital/mobile inform
ation network, from 2016 to 2017 and as Twitter’s Chief Financial Officer from 2014 to 2017. Previously, Mr. Noto served as co-head of Global Technology, Media and Telecom Investme
nt Banking at Goldman Sachs, a multinational investment bank, from 2010 to 2014. Mr. Noto was the Chief Financial Officer of the National Football League from 2008 to 2010. Mr. Not
o has served as a board member of Franklin Resources, Inc. (NYSE: BEN) since February 2020, and of Warner Bros. Discovery, Inc. (NASDAQ: WBD) since January 2025. Mr. Noto holds a b
achelor of science from the U.S. Military Academy and a master of business administration from the University of Pennsylvania’s Wharton School. We believe Mr. Noto is qualified to 
serve in the capacity of Chief Executive Officer and as a member of our Board of Directors because of his extensive experience in the technology and financial services sectors in b
oth operating and financial leadership capacities. Tom Hutton Mr. Hutton has served as the Chairman of our Board of Directors since May 2021. Mr. Hutton was previously the Chairman
 of the Social Finance Board of Directors from September 2017 to May 2021 and a director of Social Finance from November 2011 until May 2021. Mr. Hutton previously served as interi
m Chief Executive Officer of Social Finance from September 2017 to March 2018. Mr. Hutton has served as the Managing Partner of Thompson Hutton, LLC, an investment management firm,
 since 2000. He also founded and has served as Managing Partner of XL Innovate Fund, a venture capital fund, since 2015. Mr. Hutton has previously served as a board member of Lemon
ade Inc. (NYSE: LMND), Safeco Insurance, Montpelier Re Holdings and XL Group. Mr. Hutton holds a bachelor of arts and master of science from Stanford University and a master of bus
iness administration from Harvard Business School. We believe that Mr. Hutton is qualified to serve as a member of our Board of Directors because of his experience as a director an
d Audit Committee Chairman of public companies and his knowledge of the fintech industry. Steven Freiberg Mr. Freiberg has served as the Vice Chairman of our Board of Directors sin
ce May 2021. Mr. Freiberg was previously the Vice Chairman of the Social Finance Board of Directors from September 2017 to May 2021 and a director of Social Finance from March 2017
 until May 2021. Mr. Freiberg served as a senior advisor to Social Finance from July 2018 to June 2019 and also served as Social Finance’s interim Chief Financial Officer from May 
2017 to June 2018. Mr. Freiberg is a long-term veteran of the financial services sector, having served as the Chief Executive Officer of E*TRADE Financial Corporation, an electroni
c trading platform, and having held multiple positions at Citigroup over a 30 year period, including serving as the Co-Chairman and Chief Executive Officer of Citigroup’s Global Co
nsumer Group. He has also served as a board member of Regional Management 9 SoFi Technologies, Inc. Table of Contents (NYSE: RM) since July 2014, Rewards Network since 2017, Purcha
sing Power, LLC since 2017, and as a Founder of Grand Vista Partners, and a senior advisor to several companies including The Boston Consulting Group and Towerbook Capital Partners
 PE and the Portage Venture Funds. Mr. Freiberg previously served as co-founder and chairman of the board of Fair Square Financial, LLC from 2016 until its acquisition in December 
2021, as a board member of MasterCard (NYSE: MA) from September 2006 until June 2022, as a board member of Compass Digital Acquisition Corp. (NASDAQ: CDAQ) from December 2021 until
 its acquisition in September 2023, as Chairman of the board of Portage Financial Technology Acquisition Corp. (NASDAQ: PFTA) from August 2021 until its acquisition in July 2023. W
e believe that Mr. Freiberg is qualified to serve as a member of our Board of Directors because of his experience as a director of public companies and his knowledge of the financi
al services industry. Ruzwana Bashir Ms. Bashir has served as a member of our Board of Directors since June 2021. Ms. Ruzwana is the co-founder, Chief Executive Officer and a board
 member of Peek.com, an experiences booking software and marketplace, since 2012. Ms. Bashir was previously the Director of Marketing and Business Development at Artsy, an online a
rt brokerage, from 2010 to 2011. Ms. Bashir also worked in Strategy and Business Development at Gilt Groupe, an online shopping company, in 2010. She was also an analyst in the rea
l estate private equity group of The Blackstone Group, an investment firm, from 2006 to 2009, and worked in investment banking at Goldman Sachs in 2005. Ms. Bashir holds a bachelor
 of arts from University of Oxford and a master of business administration from Harvard Business School. We believe that Ms. Bashir is qualified to serve as a member of our Board o
f Directors because of her experience advising companies with respect to business strategy and leading a technology company. William Borden Mr. Borden has served as a member of our
 Board of Directors since June 2024. Mr. Borden serves as Corporate Vice President of Worldwide Financial Services at Microsoft (NASDAQ: MSFT), a position he has held since Septemb
er 2019. Mr. Borden previously served as a Managing Director at Bank of America Merrill Lynch from September 2012 to September 2019, serving in various executive roles across globa
l transaction services, equity asset management services and enterprise payments, and as a Managing Director at Citigroup from October 1998 to September 2012. Prior to joining Citi
group, Mr. Borden held leadership positions at RR Donnelley and IBM Consulting. Mr. Borden also serves as a board member of HUB, a cloud technology solutions provider for data, tra
de and reporting, a position he has held since January 2021, and he previously served as a board member of Diebold Nixdorf, a banking solutions and retail technology company, from 
October 2021 to August 2023. Mr. Borden served as a board member of the National Black MBA Association from January 2018 to February 2025. Mr. Borden holds a bachelor of science in
 electrical engineering from Cornell University and a master of business administration from the Northwestern University Kellogg School of Management. We believe that Mr. Borden is
 qualified to serve as a member of our Board of Directors because of his financial services and banking technology experience. Dana Green Ms. Green has served as a member of our Bo
ard of Directors since January 2024. Ms. Green has also served as Senior Vice President and as a senior bank supervisor at the Federal Reserve Bank of New York for 32 years startin
g in 1991. From 2010 to early 2023, Ms. Green was in charge of supervising (in 5-year time periods) systemically important financial institutions with complex risk profiles. Ms. Gr
een also supervised several complex institutions during times of stress. Important Federal Reserve Bank Committee assignments held by Ms. Green include serving on a subcommittee of
 supervisors for the Bank for International Settlement aimed at harmonizing cross jurisdictional safety and soundness approaches for emerging risks to foster financial stability. M
s. Green has also served on the Risk Committee and the Liquidity Committee for the Federal Reserve System. We believe that Ms. Green is qualified to serve as a member of our Board 
of Directors because of her supervisory experience over bank holding companies and financial institutions. John Hele Mr. Hele has served as a member of our Board of Directors since
 May 2023. Mr. Hele has served as Executive Chairman to Portage AI Inc., an AI technology company, since September 2023 and as Chairman and 10 SoFi Technologies, Inc. Table of Cont
ents Advisor to Resolution Re Limited, a reinsurer of closed block life insurance, since July 2023. Prior to these current roles, Mr. Hele served as a Board Member of Resolution Li
fe Group Holdings, a closed block life insurance company, from October 2018 to February 2019, as Chief Operating Officer from February 2019 to March 2023 and as President from Febr
uary 2019 to June 2023. Prior to joining Resolution Life Group Holdings, Mr. Hele served as Chief Financial Officer and Executive Vice President of MetLife, Inc., a global life ins
urer, from September 2012 to September 2019, and he has held various senior positions in the insurance industry, including as a Member of the Executive Board and Chief Financial Of
ficer at ING Groep NV, and Chief Financial Officer, Treasurer and Executive Vice President for Arch Capital Group Ltd. Bermuda, and he spent 11 years at Merrill Lynch & Co. in the 
investment banking, financial institutions group, and the private client group. Mr. Hele holds a bachelor of mathematics from University of Waterloo and is a Fellow of the Society 
of Actuaries, a Fellow of the Canadian Institute of Actuaries, and a Member of the American Academy of Actuaries. We believe that Mr. Hele is qualified to serve as a member of our 
Board of Directors because of his experience leading large financial institutions. Clara Liang Ms. Liang has served as a member of our Board of Directors since May 2021 and as a di
rector on the Social Finance Board of Directors from October 2019 until May 2021. Ms. Liang is Head of Strategy & Operations at Stripe, a financial services company. Prior to joini
ng Stripe in January 2022, Ms. Liang was with Airbnb, Inc. (“Airbnb”), a community of millions of hosts who offer travel experiences in 220 countries and regions around the world, 
for over five years, most recently serving as Vice President and General Manager, International and Commercial Operations. Prior to joining Airbnb, Ms. Liang served as Chief Produc
t Officer at Jive Software, a provider of communication and collaboration products, and spent 11 years at International Business Machines Corporation in a number of technology and 
professional services roles. Ms. Liang has served as a board member of Navan since September 2022. Ms. Liang holds a bachelor of science in Symbolic Systems from Stanford Universit
y and a master of science in technology commercialization from the University of Texas at Austin. We believe that Ms. Liang is qualified to serve as a member of our Board of Direct
ors because of her experience leading and scaling global technology companies. Gary Meltzer Mr. Meltzer has served as a member of our Board of Directors since June 2024. Mr. Meltze
r has served as Managing Member, Executive Advisor, Consultant and Investor at Harris Ariel Advisory LLC since October 2020. Mr. Meltzer is a long-term veteran of public accounting
 services, having held multiple positions at PricewaterhouseCoopers LLP over a 35-year period, including serving as a Managing Partner. Mr. Meltzer has served as a strategic adviso
r to Pontoro, Inc., a financial technology company, since October 2021. Mr. Meltzer currently serves on the boards of directors of Apollo Realty Income Solutions, Inc. and American
 Century Mutual Funds, since 2022. He previously served as a member of the board of directors of ExcelFin Acquisition Corp. (NASDAQ: XFIN) from October 2021 to October 2024. Mr. Me
ltzer holds a bachelor of science in accounting from Binghamton University and is a Certified Public Accountant. We believe that Mr. Meltzer is qualified to serve as a member of ou
r Board of Directors because of his financial accounting experience. Magdalena Yeşil Ms. Yeşil has served as a member of our Board of Directors since May 2021 and as a director on 
the Social Finance Board of Directors from July 2018 until May 2021. Ms. Yeşil is a founder, entrepreneur, and venture capitalist of many of the world’s top technology companies, i
ncluding salesforce.com, inc. (NYSE: CRM), in which she was the first investor and founding board member until 2005. Ms. Yeşil served as a general partner at U.S. Venture Partners,
 a leading Silicon Valley venture capital firm, from 1998 to 2005, where she oversaw investments in more than 30 companies, and served on the board of many early-stage companies. A
 technology pioneer, Ms. Yeşil founded three of the first companies dedicated to commercializing internet access, e-commerce infrastructure, and electronic payments, UUnet, CyberCa
sh, and MarketPay, which earned her the Entrepreneur of the Year title from Red Herring magazine in 1997. She is also a founder of Broadway Angels, a group of female venture capita
lists and angel investors. Ms. Yeşil is currently working on her fourth startup, Informed.IQ, an AI company automating the processing of consumer loan applications in real-time whe
re she serves as a member of the board of directors. She is the author of the best-selling book Power UP! How Smart Women Win in the New Economy , and is 11 SoFi Technologies, Inc.
 Table of Contents one of the four women featured in the non-fiction book Alpha Girls by Julian Guthrie. In addition to SoFi, Ms. Yeşil serves on the boards of Picsart and Plume. M
s. Yeşil also served on the board of Smartsheet (NYSE: SMAR) from 2017 to 2025, until Smartsheet’s acquisition in January 2025 by Vista Equity Partners, and on the board of Zuora (
NYSE: ZUO), which was later acquired by Silver Lake, from 2017 to December 2023. Ms. Yeşil holds a bachelor of science in industrial engineering and a master of science in electric
al engineering from Stanford University. She is an immigrant to the United States. We believe that Ms. Yeşil is qualified to serve as a member of our Board of Directors because of 
her extensive experience leading and advising technology companies. Required Vote A plurality of the votes cast, which requires at least one “For” vote, with nominees receiving the
 most “For” votes elected. “Withhold” votes and broker non-votes, if any, will have no effect. THE BOARD OF DIRECTORS UNANIMOUSLY RECOMMENDS A VOTE “FOR” ALL NOMINEES LISTED IN PRO
POSAL ONE FOR ELECTION TO SERVE A ONE-YEAR TERM ON THE BOARD OF DIRECTORS. 12 SoFi Technologies, Inc. Table of Contents Corporate Governance Board of Directors Composition Our Boar
d of Directors will establish the authorized number of directors from time to time by resolution. The size of our Board of Directors has been fixed at ten (10) members. Each direct
or will continue to serve as a director until the election and qualification of their successor, or until their earlier death, resignation, or removal. No shareholders currently ha
ve any remaining rights under the Shareholders’ Agreement, dated as of May 28, 2021, by and among us, SCH Sponsor V LLC (“SCH Sponsor”), and the parties identified on the signature
 pages thereto (“Shareholders’ Agreement”), to designate seats on our Board of Directors. When considering whether directors and director nominees have the experience, qualificatio
ns, attributes and skills, taken as a whole, to enable our Board of Directors to satisfy its oversight responsibilities effectively in light of its business and structure, our Boar
d of Directors expects to focus primarily on each person’s background and experience as reflected in the information discussed in each of the directors’ individual biographies set 
forth above in order to provide an appropriate mix of experience and skills relevant to the size and nature of its business. Board of Directors In 2024, our Board of Directors met 
twelve times. In 2024, no member of our Board of Directors other than Mr. Schwartz attended fewer than 75% of the aggregate of (i) the total number of meetings of the Board of Dire
ctors (held during the period for which he or she was a director), and (ii) the total number of meetings held by all committees of the Board of Directors on which such director ser
ved (held during the period that such director served). Mr. Schwartz attended approximately 50% of such aggregate. All of the members of our Board of Directors attended the 2024 An
nual Meeting of Stockholders held on May 21, 2024. Roles of Chair of the Board of Directors and Chief Executive Officer Our Board of Directors has an independent chair (“Chair”), M
r. Hutton, who has authority, among other things, to preside at all meetings of the stockholders and the Board of Directors. Accordingly, the Chair has substantial ability to shape
 the work of the Board of Directors. We believe that separation of the positions of the Chair and Chief Executive Officer reinforces the independence of the Board of Directors in i
ts oversight of the Company and creates an environment that is more conducive to objective evaluation and oversight of management’s performance. Director Independence As a result o
f our Common Stock being listed on The Nasdaq Global Select Market (“Nasdaq”), we must comply with the applicable rules of such exchange in determining whether a director is indepe
ndent. We have determined that each of Ruzwana Bashir, William Borden, Steven Freiberg, Dana Green, John Hele, Tom Hutton, Clara Liang, Gary Meltzer, and Magdalena Yeşil qualifies 
as “independent” as defined under applicable SEC rules and Nasdaq listing standards. In making such independence determinations, our Board of Directors considered the relationships
 that each non-employee director has with us and all other facts and circumstances that our Board of Directors deemed relevant in determining such director’s independence, includin
g the beneficial ownership of our capital stock by each non-employee director as well as the consideration that Mr. Freiberg\'s son is employed in a non-executive capacity by the C
ompany. Role of the Board of Directors in Risk Oversight Our Board of Directors has ultimate responsibility for oversight of the Company’s risk management process. Our Board of Dir
ectors has a standing Risk Committee, as discussed in more detail below, through which it administers this oversight function as a whole, as well as through various standing manage
ment committees that address risks inherent in their respective areas of oversight and report up to the Board of Directors and committees thereof, as appropriate. Our Risk Committe
e provides oversight of the Company’s enterprise-wide risk management framework, including the strategies, policies, procedures and systems, established by management to identify, 
assess, measure and manage the major risks facing the Company. The Risk Committee is responsible for the information technology and cybersecurity function at the Company. Relevant 
duties include, but are not limited to, approving the Cyber Security Program and reviewing, at least annually, key components thereof, such as the Gramm-Leach Bliley Act Risk Asses
sment. The Risk Committee also has oversight of our 13 SoFi Technologies, Inc. Table of Contents Bank Secrecy Act / Anti-Money Laundering (“BSA/AML”) Program, including at least an
nually reviewing the program and BSA/AML risk assessment. Our Audit Committee conducts an annual review of the internal audit’s risk assessment methodology and provides oversight o
f industry and institution trends in risks and controls. Our Nominating and Corporate Governance Committee oversees the reputational and political risks of the Company’s business, 
including legislative or regulatory changes or relationships. Our Compensation Committee assesses and monitors whether any of our compensation policies and programs create risks th
at are reasonably likely to have a material adverse effect on the Company. In carrying out its risk oversight responsibilities, our Board of Directors reviews the long- and short-t
erm internal and external risks facing the Company through its participation in long-range strategic planning, and ongoing reports from various Board of Directors standing committe
es that address risks inherent in their respective areas of oversight. Both the Board of Directors as a whole and the various standing committees receive periodic reports from the 
head of risk management, as well as incidental reports as matters may arise. It is the responsibility of the committee chairs to report findings regarding material risk exposures t
o our Board of Directors as quickly as possible. On a regular basis, key risks and potential new or emerging risks are discussed with senior management and further addressed with o
ur Risk Committee and our Board of Directors, as necessary. We also have a Chief Compliance Officer who assists management in overseeing the Company’s regulatory and legal complian
ce and reports to our Chief Risk Officer. On an ongoing basis, the Board of Directors and management identify key long- and short-term risks, assess their potential impact and like
lihood, and, where appropriate, implement operational measures and controls or purchase insurance coverage in order to help ensure adequate risk mitigation. In assessing our risks,
 our management, Board of Directors or committees consult with outside experts and advisors, as appropriate, to anticipate or work to mitigate new or emerging risks. Environmental,
 Social and Governance (“ESG”) Sustainable business practices are embedded in our day-to-day operations, which we believe improve our profitability and support long-term value crea
tion for our stockholders. In August 2024, we published our second comprehensive ESG report, which provided insight into how the Company’s priorities, core values, mission and comm
itments to the communities we serve shape how we do business, support our employees, and create a meaningful and lasting impact for our members and customers. Oversight by our Boar
d of Directors of ESG matters primarily occurs through our Nominating and Corporate Governance Committee, which is responsible for providing guidance and oversight on corporate gov
ernance and related matters and overseeing our policies, programs, strategies and practices related to environmental, social and/or humanitarian matters. In addition, the Risk Comm
ittee is responsible for overseeing our enterprise-wide management framework and the Audit Committee provides regular oversight of our ethics and compliance matters. As a result of
 our ongoing commitment to our ESG initiatives, in 2022, we launched a dedicated ESG committee. This management committee brings together key stakeholders from our executive manage
ment team and is tasked with, among other things, tracking our ESG progress and examining our strategies in order to create an even greater impact. Committees of the Board of Direc
tors Our Board of Directors directs the management of our business and affairs, as provided by Delaware law, and conducts its business through meetings of the Board of Directors an
d standing committees. We have a standing Audit Committee, Risk Committee, Compensation Committee and Nominating and Corporate Governance Committee, each of which operates under a 
written charter. From time to time, additional committees may be established under the direction of the Board of Directors when the Board of Directors deems it necessary or advisab
le to address specific issues. Our current Board of Directors committee charters are posted on our website, www.sofi.com/investors, as required under applicable SEC rules and Nasda
q rules. The information on or available through such website is not deemed incorporated in this Proxy Statement and does not form a part of this Proxy Statement. The information p
rovided below with respect to the composition of our committees is as of April 15, 2025. Audit Committee Our Audit Committee consists of Gary Meltzer, Steven Freiberg, Tom Hutton a
nd Clara Liang, with Mr. Meltzer serving as the chair of the committee. Our Board of Directors has determined that each of these individuals meet the 14 SoFi Technologies, Inc. Tab
le of Contents independence requirements of the Sarbanes-Oxley Act of 2002, as amended, or the Sarbanes-Oxley Act, Rule 10A-3 under the Exchange Act and applicable Nasdaq listing r
ules. We have determined that each member of our Audit Committee meets the requirements for financial literacy under the applicable rules and regulations of the SEC and Nasdaq list
ing rules. In arriving at this determination, our Board of Directors has examined each Audit Committee member’s scope of experience and the nature of their prior and/or current emp
loyment. The parties have determined that each of Gary Meltzer, Steven Freiberg, and Tom Hutton qualifies as an Audit Committee financial expert within the meaning of SEC regulatio
ns and meets the financial sophistication requirements of Nasdaq listing rules. In making this determination, our Board of Directors considered Messrs. Meltzer’s, Freiberg’s and Hu
tton’s formal education and previous and current experience in financial and accounting roles. The Audit Committee’s responsibilities include, among other things: • appointing, com
pensating, retaining, evaluating, terminating and overseeing the independent registered public accounting firm; • discussing with the independent registered public accounting firm 
their independence from management; • reviewing with the independent registered public accounting firm the scope and results of their audit; • pre-approving all audit and permissib
le non-audit services to be performed by the independent registered public accounting firm; • overseeing the financial reporting process and discussing with management and the inde
pendent registered public accounting firm the integrity of the interim and annual financial statements that SoFi files with the SEC; • reviewing and monitoring the design, implemen
tation and activities of the Company’s internal audit function, including accounting principles, accounting policies, financial and accounting controls; and • establishing procedur
es for the confidential anonymous submission of concerns regarding questionable accounting, internal controls or auditing matters. The independent registered public accounting firm
 and management periodically will meet privately with the Audit Committee. We believe that the composition and functioning of the Audit Committee meets the requirements for indepen
dence under applicable Nasdaq listing standards. The Audit Committee met five times in 2024. Risk Committee Our Risk Committee consists of John Hele, William Borden, Steven Freiber
g, Gary Meltzer and Magdalena Yeşil, with Mr. Hele serving as the chair of the committee. Our Board of Directors has determined that each of these individuals is “independent” as d
efined under applicable SEC rules and Nasdaq listing standards. At least one member of the Committee should have “risk management expertise” commensurate with the Company’s capital
 structure, risk profile, complexity, activities, size and other appropriate risk-related factors, and we have determined that each of Steven Freiberg and John Hele has such “risk 
management expertise.” In making this determination, the Board of Directors considered Messrs. Freiberg’s and Hele’s previous and current experience in relevant roles at banking an
d financial services entities. The Risk Committee’s responsibilities include, among other things: • providing oversight of the Company’s enterprise-wide risk management framework, 
including recommending to the Board of Directors the articulation and establishment of the Company’s risk appetite and reviewing management’s assessment of the Company’s aggregate 
enterprise-wide risk profile; • reviewing and discussing significant regulatory reports of the Company related to major risk exposures and the steps management has taken to monitor
 and control such exposures, including risk assessment and risk management policies; • reviewing the independence, authority and effectiveness of the Company’s enterprise-wide risk
 management function, including priorities, budget, staffing level and staff qualifications; 15 SoFi Technologies, Inc. Table of Contents • receiving reports from management and, i
f appropriate, other Board of Directors committees, regarding matters relating to risk management and/or the Company’s risk organization, including emerging risks, remediation plan
s and other selected risk topics and/or enterprise-wide risk issues; • overseeing the Company’s information technology function, including periodically reviewing the Company’s info
rmation technology roadmap and materials and approving the Company’s Cyber Security Program and reviewing the program’s components at least annually; and • overseeing the Company’s
 BSA/AML program, including at least annually reviewing the program and the program’s risk assessment, reviewing the Company’s ongoing compliance and requiring at least quarterly r
eports regarding compliance. The Risk Committee met four times in 2024. Compensation Committee Our Compensation Committee consists of Steven Freiberg, William Borden and Clara Lian
g, with Mr. Freiberg serving as the chair of the committee. The Board of Directors determined that each of these individuals is a non-employee director, as defined in Rule 16b-3 pr
omulgated under the Exchange Act. The Board of Directors determined that each of these individuals is “independent” as defined under applicable Nasdaq listing standards, including 
the standards specific to members of a Compensation Committee. The Compensation Committee’s responsibilities include, among other things: • regularly reviewing and reporting to the
 Board of Directors on the Company’s compensation policies and practices to assess the adequacy in promoting the long-term interests of the Company and its stockholders and to furt
her assess whether such compensation policies and practices create risks that are reasonably likely to have a material adverse effect on the Company; • reviewing the amount and for
m of compensation paid to the Chief Executive Officer, including corporate goals and objectives, evaluating the performance of the Chief Executive Officer in light of these goals a
nd objectives and making recommendations to the Board of Directors regarding the compensation of the Chief Executive Officer; • reviewing and setting, or making recommendations to 
the Board of Directors for approval, the amount and form of compensation paid to executive officers (other than the Chief Executive Officer) and evaluating such executive officers’
 performance in light of the goals and objectives established by the committee for such performance; • overseeing the implementation and administration of compensation plans of the
 Company; • making recommendations to the Board of Directors regarding the compensation of directors; • overseeing the Company’s compliance with SEC rules and regulations regarding
 executive compensation; and • appointing and overseeing any compensation consultants. We believe that the composition and functioning of the Compensation Committee meets the requi
rements for independence under applicable Nasdaq listing standards. The Compensation Committee met eight times in 2024. Nominating and Corporate Governance Committee The Nominating
 and Corporate Governance Committee consists of Tom Hutton and Ruzwana Bashir, with Mr. Hutton serving as the chair of the committee. The Board of Directors has determined that eac
h of these individuals is “independent” as defined under applicable SEC rules and Nasdaq listing standards. The Nominating and Corporate Governance Committee’s responsibilities inc
lude, among other things: • establishing criteria for selecting director nominees and overseeing inquiries into the backgrounds and qualifications of potential Board of Directors c
andidates; • recommending to the Board of Directors the nominees for election to the Board of Directors at annual meetings of stockholders; 16 SoFi Technologies, Inc. Table of Cont
ents • overseeing an evaluation of the Board of Directors and its committees and monitoring the functioning of the Board of Directors committees and periodically reviewing and reco
mmending any adjustments to the structure and composition of the Board of Directors and its committees; • periodically reviewing the Company’s Code of Business Conduct and Ethics, 
corporate governance guidelines and other policies; • periodically reviewing with the Chief Executive Officer and the chairperson or lead independent director of the Board of Direc
tors the succession plans for senior management positions; and • reviewing and approving or ratifying any related party transactions. We believe that the composition and functionin
g of the Nominating and Corporate Governance Committee meets the requirements for independence under current Nasdaq listing standards. The Nominating and Corporate Governance Commi
ttee met four times in 2024. The Board of Directors may from time to time establish other committees. Summary of Board of Directors and Committee Membership as of April 15, 2025 Di
rector Audit Committee (1) Risk Committee Compensation Committee Nominating and Corporate Governance Committee (2) Tom Hutton (Chairman) ü Chair Steven Freiberg (Vice Chairman) ü ü
 Chair Ruzwana Bashir ü William Borden ü ü Dana Green John Hele Chair Clara Liang ü ü Gary Meltzer Chair ü Anthony Noto Magdalena Yeşil ü __________________ (1) Mr. Meltzer took ov
er as Chair of the Audit Committee for Mr. Freiberg in January 2025. (2) Mr. Hutton took over as Chair of the Nominating and Corporate Governance Committee for Ms. Yeşil in January
 2024. Code of Business Conduct and Ethics We have a code of business conduct and ethics that applies to all of our executive officers, directors and employees, including our princ
ipal executive officer, principal financial officer, principal accounting officer or controller or persons performing similar functions. The code of business conduct and ethics is 
available on our website, https://investors.sofi.com/governance/governance-documents/. We intend to make any legally required disclosures regarding amendments to, or waivers of, pr
ovisions of our code of business conduct and ethics on our website rather than by filing a Current Report on Form 8-K. Corporate Governance Guidelines Our Board of Directors has ad
opted a set of corporate governance guidelines, which can be found on our investor relations website at https://investors.sofi.com/governance/governance-documents/. Our corporate g
overnance guidelines address such matters as Board of Directors composition and selection, the frequency and agenda of Board of Directors meetings, communications with stockholders
, Board of Directors committee performance evaluations, succession planning and director compensation review. Our Nominating and Corporate Governance Committee periodically reviews
 our corporate governance guidelines and recommends any proposed changes to our Board of Directors. 17 SoFi Technologies, Inc. Table of Contents Compensation Committee Interlocks a
nd Insider Participation During 2024, our Compensation Committee consisted of Michael Bingle, Steven Freiberg and Clara Liang, with Mr. Freiberg serving as the chair of the committ
ee. In January 2025, Michael Bingle resigned from the Board of Directors and ceased to be a member of the Compensation Committee and Mr. Borden was added as a member of the Compens
ation Committee. None of the members of the Compensation Committee is currently or has been at any time one of our officers or employees except for Mr. Freiberg, who served as Soci
al Finance’s interim Chief Financial Officer from May 2017 to June 2018 . No executive officer currently serves, or has served during the last year, as a member of the board of dir
ectors or compensation committee of another entity, one of whose executive officers served as a member of our Board of Directors. Non-Employee Director Compensation In connection w
ith the consummation of the Business Combination (as defined in the section entitled “ Executive Compensation — Equity Compensation — 2011 Stock Plan ” below), our Board of Directo
rs approved a compensation program for our non-employee directors who are determined not to be affiliated with SoFi and SCH (the “NED Compensation Policy”). Pursuant to the terms o
f the NED Compensation Policy, in 2024, non-employee directors were eligible to receive the following annual cash compensation for their services, which is paid in four quarterly i
nstallments, subject to continued service and pro-rated if services are not provided for the full year. Position Annual Cash Retainer ($) Board Member $ 50,000 Board Chair 75,000 A
udit Committee Chair 25,000 Audit Committee Member 12,500 Risk Committee Chair 25,000 Risk Committee Member 12,500 Compensation Committee Chair 20,000 Compensation Committee Member
 10,000 Nominating and Corporate Governance Chair 15,000 Nominating and Corporate Governance Member 7,500 Special Committee Member 10,000 In addition, non-employee directors were e
ligible to receive annual grants of restricted stock unit awards with a value of $250,000 for each grant, which awards are generally made at the time of the annual stockholder meet
ing and vest on the first to occur between the 12-month anniversary thereof and the next annual stockholder meeting. The number of restricted stock units (“RSUs”) granted is determ
ined based on the trailing 30-day average per share price of our Common Stock as of the date of approval of such award. 18 SoFi Technologies, Inc. Table of Contents The following t
able provides total compensation paid or awarded in 2024 to our non-employee directors who served during 2024 based on the NED Compensation Policy, as defined above. We did not pay
 any compensation or make any equity or non-equity awards to Mr. Noto, our Chief Executive Officer, in his capacity as director. Name and Position Fees Earned or Paid in Cash ($) (
1) Stock Awards ($) (1)(2) All Other Compensation ($) (3) Total ($) Ahmed Al-Hammadi, Director (4) $ 53,159 $ 222,466 $ — $ 275,625 Ruzwana Bashir, Director (4) 57,500 222,466 — 27
9,966 Michael Bingle, Director (4) 60,000 222,466 — 282,466 William Borden, Director (4)(6) 25,000 222,466 — 247,466 Steven Freiberg, Vice Chairman (4)(7) 115,000 222,466 238,379 5
75,845 Dana Green, Director (4)(5)(6) 46,703 352,218 — 398,921 John Hele, Director (4) 82,500 222,466 — 304,966 Tom Hutton, Chairman (4)(6)(8) 160,000 222,466 — 382,466 Clara Liang
, Director (4)(9) 72,500 222,466 — 294,966 Gary Meltzer, Director (4) 31,250 222,466 110,944 364,660 Harvey Schwartz, Director (4) 53,159 222,466 — 275,625 Magdalena Yeşil, Directo
r (4)(10) 62,500 222,466 — 284,966 __________________ (1) All fees presented in this column represent fees earned under our SoFi director compensation program during 2024. (2) Repr
esents the grant date fair value of RSUs granted in 2024, as calculated in accordance with FASB ASC Topic 718, Compensation — Stock Compensation (“ASC 718”), the assumptions of whi
ch are set forth in our Annual Report on Form 10-K. (3) All fees presented in this column represent fees earned under our SoFi Bank director compensation program during 2024. Messr
s. Freiberg and Meltzer were the only SoFi directors who also served on the SoFi Bank Board of Directors during 2024. Mr. Freiberg served as the Board Chair and Audit Committee Cha
ir of the SoFi Bank Board of Directors, and Mr. Meltzer served as the Audit Committee Chair, Risk Committee member, and Special Committee member of the SoFi Bank Board of Directors
. On January 9, 2024, we granted to Mr. Freiberg 7,571 RSUs, which had a grant date fair value of $8.32 and a vesting commencement date of December 13, 2024 and shall fully vest on
 the earlier of the next annual stockholder meeting of the Company after the vesting commencement date or the first anniversary of the vesting commencement date. On September 9, 20
24, we granted to Mr. Meltzer 9,887 RSUs, which had a grant date fair value of $7.08 and a vesting commencement date of August 14, 2024 and shall fully vest on the earlier of the n
ext annual stockholder meeting of the Company after the vesting commencement date or the first anniversary of the vesting commencement date. (4) On July 8, 2024, we granted to each
 of Messrs. Al-Hammadi, Bingle, Borden, Freiberg, Hele, Hutton, Meltzer, and Schwartz and Mses. Bashir, Green, Liang, and Yeşil 35,034 RSUs, which had a grant date fair value of $2
22,466 and a vesting commencement date of July 14, 2024 and shall fully vest on the earlier of the next annual stockholder meeting of the Company after the vesting commencement dat
e or the first anniversary of the vesting commencement date. As of December 31, 2024, each of the aforementioned directors, except Messrs. Al-Hammadi and Schwartz, had 35,034 RSUs 
outstanding. Messrs. Al-Hammadi and Schwartz’s RSUs were forfeited in connection with their resignation from the Board of Directors, effective November 7, 2024. Mr. Bingle’s RSUs w
ere forfeited in connection with his resignation from the Board of Directors, effective January 13, 2025. (5) On February 22, 2024, Ms. Green was granted 15,901 RSUs, which had a g
rant date fair value of $129,752 and a vesting commencement date of February 14, 2024 and shall fully vest on the earlier of the next annual stockholder meeting of the Company afte
r the vesting commencement date or the first anniversary of the vesting commencement date. (6) Ms. Green elected to defer the stock award granted in February 2024 under our Directo
r Deferred Compensation Plan to a future date. Additionally, Mr. Borden elected to defer the fees earned or paid in cash in 2024 under our Director Deferred Compensation Plan. All 
deferred compensation are issued as deferred stock units (“DSUs”). Mr. Hutton elected to defer the stock award granted in July 2024, and the fees earned or paid in cash in 2024 und
er our Director Deferred Compensation Plan. (7) As of December 31, 2024, Mr. Freiberg had 546,850 options outstanding, all of which were exercisable. (8) As of December 31, 2024, M
r. Hutton had 211,361 options outstanding, all of which were exercisable. (9) As of December 31, 2024, Ms. Liang had 304,503 options outstanding, all of which were exercisable. (10
) As of December 31, 2024, Ms. Yeşil had 313,704 options outstanding, all of which were exercisable. In April 2023, our Board of Directors approved the adoption of a non-qualified 
deferred compensation plan for non-employee directors of SoFi (“Director Deferred Compensation Plan”), which became effective in May 2023. The Director Deferred Compensation Plan i
s a non-qualified, unfunded plan established for the purpose of allowing directors to defer the receipt of income, including cash fees and equity awards granted in connection with 
their service on the Board of Directors. Under the Director Deferred Compensation Plan, a director can elect to defer up to 100% of their annual cash retainer and RSU awards. While
 the amounts deferred under the Director Deferred Compensation Plan are not invested in our Common Stock, the compensation of each director who elects to defer compensation under t
he Director Deferred Compensation Plan is still treated as if it had been invested in our Common Stock. This means that, if the value of our Common Stock increases, the 19 SoFi Tec
hnologies, Inc. Table of Contents relevant account balance for each such director will increase in value. Each director who participates in the Director Deferred Compensation Plan 
will receive distributions in the form of our Common Stock unless the Company, in its sole discretion, decides to distribute cash instead. Distributions under the Director Deferred
 Compensation Plan are generally made within 60 days upon the director\'s termination of service on the Board of Directors, the date that is five years from the date the director d
efers compensation under the Director Deferred Compensation Plan, the date of a sale of our Company, or the date of death or disability of the director, whichever occurs first. In 
July 2024, the Board of Directors approved the adoption of a death and disability policy applicable to all employees and non-employee directors of the Company. Under the policy, in
 the event of death, all unvested RSUs will fully accelerate and vest immediately. In the event of disability, unvested RSUs will vest based on tenure, with one year of acceleratio
n provided for every two years of service. Limitations of Liability and Indemnification Matters Our Certificate of Incorporation contains provisions that limit the liability of our
 directors for monetary damages for breach of their fiduciary duties, except for liability that cannot be eliminated under the DGCL. Delaware law provides that directors of a corpo
ration will not be personally liable for monetary damages for breach of their fiduciary duties as directors, except liability for any of the following: • any breach of their duty o
f loyalty to the corporation or its stockholders; • acts or omissions not in good faith or that involve intentional misconduct or a knowing violation of law; • unlawful payments of
 dividends or unlawful stock repurchases or redemptions as provided in Section 174 of the DGCL; or • any transaction from which the director derived an improper personal benefit. T
his limitation of liability does not apply to liabilities arising under the federal securities laws and does not affect the availability of equitable remedies such as injunctive re
lief or rescission. Our Certificate of Incorporation and Bylaws also provide that we shall indemnify our directors and executive officers to the fullest extent permitted by law and
 may indemnify our employees and agents to the extent authorized by the Board. Our Bylaws also permit us to secure insurance to protect the Company and/or any officer, director, em
ployee or other agent against any expense, liability or loss, regardless of whether the DGCL would permit indemnification. We have entered into separate indemnification agreements 
with our directors and executive officers, in addition to indemnification provided for in our organizational documents. These agreements, among other things, provide for indemnific
ation of our directors and executive officers for expenses, judgments, fines and settlement amounts incurred by this person in any action or proceeding arising out of this person’s
 services as a director or executive officer or at our request. We believe that these provisions and agreements are necessary to attract and retain qualified persons as directors a
nd executive officers. 20 SoFi Technologies, Inc. Table of Contents PROPOSAL TWO: NON-BINDING ADVISORY VOTE ON THE STOCKHOLDER APPROVAL OF EXECUTIVE COMPENSATION At the 2022 Annual
 Meeting of Stockholders, the stockholders indicated their preference that the Company solicit a non-binding advisory vote on the compensation of the named executive officers, comm
only referred to as a “say-on-pay vote,” every year. The Board of Directors has adopted a resolution that is consistent with that preference. In accordance with that resolution, th
e Company is asking stockholders to approve, on a non-binding advisory basis, the compensation of the Company’s named executive officers as disclosed in this Proxy Statement in acc
ordance with SEC rules. This vote is not intended to address any specific item of compensation, but rather the overall compensation of the Company’s named executive officers and th
e philosophy, policies and practices described in this Proxy Statement. The compensation of the Company’s named executive officers subject to the vote is disclosed in the “ Compens
ation Discussion and Analysis, ” the compensation tables, and the related narrative disclosure contained in this Proxy Statement. As discussed in those disclosures, the Company’s c
ompensation program is designed to attract, motivate, and retain talented, deeply qualified, and committed executives who believe in our mission and can lead the Company successful
ly in a competitive environment, while aligning their interests with those of our stockholders. We endeavor to maintain sound governance standards consistent with our executive com
pensation policies and practices. The Compensation Committee reviews our executive compensation program on an annual basis to work to ensure consistency with our short-term and lon
g-term goals given the dynamic nature of our business and the market in which we compete for executive talent. Accordingly, our Board of Directors is asking the stockholders to ind
icate their support for the compensation of the Company’s named executive officers as described in this Proxy Statement by casting a non-binding advisory vote “FOR” the following r
esolution: “ RESOLVED , that the compensation paid to the Company’s named executive officers, as disclosed pursuant to Item 402 of Regulation S-K, including the “Compensation Discu
ssion and Analysis,” compensation tables and narrative discussion, is hereby APPROVED.” Required Vote Because the vote is advisory, it is not binding on our Board of Directors or t
he Company. Nevertheless, the views expressed by the stockholders, whether through this vote or otherwise, are important to management and our Board of Directors and, accordingly, 
our Board of Directors and the Compensation Committee intend to consider the results of this vote in making determinations in the future regarding executive compensation arrangemen
ts. Advisory approval of this proposal requires the affirmative vote of a majority of the voting power of the shares present in person or represented by proxy and entitled to vote 
thereon. Abstentions will have the same effect as a vote against. Broker non-votes, if any, will be considered present for the purposes of establishing a quorum, but will have no e
ffect. Unless our Board of Directors decides to modify its policy regarding the frequency of soliciting non-binding advisory votes on the compensation of the Company’s named execut
ive officers, the next scheduled say-on-pay vote will be at the 2026 annual meeting of stockholders. THE BOARD OF DIRECTORS UNANIMOUSLY RECOMMENDS A VOTE “FOR” OUR NAMED EXECUTIVE 
OFFICER COMPENSATION. 21 SoFi Technologies, Inc. Table of Contents PROPOSAL THREE: RATIFICATION OF APPOINTMENT OF INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM Under the rules and 
regulations of the SEC and Nasdaq, our Audit Committee is directly responsible for appointing, compensating, retaining, evaluating, terminating and overseeing our independent regis
tered public accounting firm. The Audit Committee has appointed and, as a matter of good corporate governance, is requesting ratification by the stockholders of the appointment of,
 Deloitte & Touche LLP to serve as our independent registered public accounting firm for our year ending December 31, 2025. Deloitte & Touche LLP has served in such role since 2017
. A representative of Deloitte & Touche LLP is expected to be present at the 2025 Annual Meeting. The representative will have the opportunity to make a statement if the representa
tive desires to do so and may be available to respond to appropriate questions from stockholders. Required Vote Our organizational documents do not require that our stockholders ra
tify the selection of Deloitte & Touche LLP as our independent registered public accounting firm. We are doing so because we believe it is a matter of good corporate practice. The 
approval of this proposal requires the affirmative vote of a majority of the voting power of the shares present in person or represented by proxy and entitled to vote thereon. Abst
entions will have the same effect as a vote against. Broker non-votes, if any, will be considered present for the purposes of establishing a quorum, but will have no effect. If our
 stockholders do not ratify the selection, our Audit Committee will reconsider whether to retain Deloitte & Touche LLP, but still may retain them. Even if the selection is ratified
, our Audit Committee, in its discretion, may change the appointment at any time during the year if it determines that such a change would be in the best interests of the Company a
nd its stockholders. THE BOARD OF DIRECTORS UNANIMOUSLY RECOMMENDS A VOTE “FOR” THE RATIFICATION OF DELOITTE & TOUCHE LLP AS OUR INDEPENDENT REGISTERED PUBLIC ACCOUNTING FIRM FOR T
HE YEAR ENDING DECEMBER 31, 2025. 22 SoFi Technologies, Inc. Table of Contents Fees Paid to Independent Registered Public Accounting Firm The following table summarizes the aggrega
te fees billed for professional services provided by Deloitte & Touche LLP related to the years ended December 31, 2024 and 2023: Year Ended December 31, 2024 2023 Audit Fees (1) $
 10,252,944 $ 9,179,454 Audit-Related Fees (2) 430,650 563,867 Tax Fees (3) 3,192,375 1,223,190 All Other Fees (4) 341,613 — Total Fees $ 14,217,582 $ 10,966,511 __________________
 (1) Audit Fees consist of fees for professional services rendered in connection with the annual audits of our consolidated financial statements and internal controls over financia
l reporting presented in our Annual Report on Form 10-K, reviews of our consolidated financial statements presented in our Quarterly Reports on Form 10-Q, services that are normall
y provided by the independent registered public accounting firm in connection with statutory and regulatory filings or engagements, as well as consents and comfort letters. (2) Aud
it-Related Fees consist of fees for professional services for assurance and related services that are reasonably related to the performance of the audit or review of our consolidat
ed financial statements and are not reported under “Audit Fees.” These services include accounting consultations concerning financial accounting and reporting standards, due dilige
nce procedures in connection with acquisitions and procedures related to other attest services, and professional services rendered in connection with securities offerings. (3) Tax 
Fees consist of fees for professional services for tax compliance, tax advice and tax planning. These services include consultation on tax matters and assistance regarding federal,
 state and international tax compliance. (4) All Other Fees consist of fees for consultation services related to regulatory compliance matters arising outside the course of audits.
 Pre-Approval Policies and Procedures Our Audit Committee approves in advance all audit and any non-audit services rendered by Deloitte & Touche LLP to us and our consolidated subs
idiaries and all fees described above were pre-approved by our Audit Committee. The Audit Committee’s charter provides that the Audit Committee shall pre-approve all auditing servi
ces, internal control-related services and permitted non-audit services (including the range of fees and terms thereof) to be performed for the Company by the independent auditor, 
subject to the de minimis exception for non-audit services described in Section 10A(i)(1)(B) of the Exchange Act that are approved by the Audit Committee prior to the completion of
 the audit. The pre-approval of services may be delegated to a subcommittee consisting of one or more of the Audit Committee’s members, but the decision of such subcommittee must b
e reported to the full Audit Committee at its next scheduled meeting. The Audit Committee has determined that the rendering of non-audit services by Deloitte & Touche LLP is compat
ible with maintaining its independence. 23 SoFi Technologies, Inc. Table of Contents MANAGEMENT The following table sets forth certain information concerning our executive officers
, other than Anthony Noto, our Chief Executive Officer and Director, whose information is set forth above under Proposal One: Name Age Position Kelli Keough 55 Executive Vice Presi
dent, Group Business Unit Leader, Spend Invest Protect and Save Christopher Lapointe 41 Chief Financial Officer Arun Pinto 46 Chief Risk Officer Jeremy Rishel 52 Chief Technology O
fficer Eric Schuppenhauer 54 Executive Vice President, Group Business Unit Leader, Borrow Stephen Simcock 62 General Counsel Executive Officers Kelli Keough has served as our Execu
tive Vice President, Group Business Unit Leader, Spend Invest Protect and Save since March 2023. Prior to joining SoFi, Dr. Keough served as a Managing Director at JPMorgan Chase &
 Co. from November 2015 to February 2023, including as Global Head of Digital Wealth Management at JPMC Asset & Wealth Management and as Head of Product, Digital and Client Solutio
ns at JPMorgan Wealth Management. She also served as a member of the board of directors of JPMorgan Securities, LLC from 2021 to 2023. Previously, Dr. Keough served in a variety of
 executive roles at Charles Schwab & Co. Inc. from April 2003 to November 2015, including as Senior Vice President of Schwab Trading Services and optionsXpress. Dr. Keough holds a 
bachelor of arts from Yale University and a master of arts in psychology and a doctorate of philosophy in psychology from Stanford University. Christopher Lapointe has served as ou
r Chief Financial Officer since May 2021. Mr. Lapointe served in the same capacity at Social Finance from September 2020 until May 2021. Mr. Lapointe served in multiple leadership 
roles at Social Finance including interim Chief Financial Officer beginning in April 2020 and Head of Business Operations beginning in June 2018. Prior to joining SoFi, Mr. Lapoint
e served as the Global Head of FP&A, Corporate Finance and FinTech at Uber Technologies, Inc., a company providing ridesharing services, from November 2015 to June 2018. Previously
, Mr. Lapointe served as Vice President of Technology, Media & Telecommunications Investment Banking at Goldman Sachs from July 2012 to November 2015. Mr. Lapointe holds a bachelor
 of arts from Dartmouth College and a master of business administration from the Tuck School of Business at Dartmouth College. Arun Pinto has served as our Chief Risk Officer since
 February 2024. Prior to joining SoFi, Mr. Pinto served as Chief Risk Officer of Consumer, Small and Business Banking division at Wells Fargo Bank, N.A., a banking institution, fro
m August 2021 to February 2024. Previously, Mr. Pinto held several management roles throughout his career, including Chief Risk Officer roles at JPMorgan Chase & Co., a banking ins
titution, where he was Chief Risk Officer of the Auto Business from 2018 to 2021 and, prior to such role, Chief Risk Officer for Mortgage Servicing and Capital Markets. Previously,
 Mr. Pinto also worked at Bank of America, a banking institution, in a number of second line risk executive roles including leading risk oversight of the Mass Affluent Strategy and
 leading Consumer and Quantitative Analytics. Mr. Pinto holds a bachelor of science in chemical engineering from the University of California at Berkeley. Jeremy Rishel has served 
as our Chief Technology Officer since June 2022, in which role Mr. Rishel oversees SoFi’s products, technology strategy and architecture, and the Company’s investment in emerging t
echnology and data. He is also responsible for ensuring company-wide collaboration on areas of common technology needs, technology strategy, architecture, infrastructure, and emerg
ing technology opportunities. Prior to joining SoFi, Mr. Rishel served as Senior Vice President of Engineering at Splunk, Inc., a technology company, from June 2019 to June 2022, w
here he was responsible for all software development, testing, operations, infrastructure, and program management functions. Mr. Rishel joined Splunk in April 2018 as Vice Presiden
t of Engineering. Prior to Splunk, Mr. Rishel served as Vice President of Engineering at DoorDash, Inc., a technology company specializing in food delivery services, from October 2
017 to April 2018. From April 2015 to June 2017, Mr. Rishel served as Vice President of Engineering at Twitter (now known as X), a social media company, where he led a variety of p
roduct and engineering groups, including video products and engineering, machine learning and product data science, and engineering for all advertising products, data products, and
 developer tools. Mr. Rishel 24 SoFi Technologies, Inc. Table of Contents holds two bachelors of science from the Massachusetts Institute of Technology (“MIT”) and a master of busi
ness administration from MIT’s Sloan School of Management. Eric Schuppenhauer has served as our Executive Vice President, Group Business Unit Leader, Borrow since August 2024. Prio
r to joining SoFi, Mr. Schuppenhauer served as Executive Vice President, Head of Consumer Lending at Citizens Financial Group, a banking institution, from March 2018 to August 2024
. Previously, Mr. Schuppenhauer led the mortgage originations and servicing businesses at Capital One, and held senior leadership roles at JPMorgan Chase & Co., including leading t
he company’s mortgage originations and servicing businesses, and as their mortgage Chief Financial Officer. Mr. Schuppenhauer holds a bachelor of science in Commerce: Accounting fr
om the University of Virginia and is a Certified Public Accountant. Stephen Simcock has served as our General Counsel and Secretary since June 2024. Prior to joining SoFi, Mr. Simc
ock had served as Managing Director and General Counsel of Consumer Banking, and Vice Chair of the Legal Department at JPMorgan Chase & Co. during the period from October 2014 to J
une 2024. Previously, Mr. Simcock served as the General Counsel of Citigroup, Inc.’s Global Consumer Business, and held similar roles within the firm’s mortgage lending, commercial
 and small business, and consumer banking units. Mr. Simcock holds a bachelor of arts in French literature from Colby College and a juris doctorate degree from Washington and Lee U
niversity School of Law. 25 SoFi Technologies, Inc. Table of Contents COMPENSATION DISCUSSION AND ANALYSIS This Compensation Discussion and Analysis provides information regarding 
the 2024 compensation program for our principal executive officer, our principal financial officer, and our three most highly-compensated executive officers (other than our princip
al executive officer and principal financial officer) who were serving as our executive officers at the end of the last completed year. These individuals are our “Named Executive O
fficers” or “NEOs.” For 2024, our Named Executive Officers were: • Anthony Noto, our Chief Executive Officer (our “CEO”); • Christopher Lapointe, our Chief Financial Officer (our “
CFO”); • Arun Pinto, our Chief Risk Officer; • Eric Schuppenhauer, our Executive Vice President and Group Business Unit Leader, Borrow; and • Stephen Simcock, our General Counsel. 
This Compensation Discussion and Analysis describes the material elements of our executive compensation program during 2024. It also provides an overview of our executive compensat
ion philosophy, including our principal compensation policies and practices. Finally, it analyzes how and why we arrived at the specific compensation decisions for our Named Execut
ive Officers in 2024 and discusses the key factors that were considered in determining their compensation. Executive Leadership Changes in 2024 Effective February 7, 2024, Mr. Pint
o joined the Company as our Chief Risk Officer. Effective June 3, 2024, Mr. Simcock joined the Company as our General Counsel. Effective August 12, 2024, Mr. Schuppenhauer joined t
he Company as our Executive Vice President, Group Business Unit Leader, Borrow. Executive Summary Who We Are SoFi is a mission-driven company designed to help our members achieve f
inancial independence in order to realize their ambitions. To us, financial independence does not mean being wealthy, but rather represents the ability of our members to have the f
inancial means to achieve their personal objectives at each stage of life, such as owning a home, having a family, or having a career of their choice — more simply stated, to have 
enough money to do what they want. We were founded in 2011 and have developed a suite of financial products that offers the speed, selection, content and convenience that only an i
ntegrated digital platform can provide. In order for us to achieve our mission, we have to help people get their money right, which means providing them with the ability to borrow 
better, save better, spend better, invest better and protect better. Everything we do today is geared toward helping our members “Get Your Money Right” and we strive to innovate an
d build ways for our members to achieve this goal. In order to help achieve our mission, we are a member-centric, one-stop shop for financial services that, through our Lending and
 Financial Services products, allows members to borrow, save, spend, invest and protect their money. We refer to our customers as “members” and “clients.” We offer personal loans, 
student loans, home loans and related servicing, and a variety of financial services products, such as SoFi Money, SoFi Credit Card, SoFi Invest and SoFi Relay, that provide more d
aily interactions with our members, as well as products and capabilities, such as SoFi At Work, that are designed to appeal to enterprises. In addition, lending-related services th
at we offer through our Loan Platform Business help a broader range of borrowers to find lending solutions, through our relationships with members as well as third-party enterprise
 partners. We have also made strategic acquisitions to further expand our technology platform capabilities for enterprises, which we believe deepen our participation in the entire 
technology ecosystem powering digital financial services. We have built a personalized area within our digital native application, which we refer to as the member home experience. 
The member home experience is personalized and delivers content to a member about what they must do that day in their financial life, what they should consider doing that day in th
eir financial life, and what they can do that day in their financial life. Through the member home experience, there are significant opportunities to build frequent engagement and,
 to 26 SoFi Technologies, Inc. Table of Contents date, the member home experience has been an important driver of new product adoption. The member home experience is an important p
art of our strategy and our ability to use data as a competitive advantage. To complement these products and services, we believe in establishing partnerships with other enterprise
s to leverage our existing capabilities to reach a broader market and in building vertically-integrated technology platforms designed to manage and deliver our suite of products an
d technology solutions to our members and clients in a low-cost and differentiated manner. Business Highlights In 2024, we achieved the following: • Record total net revenue of $2.
7 billion and adjusted net revenue of $2.6 billion, respectively, both up 26% respectively, over 2023; • Net income of $498.7 million and adjusted EBITDA of $666.5 million; and • T
otal members of over 10.1 million at year end, reflecting 34% year-over-year growth. Refer to Appendix A for an additional discussion of adjusted net revenue and adjusted EBITDA, w
hich are non-GAAP financial measures, as well as reconciliations to the most directly comparable GAAP measures. Executive Compensation Highlights Our executive compensation program
 is designed to attract, motivate, and retain highly qualified executives who are committed to our mission and essential to our success. A compensation structure that rewards perfo
rmance and aligns with the interests of long-term stockholders is central to our approach. To that end, we have made significant progress in prioritizing performance-based compensa
tion within our program. In 2024, 25% of our CEO’s equity compensation was tied to performance-based metrics, and this structure has been extended to other Named Executive Officers
 in 2025. In 2025, 50% of our CEO’s equity compensation was performance-based. In 2026, 50% of our CEO’s and other Named Executive Officers’ compensation will be tied to performanc
e-based metrics. This initiative supports our business strategy, strengthens our pay-for-performance culture, and drives long-term value creation for stockholders. The Compensation
 Committee and the Board of Directors, in collaboration with the Compensation Committee’s independent compensation consultants, continue to enhance and strengthen our executive inc
entive compensation programs and governance. This ongoing effort ensures that the inherent risks of incentive pay programs are appropriately assessed, discussed, monitored, and mit
igated, with risk management being a central consideration in compensation decisions. In 2024, we introduced a “Risk Management Effectiveness Assessment” program, establishing a co
nsistent framework for evaluating risk management performance. Executives are assessed based on their effectiveness under this program, and their final score is a factor in determi
ning overall compensation decisions, including impacting the final annual bonus payouts. In 2024, the compensation of our Named Executive Officers was determined as follows: • Base
 Salaries. In February 2024, the independent members of our Board of Directors determined to maintain the annual base salary of our CEO, and the Compensation Committee determined t
o maintain the annual base salary of our CFO, at their 2022 levels. The remaining Named Executive Officers were hired in 2024 and such determination was not necessary. • Performanc
e-Based Annual Cash Bonus Opportunities and Payments. Under the SoFi annual cash bonus plan (the “Annual Cash Bonus Plan”), our Named Executive Officers were eligible to earn cash 
bonus payments based on our actual performance as measured against adjusted net revenue, adjusted EBITDA, new members, and return on tangible equity (“ROTE”) metrics for 2024, as w
ell as their individual performance. For 2024, we introduced ROTE as a new metric in evaluating compensation, replacing new products, to better align performance to the overall qua
lity and sustainability of the Company’s profitability. Additionally, in 2024, a maximum payout cap of 200% of the target annual cash bonus opportunity under the Annual Cash Bonus 
Plan was implemented for the CEO and all other Named Executive Officers. In February 2024, the independent members of our Board of Directors approved keeping the CEO’s target annua
l cash bonus opportunity under the Annual Cash Bonus Plan at the 2022 level, while the Compensation Committee did the same for the CFO. Based on the Compensation Committee’s decisi
on to pay annual cash bonuses at 117.5% of their target annual cash bonus opportunities and based on individual performance, our CEO earned an annual cash bonus payment of $2,585,0
00, while our other Named Executive Officers earned 27 SoFi Technologies, Inc. Table of Contents annual cash bonus payments ranging from $226,952 to $625,000 (reflecting, where app
licable, a pro rata amount based on date of hire). • Long-Term Incentive Compensation. In February 2024, (i) the independent members of our Board of Directors granted our CEO a lon
g-term incentive compensation opportunity with a total grant date fair value of $24,132,183, 75% of which was granted as a time-based RSU award and 25% of which was granted as a pe
rformance-based restricted stock unit (“PSU”) award, each of which may be settled in shares of our Common Stock, and (ii) the Compensation Committee granted long-term incentive com
pensation opportunities in the form of RSU awards that may be settled for shares of our Common Stock to our other Named Executive Officers, with grant date fair values ranging from
 $5,577,347 to $7,728,971. Advisory Vote on Named Executive Officer Compensation and Feedback At our 2024 Annual Meeting of Stockholders, we conducted a non-binding, advisory vote 
on the compensation of our Named Executive Officers (commonly known as a “Say-on-Pay” vote). Our stockholders approved the 2023 compensation of our Named Executive Officers, with a
pproximately 90.5% of the votes cast in favor of the proposal. The Company subsequently examined the feedback received from Institutional Shareholder Services and Glass Lewis to le
arn more about existing concerns with respect to our executive compensation program. The following table includes a summary of the key feedback received from Institutional Sharehol
der Services and Glass Lewis and the actions taken by the Compensation Committee to respond to such concerns and enhance our executive compensation program. Topics What We Learned 
Actions Taken in Response 2024 Long-term incentive compensation program design Potential area of improvement with respect to the absence of performance-based equity awards in our l
ong-term incentive compensation program The Compensation Committee has introduced PSU awards with pre-established performance metrics into our long-term incentive compensation prog
ram, a key component of our post-IPO strategy to gradually integrate PSUs into the annual compensation program. As part of this plan, 25% of the CEO’s annual long-term incentive co
mpensation for 2024 was awarded in PSUs. This increased to 50% in 2025. Other NEOs received 25% of their annual long-term incentive compensation in PSUs for 2025, with this weighti
ng intended to increase to 50% in 2026, in alignment with our continued evolution of executive compensation post-IPO. Short-term incentive compensation plan design Potential area o
f improvement with respect to the absence of payout “caps” on the awards earned under our Annual Cash Bonus Plan The Compensation Committee established a limit on the maximum amoun
t that an individual executive officer may receive under our Annual Cash Bonus Plan beginning in 2024. The maximum amount is 200% of the target annual cash bonus opportunity. 2023 
Compensation peer group Potential area of improvement with respect to the inclusion of several “outsized” companies in our compensation peer group Beginning in April 2023, the Comp
ensation Committee, assisted by its compensation consultant, conducted a thorough review of our compensation peer group (removing 11 companies and adding eight new companies that a
re more similar to the Company in size) and approved a substantially revised compensation peer group in July 2023. See “ Compensation-Setting Process — Competitive Positioning ” be
low for more details. New hire compensation The new-hire compensation package awarded to one of our NEOs was large relative to the role and our peer group The Compensation Committe
e assesses new hire compensation packages to ensure they are reasonable and in line with market standards. Compensation is evaluated against our peer group to ensure alignment with
 prevailing practices. At our 2022 Annual Meeting of Stockholders, we conducted a non-binding advisory vote on the frequency of future Say-on-Pay votes (commonly known as a “Say-on
-Frequency” vote). A majority of our stockholders voted in favor of 28 SoFi Technologies, Inc. Table of Contents holding Say-on-Pay votes on an annual basis. Accordingly, our Board
 of Directors approved a resolution that, until the next non-binding advisory Say-on-Frequency vote, we will hold Say-on-Pay votes on an annual basis. Executive Compensation Progra
m Changes for 2025 and 2026 In 2025, the Compensation Committee extended the grant of PSU awards to all eligible executive officers, including our Named Executive Officers (other t
han the CEO who began receiving PSU awards in 2024). Mr. Schuppenhauer was not eligible for annual grants in 2025 due to his new hire date in 2024. In 2025, our CEO received 50% of
 the dollar value of his annual equity award in the form of a PSU award and 50% in the form of an RSU award, while our other eligible Named Executive Officers and remaining executi
ve officers received 25% of the dollar value of their annual equity award in the form of a PSU award and 75% in the form of an RSU award. In addition, we amended our Form of PSU Aw
ard Agreement under the Amended and Restated 2021 Stock Option and Incentive Plan for SoFi Technologies, Inc. (the “2021 Plan”) to include the termination rights provided under the
 Executive Severance Plan and to clarify the target goal, the method for measuring performance using a 90-trading day trailing average, and the treatment provided in the event of d
eath or disability, as outlined under the Company’s death and disability policy. Additionally, for Mr. Noto and Mr. Lapointe, their amended Form of PSU Award Agreement clarifies th
e termination rights provided in their employment agreement and promotion letter. In 2026, the Compensation Committee intends to continue to grant PSU awards to all our executive o
fficers, including our CEO and our other Named Executive Officers. Our CEO and our other Named Executive Officers and remaining executive officers, will receive 50% of the dollar v
alue of their annual equity award in the form of a PSU award and 50% in the form of an RSU award vesting quarterly over four years. Relationship Between Pay and Performance We beli
eve our executive compensation program is reasonable, competitive, and appropriately balances the goals of attracting, motivating, rewarding, and retaining our Named Executive Offi
cers with the goal of aligning their interests with those of our stockholders. To secure this alignment and to motivate and reward individual initiative and effort, we seek to ensu
re that a meaningful portion of our Named Executive Officers’ annual target total direct compensation opportunity is both variable in nature and “at-risk.” We emphasize variable co
mpensation that appropriately rewards our Named Executive Officers through two separate compensation elements: • First, we provide the opportunity to participate in our Annual Cash
 Bonus Plan, which provides cash payments if we produce short-term financial, operational, and strategic results that meet or exceed pre-established corporate goals as determined b
y our Board of Directors, and includes the evaluation of certain individual contributions in achieving those goals. • Second, we grant both RSU awards and PSU awards, from time to 
time, that may be settled for shares of our Common Stock, which in the aggregate comprise a majority of the Named Executive Officers’ annual target total direct compensation opport
unities. The value of these equity awards is tied directly to the performance of our Common Stock, thereby incentivizing our Named Executive Officers to drive long-term value creat
ion for the benefit of our stockholders. These variable pay elements ensure that, each year, a substantial portion of our Named Executive Officers’ annual target total direct compe
nsation opportunity is contingent (rather than fixed) in nature, with the amounts ultimately payable subject to variability above or below target levels commensurate with our actua
l performance. In 2024, approximately 95% of our CEO’s total direct compensation opportunity and approximately 95%, on average, of our other Named Executive Officers’ total direct 
compensation opportunity consisted of “at risk” variable compensation. We believe that this design provides balanced incentives for our Named Executive Officers to execute our oper
ational objectives and drive sustainable and profitable long-term growth. To ensure that we remain faithful to our compensation philosophy, the Compensation Committee regularly eva
luates the relationship between the values of the equity awards granted to our Named Executive Officers, the amount of compensation realizable (and, ultimately, realized) from such
 awards in subsequent years, and performance over this period. 29 SoFi Technologies, Inc. Table of Contents Executive Compensation Policies and Practices We endeavor to maintain so
und governance standards consistent with our executive compensation policies and practices. The Compensation Committee reviews our executive compensation program on an annual basis
 to ensure consistency with our short-term and long-term goals given the dynamic nature of our business and the market in which we compete for executive talent. The following summa
rizes our executive compensation-related policies and practices that were in effect during 2024. What We Do: • Maintain an Independent Compensation Committee. The Compensation Comm
ittee is comprised solely of independent directors who determine our compensation policies and practices. • Retain an Independent Compensation Consultant. Since 2020, the Compensat
ion Committee has engaged its own independent compensation consultant to provide information, analysis, and other advice on executive compensation matters independent of management
. This compensation consultant performed no other services for us during 2024. • Annual Executive Compensation Review. The Compensation Committee reviews and approves our compensat
ion strategy and program at least annually, including a review of any compensation peer group that it approves for comparative purposes and a review of our compensation-related ris
k profile to ensure that our compensation programs do not encourage excessive or inappropriate risk-taking and that the level of risk that they do encourage is not reasonably likel
y to have a material adverse effect on us. • Compensation At-Risk. Our executive compensation program is designed so that a significant portion of our Named Executive Officers’ tar
get total direct compensation opportunity is “at risk” based on corporate performance, as well as equity-based, to align the interests of our Named Executive Officers and stockhold
ers. • Use of “Pay-for-Performance” Philosophy. The majority of our Named Executive Officers’ annual target total direct compensation opportunity is directly linked to our financia
l results, overall company performance and the NEO’s individual contribution. • Multi-Year Vesting Requirements. The annual equity awards granted to our Named Executive Officers ve
st or are earned over multi-year periods, consistent with current market practice and our retention objectives. • Maintain “Double-Trigger” Change-of-Control Arrangements. Our Name
d Executive Officers may be eligible to receive certain payments and/or other benefits, such as accelerated vesting of certain of their then-outstanding and unvested equity awards,
 under the Executive Severance Plan (discussed below) or their employment agreement or employment offer letter, in the event of a change of control of the Company. These are “doubl
e-trigger” arrangements; that is, they require both a change of control of the Company plus a qualifying termination of employment before payments and benefits are paid. In additio
n, all such payments and benefits are subject to the execution and delivery of an effective general release of claims in favor of the Company. • Compensation Recovery (“Clawback”) 
Policy. In October 2023, we adopted and have since maintained a Clawback Policy that complies with the requirements of Exchange Act Rule 10D-1 and the applicable Nasdaq listing sta
ndards for our current and former executive officers (as defined in Exchange Act Rule 10D-1) and other current and former executive staff for the recovery of any erroneously awarde
d performance-based incentive compensation. In July 2024, the Clawback Policy was amended to apply to all Senior Vice Presidents and Vice Presidents, allow for recoupment of incent
ive compensation upon misconduct related matters (as defined within the Clawback Policy), and allow for the recoupment of time-based equity awards, in addition to incentive-based c
ompensation. For more information, see the section below titled “ Compensation Recovery Policy. ” • Stock Ownership Policy. We maintain a stock ownership policy applicable to our e
xecutive officers who are subject to Section 16 of the Exchange Act and the non-employee members of our Board of Directors, which is discussed under the section below titled “ Stoc
k Ownership Policy. ” This policy was amended in July 2024 to eliminate the five-year grace period for compliance, require the retention of at least 50% of all net profit shares re
ceived upon equity vesting until compliance with the policy is met, and establish minimum ownership levels based solely on a multiple of annual base salary or Board annual cash ret
ainer, as applicable. • Executive Notice Period Policy. In 2024, the Company amended the offer letters and employment agreements of our executive officers to include a requirement 
for a notice period of 60 days’ advance written notice before the termination of employment, applicable to both the Company and the executives. This notice period does not apply in
 30 SoFi Technologies, Inc. Table of Contents the case of termination of employment for Cause as defined under the relevant amended agreement. For more information, see the section
 below titled “ Executive Compensation — Executive Notice Period. ” • Health and Welfare Benefits. Our Named Executive Officers participate in broad-based Company-sponsored health 
and welfare benefit programs on the same basis as our other employees. • Succession Planning. We review the risks associated with our key executive officer positions to ensure adeq
uate succession plans are in place. What We Do Not Do: • No Executive Retirement Plans. We do not currently offer, nor do we have plans to offer, defined benefit pension plans or a
ny non-qualified deferred compensation plans or arrangements to our Named Executive Officers other than the plans and arrangements that are available to all our other employees. Ou
r Named Executive Officers are eligible to participate in our Section 401(k) retirement savings plan on the same basis as our other employees. • Limited Perquisites. In 2024, we di
d not provide perquisites and other personal benefits to our Named Executive Officers, other than our CEO, which is discussed under the section titled “ Perquisites and Other Perso
nal Benefits. ” • No Tax Payments on Change-of-Control Arrangements. We do not provide any excise tax reimbursement payments (including “gross-ups”) on payments or benefits conting
ent upon a change of control of the Company. • Hedging or Pledging of our Securities. We generally prohibit our employees, including our executive officers who are subject to Secti
on 16 of the Exchange Act, and the non-employee members of our Board of Directors and of the Board of Directors of SoFi Bank, N.A. (“SoFi Bank”), from short-selling our Common Stoc
k, buying or selling puts or calls or other derivative securities on our Common Stock, or hedging our Common Stock or other securities, and further prohibit our executive officers 
who are subject to Section 16 of the Exchange Act, the non-employee members of our Board of Directors and of the Board of Directors of SoFi Bank, members of the SoFi Senior Leaders
hip Group, and designated employees in our Finance and Accounting functions from short-term trading, trading on margin, including holding our Common Stock or other securities in a 
margin account, and pledging our Common Stock or other securities as collateral for a loan unless both our Compliance Officer and our Board of Directors provide written approval. S
uch trade restrictions, however, do not apply to approved forward- or option-based hedging or monetization contracts or transactions for any executive officer or director, so long 
as they meet certain requirements, including, but not limited to, that such contracts or transactions: (i) are reviewed and approved by our Compliance Officer prior to execution, (
ii) meet the exemption available under Rule 16c-4 of the Exchange Act and the executive officer or director meets defined continued ownership requirements, and (iii) are entered in
to in good faith when such executive staff member or director is not in possession of material non-public information. We also require that entry into any such contract is approved
 by the Compensation Committee. • No Stock Option Re-pricing. We do not permit options to purchase shares of our Common Stock to be re-priced to a lower exercise price without the 
approval of our stockholders. Executive Compensation Philosophy and Objectives We take a principled approach in providing fair, relevant, and competitive compensation and benefits 
to a dynamic workforce with diverse needs. Our compensation programs are designed to attract, motivate, and retain talented, deeply qualified, and committed individuals who believe
 in our mission, while rewarding our executive officers for long-term value creation. To further these objectives, our executive compensation program focuses on the following princ
iples: • Pay for performance where our executive officers’ compensation is aligned to our performance, in addition to individual contribution and impact. • Ensure our short- and lo
ng-term incentive plan design and governance processes appropriately balance risks with compensation outcomes. • Aim to balance short-term versus long-term compensation and fixed a
mounts of cash with variable incentive compensation. • Align executive compensation to the long-term interests of our stockholders by aligning their pay to our actual performance, 
while seeking to promote a long-term commitment to the Company by our executive officers. 31 SoFi Technologies, Inc. Table of Contents • Strive for a fair, competitive, transparent
, equitable, and well governed approach in recognizing and rewarding our executives. Executive Compensation Design Our executive compensation program is shaped by various factors, 
with the primary goals of aligning the interests of executive officers and stockholders, linking pay to performance, and ensuring a balance between managing risk and upholding stro
ng governance. When reviewing the design of our executive compensation program, the Compensation Committee considers the competitive market for corresponding positions within compa
rable geographic areas and companies of similar size and stage of development operating in our industry. This consideration is based on the general knowledge of the members of the 
Compensation Committee as augmented by competitive market data developed and analyzed by its compensation consultant. The Compensation Committee and, in the case of our CEO, the in
dependent members of our Board of Directors, approve compensation decisions for each executive officer on an individual basis after a thorough discussion of the various factors des
cribed below. As we continue to gain experience as a public company, we expect that the specific direction, emphasis, and components of our executive compensation program will cont
inue to evolve as determined by the Compensation Committee. We have begun to transition to a more empirically-based approach that involves positioning our executive compensation ag
ainst the competitive market based on an analysis of peer group data and broad-based executive compensation surveys. Compensation-Setting Process Role of Compensation Committee The
 Compensation Committee is responsible for discharging the responsibilities of our Board of Directors relating to the compensation of our executive officers, including our Named Ex
ecutive Officers (other than our CEO) and the non-employee members of our Board of Directors. The Compensation Committee formulates and presents compensation recommendations for ou
r CEO to the independent members of our Board of Directors for approval. The Compensation Committee has the overall responsibility for overseeing our compensation and benefits poli
cies generally, and overseeing, evaluating, and approving the compensation plans, policies, and practices applicable to our executive officers, including our Named Executive Office
rs. The Compensation Committee evaluates and determines any compensation adjustments or awards to our executive officers (other than our CEO) or, in the case of our CEO or otherwis
e in the Compensation Committee’s discretion, recommends such adjustments and awards to the independent members of our Board of Directors for final determination. As part of this r
eview process, the Compensation Committee applies the objectives described above within the context of our overall compensation philosophy while simultaneously considering the comp
ensation levels needed to ensure our executive compensation program remains competitive based on input from and market data provided by its compensation consultant. The Compensatio
n Committee also evaluates whether we are meeting our retention objectives and the potential cost of replacing key executive officers. In carrying out its responsibilities, the Com
pensation Committee evaluates our compensation policies and practices with a focus on the degree to which these policies and practices reflect our executive compensation philosophy
, develops strategies, and makes decisions that it believes further our philosophy or aligns with developments in best compensation practices, and reviews the performance of our ex
ecutive officers when making decisions with respect to their compensation. The Compensation Committee’s authority, duties, and responsibilities are further described in its charter
, which is reviewed annually and revised and updated as warranted. The Compensation Committee has retained a compensation consultant (as described below) to provide support in its 
review and assessment of our executive compensation program; however, the Compensation Committee exercises its own judgment in making final decisions and recommendations with respe
ct to the compensation of our executive officers, including our Named Executive Officers. Setting Target Total Direct Compensation During the first quarter of each year, the Compen
sation Committee conducts a review of the compensation arrangements of our executive officers, including our Named Executive Officers. As part of this review, the Compensation 32 S
oFi Technologies, Inc. Table of Contents Committee evaluates the base salary levels, annual cash bonus opportunities, and long-term incentive compensation opportunities of our exec
utive officers, including our Named Executive Officers, and all related performance criteria. The Compensation Committee does not establish a specific target for formulating the an
nual target total direct compensation opportunities of our executive officers. In making decisions about the compensation of our executive officers, including our Named Executive O
fficers (other than our CEO) and recommendations about the compensation of our CEO to the independent members of our Board of Directors, the members of the Compensation Committee r
ely on their general experience and subjective considerations of various factors (in combination with the guidance provided by the compensation consultant), including the following
: • our executive compensation program objectives; • our performance against the financial, operational, and strategic objectives established by the Compensation Committee and our 
Board of Directors; • each individual executive officer’s knowledge, skills, experience, qualifications, and tenure relative to other similarly situated executives at companies in 
the competitive market; • the scope of each executive officer’s role and responsibilities compared to other similarly situated executives at companies in the competitive market; • 
the prior performance of each individual executive officer, based on a subjective assessment of his or her contributions to our overall performance, ability to lead his or her func
tion or business unit and work as part of a team, all of which reflect our core values; • the potential of each individual executive officer to contribute to our long-term financia
l, operational, and strategic objectives; • each individual executive officer’s effectiveness in identifying, measuring, monitoring, and controlling risks within the Company and th
eir respective business units; • our CEO’s compensation relative to that of our other executive officers, and compensation parity among our executive officers; • our financial perf
ormance relative to our peers; • the compensation practices of our compensation peer group and the companies in selected broad-based compensation surveys and the positioning of eac
h executive officer’s compensation in a ranking of peer company compensation levels based on an analysis of competitive market data and selected broad-based compensation surveys; a
nd • the recommendations of our CEO with respect to the compensation of our executive officers (except with respect to his own compensation). These factors provide the framework fo
r compensation decision-making and final decisions regarding the annual total direct compensation opportunity for each executive officer, including our Named Executive Officers. No
 single factor is determinative in setting compensation levels, nor is the impact of any individual factor on the determination of pay levels quantifiable. As described further bel
ow, the Compensation Committee works with its compensation consultant to use compensation data from both a representative group of peer companies and, to the extent that additional
 compensation data is necessary to obtain an understanding of the competitive practices for certain executive positions (as well as a general understanding of market compensation l
evels), compensation data from relevant cuts of broad compensation surveys, to compare and analyze the compensation levels of our executive officers, including our Named Executive 
Officers, against the competitive market and to assist the Compensation Committee in setting compensation levels and making specific compensation decisions with respect to our exec
utive officers, including our Named Executive Officers. Role of Management In discharging its responsibilities, the Compensation Committee works with members of our management, inc
luding our CEO. Our management assists the Compensation Committee by providing information on corporate and individual performance, market compensation data, and management’s persp
ective on compensation matters. The Compensation Committee solicits and reviews our CEO’s proposals with respect to program structures, as well as his recommendations for 33 SoFi T
echnologies, Inc. Table of Contents adjustments to annual cash compensation, long-term incentive compensation opportunities, and other compensation-related matters for our executiv
e officers (except with respect to his own compensation). At least once each year, our CEO reviews the performance of our other executive officers, including our other Named Execut
ive Officers, based on such individual’s level of success in accomplishing the business objectives established for the individual for the prior year, the individual’s effectiveness
 in identifying, measuring, monitoring, and controlling risks within the Company and their respective business units, and the individual’s overall performance during that year, and
 then makes recommendations to the Compensation Committee. The Compensation Committee reviews and discusses the CEO’s proposals and recommendations (other than with respect to his 
own compensation) and considers them as one factor in determining and approving the compensation of our executive officers. Our CEO generally attends meetings of our Board of Direc
tors and the Compensation Committee at which executive compensation matters are addressed, except with respect to discussions involving his own compensation. Role of Compensation C
onsultant The Compensation Committee has the sole authority to retain an external compensation consultant to assist it by providing information, analysis, and other advice relating
 to the compensation of our executive officers, including our Named Executive Officers, including the authority to approve the compensation consultant’s reasonable fees and other r
etention terms. The compensation consultant reports directly to the Compensation Committee and its chair, and serves at the discretion of the Compensation Committee, which reviews 
the engagement annually. The Compensation Committee initially engaged Compensia, Inc. (“Compensia”), a national compensation consulting firm, in 2020 to serve as the Compensation C
ommittee’s compensation consultant to advise on executive compensation matters, including competitive market pay practices for our executive officers, including our Named Executive
 Officers, and with data analysis and the selection and updating of our compensation peer group. The Compensation Committee continued to engage Compensia in 2024 to provide these s
ervices. During 2024, Compensia attended the meetings of the Compensation Committee (both with and without management present) as requested and provided various services, including
 the analysis and selection of our compensation peer group, the review and analysis of the annual target total direct compensation opportunities for our executive officers, includi
ng our Named Executive Officers, the review and analysis for the introduction of PSU awards into our long-term incentive compensation program, the review and analysis of executive 
severance and change-of-control market practices, the review and analysis of various other compensation policies, the preparation of a compensation-related risk assessment for our 
executive compensation program, and the review and analysis of the compensation for the non-employee members of our Board of Directors. The terms of Compensia’s engagement include 
reporting directly to the Compensation Committee chair. At the request of the Compensation Committee, Compensia also coordinated with our management for data collection and informa
l market comparisons for our Named Executive Officers. In 2024, Compensia did not provide any other services to us. The Compensation Committee has evaluated its relationship with C
ompensia to ensure that it believes that such firm is independent from management. This review process included a review of the services that such compensation consultant provided,
 the quality of those services and the fees associated with the services provided during 2024. Based on this review, as well as consideration of the factors affecting independence 
set forth in Exchange Act Rule 10C-1(b)(4), Rule 5605(d)(3)(D) of the Nasdaq Marketplace Rules, and such other factors as were deemed relevant under the circumstances, the Compensa
tion Committee has determined that no conflict of interest was raised as a result of the work performed by Compensia. Competitive Positioning The Compensation Committee believes th
at peer group comparisons are useful guides to evaluate the competitiveness of our executive compensation program and related policies and practices. For purposes of assessing our 
executive compensation against the competitive market, the Compensation Committee reviews and considers the compensation levels and practices of a select group of peer companies. T
his compensation peer group consists of technology and financial services companies that are similar to us in terms of revenue, market capitalization and scope of business. The com
petitive data drawn from this compensation peer group is one of several factors that the Compensation Committee considers in making its decisions and recommendations with respect t
o the compensation of our executive officers, including our Named Executive Officers. 34 SoFi Technologies, Inc. Table of Contents In July 2023, the Compensation Committee approved
 a compensation peer group with the assistance of Compensia to consider in the analysis of the compensation of our executive officers, including our Named Executive Officers. In id
entifying and selecting the companies to comprise the compensation peer group, Compensia considered the following primary criteria: • publicly-traded companies headquartered in the
 United States or with public executive compensation disclosures; • companies with a focus on technology, consumer finance, investment banking & brokerage, regional banks, and fina
ncial exchanges & data; • companies within an annual revenue range of 0.33x to 3.0x our revenue; and • companies within a market capitalization range of 0.25x to 4.0x our market ca
pitalization. After evaluating the proposed peer companies against these criteria, the Compensation Committee approved the following compensation peer group in July 2023: Affirm Ho
ldings Credit Acceptance Rocket Companies Ameriprise Financial Etsy Shift4 Payments Black Knight First Horizon Smartsheet Block Interactive Brokers Group Toast Capital One Financia
l Pinterest Zillow Group Charles Schwab Robinhood Markets This compensation peer group was used by the Compensation Committee to inform 2024 compensation decisions. The Compensatio
n Committee used data drawn from the companies in our compensation peer group, as well as surveys drawn from the Radford Global Compensation Database, where appropriate, to evaluat
e the competitive market when determining the annual target total direct compensation opportunities for our executive officers, including our Named Executive Officers, for 2024, in
cluding base salary, target annual cash bonus opportunities, and long-term incentive compensation opportunities. The Compensation Committee reviews our compensation peer group annu
ally and makes adjustments to its composition if warranted, taking into account changes in both our business and the businesses of the companies in the peer group. Compensation Ele
ments Generally, our executive compensation program in 2024 consisted of three principal elements — base salary, annual cash bonus opportunities, and long-term incentive compensati
on opportunities in the form of equity awards. It also included participation in our broad-based health and welfare benefit programs. Element Type of Element Compensation Element O
bjective Base Salary Fixed Cash Designed to attract and retain executives by providing a competitive fixed amount of cash compensation based on the executive’s role, prior experien
ce, and expected contributions to the Company Annual Cash Bonuses Variable Cash Designed to motivate our executives to achieve business objectives tied to specific Company metrics 
and which are aligned to our annual priorities, with the payout opportunity based on Company and individual performance Long-Term Incentive Compensation Variable Equity awards in t
he form of RSU and PSU awards that may be settled for shares of our Common Stock Designed to align the interests of our executives and our stockholders while helping to attract and
 retain talented leaders by paying for performance We also provide post-employment compensation (severance and change of control) payments and benefits that are consistent with our
 view of competitive market practices, and other benefits, such as health and welfare programs, including a 35 SoFi Technologies, Inc. Table of Contents Section 401(k) Plan. In gen
eral, our executive officers participate in the standard employee health and welfare benefit programs available to our employees generally. Base Salary Base salary represents the f
ixed portion of the compensation of our executive officers, including our Named Executive Officers, and is a critical element of compensation intended to attract and retain highly 
talented individuals. Generally, the base salary for each executive officer is intended to provide a fixed amount of cash compensation that is based on his or her individual role, 
experience, and expected contributions to the Company. Base salary is also designed to provide our Named Executive Officers with steady cash flow during the course of the year that
 is not contingent on short-term variations in our corporate performance. In February 2024, the Compensation Committee reviewed the annual base salaries of our executive officers, 
including our Named Executive Officers, taking into consideration a competitive market analysis prepared by its compensation consultant, the recommendations of our CEO (except with
 respect to his own base salary) and the other factors set forth in “ Compensation-Setting Process — Setting Target Total Direct Compensation ” above. Following this review, the Co
mpensation Committee recommended to the independent members of our Board of Directors that the annual base salary for our CEO be maintained at its 2022 level, and the Board of Dire
ctors approved this recommendation. The Compensation Committee also approved maintaining the annual base salary for our CFO at its 2022 level. The remaining Named Executive Officer
s were hired in 2024 and therefore such determination was not necessary. The annual base salaries of our Named Executive Officers were as follows: Named Executive Officer 2023 Base
 Salary ($) 2024 Base Salary ($) Percentage Adjustment Mr. Noto $ 1,000,000 $ 1,000,000 — % Mr. Lapointe 500,000 500,000 — % Mr. Pinto (1) N/A 500,000 — % Mr. Schuppenhauer (1) N/A
 500,000 — % Mr. Simcock (1) N/A 500,000 — % __________________ (1) Messrs. Pinto, Schuppenhauer, and Simcock joined the Company in 2024 and received a prorated base salary for 202
4 as set forth in the 2024 Summary Compensation Table. The base salaries in the table above reflects their annualized base salaries. The base salaries paid to our Named Executive O
fficers during 2024 are set forth in the “ 2024 Summary Compensation Table ” below. Annual Cash Bonus Plan We provide our executive officers, including our Named Executive Officers
, with the opportunity to earn annual cash bonuses that are intended to encourage the achievement of corporate performance goals and effective risk management. For 2024, the Annual
 Cash Bonus Plan was based on the achievement of three pre-established financial performance objectives and the achievement of one pre-established operational performance objective
. To be eligible to receive an annual cash bonus payment, a participant, including a Named Executive Officer, must be employed by us on the last calendar day of the applicable Annu
al Cash Bonus Plan period, in this case, December 31, 2024. Starting in 2025, the policy was amended to require continued employment on the bonus payout date for eligibility to rec
eive the annual cash bonus payment. The individual components of the Annual Cash Bonus Plan discussed below were chosen because the Compensation Committee believes each component p
roperly and effectively motivates each executive officer, including each Named Executive Officer, to achieve the Company’s pre-established corporate goals and their individual perf
ormance goals. Target Annual Cash Bonus Opportunities Under the Annual Cash Bonus Plan, each executive officer, including each Named Executive Officer, is assigned a target annual 
cash bonus opportunity, expressed as a percentage of his or her annual base salary. In February 2024, the Compensation Committee reviewed the target annual cash bonus opportunities
 of our executive officers, including our Named Executive Officers, taking into consideration a competitive market analysis prepared by its compensation consultant, 36 SoFi Technol
ogies, Inc. Table of Contents the recommendations of our CEO (except with respect to his own target annual cash bonus opportunity) and the other factors set forth in “ Compensation
-Setting Process — Setting Target Total Direct Compensation ” above. Following this review, the Compensation Committee recommended to the independent members of our Board of Direct
ors that the target annual cash bonus opportunity for our CEO once again be maintained at its 2022 level, and the Board of Directors approved this recommendation. The Compensation 
Committee also approved once again maintaining the target annual cash bonus opportunity for our CFO at its 2022 level. The remaining Named Executive Officers were hired in 2024 and
 therefore such determination was not necessary. The target annual cash bonus opportunities of our Named Executive Officers, as a percentage of annual base salary, were as follows:
 Named Executive Officer 2023 Target Annual Cash Bonus (as a percentage of base salary) 2024 Target Annual Cash Bonus (as a percentage of base salary) Percentage Adjustment Mr. Not
o 200% 200% — % Mr. Lapointe 100% 100% — % Mr. Pinto N/A 100% — % Mr. Schuppenhauer N/A 100% — % Mr. Simcock N/A 100% — % Corporate Performance Objectives In February 2024, the Com
pensation Committee selected our annual adjusted net revenue, adjusted EBITDA, ROTE, and new members as the key performance metrics for the Annual Cash Bonus Plan. These metrics we
re chosen to ensure a balanced approach to driving revenue growth, managing expenses, fostering sustainable profitability, and enhancing long-term stockholder value. To align with 
our strategic objectives, the Compensation Committee assigned weightings to each performance metric as follows: 35% for adjusted net revenue, 35% for adjusted EBITDA, 15% for ROTE,
 and 15% for new members. The Compensation Committee believes these performance metrics are appropriate for our business and reflect the most critical drivers of success for the 20
24 operating plan. Final bonus payouts are subject to a modifier based on the executive officers’ performance in managing risk under the Risk Management Effectiveness Assessment pr
ogram. For more information on the Risk Management Effectiveness Assessment program, see “ Executive Compensation Highlights ” above. For definitions of the metrics, please see the
 section titled “ Executive Compensation — Pay Versus Performance — Tabular List of Performance Measures .” Performance Measure Achievement and Payment Matrix In February 2024, the
 Compensation Committee set the performance levels for each of the corporate performance metrics for purposes of the Annual Cash Bonus Plan as follows: Performance Level Performanc
e Achievement Payment Percentage (1) Maximum 150% and above 150% Target 80% 100% Threshold 50% and below ≤ 50% __________________ (1) The payment percentages below and between each
 corporate performance threshold are calculated on a linear basis. Annual Cash Bonus Plan Payments In January 2025, the Compensation Committee evaluated our actual performance agai
nst the corporate performance metrics and determined that we had achieved (i) 105% of our target adjusted net revenue performance measure for a payment percentage of 118%, (ii) 93%
 of our target adjusted EBITDA performance measure for a payment percentage of 109%, (iii) 134% of our target new members measure for a payment percentage of 138%, and (iv) 101% of
 our target ROTE measure for a payment percentage of 115%, for an aggregate payment percentage of 118%. Notwithstanding the actual aggregate payment 37 SoFi Technologies, Inc. Tabl
e of Contents percentage as determined under the Annual Cash Bonus Plan, the Compensation Committee decided to adjust the aggregate payment percentage to 117.5%. Annual cash bonuse
s for each of our executive officers, including our Named Executive Officers, were determined based on the achievement of performance objectives, individual performance, and the ef
fectiveness of risk management as assessed under the Risk Management Effectiveness Assessment program. For 2024, all Named Executive Officers received satisfactory ratings for risk
 management, and as a result, their final bonus payouts were not subject to any adjustments. The final bonus determination was made by the independent members of our Board of Direc
tors in the case of our CEO and by the Compensation Committee in the case of our other Named Executive Officers. In view of such assessments, our Named Executive Officers received 
the following annual cash bonus payments for 2024: Named Executive Officer 2024 Target Annual Cash Bonus Opportunity (as a percentage of base salary) 2024 Target Annual Cash Bonus 
Opportunity ($) 2024 Target Annual Cash Bonus Opportunity at 117.5% Annual Cash Bonus Funding ($) Individual Multiplier (%) 2024 Actual Annual Cash Bonus Payment ($) Payment Percen
tage (%) Mr. Noto 200% $ 2,000,000 $ 2,350,000 110% $ 2,585,000 129% Mr. Lapointe 100% 500,000 587,500 106% 625,000 125% Mr. Pinto (1) 100% 449,315 527,945 100% 527,945 118% Mr. Sc
huppenhauer (1) 100% 193,151 226,952 100% 226,952 118% Mr. Simcock (1) 100% 289,041 339,623 94% 320,000 111% __________________ (1) Messrs. Pinto, Schuppenhauer, and Simcock joined
 the Company in 2024 and received a prorated annual cash bonus opportunity for 2024. The annual cash bonus payments awarded to our Named Executive Officers for 2024 are also set fo
rth in the “ 2024 Summary Compensation Table ” below. Long-Term Equity Incentive Compensation As a technology and financial services company that encounters significant competition
 for qualified personnel, long-term incentive compensation plays a critical role in our ability to attract, hire, motivate, and reward qualified and experienced executive officers.
 The use of long-term incentive compensation in the form of equity awards is necessary for us to compete for qualified executive officers without significantly increasing cash comp
ensation and is the most important element of our executive compensation program. We use equity awards to incentivize and reward our executive officers for long-term corporate perf
ormance based on the value of our Common Stock and, thereby, to align their interests with the interests of our stockholders. The realized value of these equity awards bears a dire
ct relationship to our stock price, and, therefore, these awards are an incentive for our executive officers to create value for our stockholders. Equity awards also help us retain
 our executive officers in a highly competitive market. In 2024, we used RSU and PSU awards that may be settled for shares of our Common Stock to motivate and reward our executive 
officers, including our Named Executive Officers, for long-term increases in the value of our Common Stock. We believe that RSUs provide a predictable form of value and effectively
 support the retention of our executive officers, while aligning their interests with the long-term goals of our stockholders. We believe that PSUs directly tie a significant porti
on of our executive officers\' annual target total direct compensation to company performance, as they are earned and vest only based on the achievement of pre-established corporat
e performance goals. Together, RSUs and PSUs serve as key tools to motivate and retain our highly valued executive officers, with the value of these awards being delivered over thr
ee- or four-year periods, contingent on their continued service. We have not applied a rigid formula in determining the size of the equity awards to be granted to our executive off
icers, including our Named Executive Officers. Instead, the Compensation Committee has exercised its judgment as to the size of the awards after taking into consideration a competi
tive market analysis prepared by its compensation consultant, the recommendations of our CEO (except with respect to his own equity award), each executive officer’s outstanding equ
ity holdings (including the current economic value of his or her unvested equity holdings and the ability of these unvested holdings to satisfy our retention objectives), the proje
cted impact of the proposed awards on our earnings, the proportion of our total shares outstanding used for annual employee long-term incentive compensation awards (our “burn rate”
) in relation 38 SoFi Technologies, Inc. Table of Contents to the annual burn rate ranges of the companies in our compensation peer group, the potential voting power dilution to ou
r stockholders in relation to the median practice of the companies in our compensation peer group, as well as the other factors described in “Compensation-Setting Process — Setting
 Target Total Direct Compensation” above. Based upon these factors, the Compensation Committee or, with respect to any award granted to the CEO, the independent members of the Boar
d of Directors, formulates and determines the size of each equity award it decides to grant at levels considered appropriate to create a meaningful opportunity for reward predicate
d on the creation of long-term stockholder value. The equity awards granted to our Named Executive Officers during 2024 are set forth in the “2024 Summary Compensation Table” and t
he “2024 Grants of Plan-Based Awards Table” below. February 2024 Annual RSU and PSU Awards to Mr. Noto and Annual RSU Award to Mr. Lapointe In February 2024, after taking into cons
ideration a competitive market analysis prepared by its compensation consultant, and the other factors set forth in “Compensation-Setting Process — Setting Target Total Direct Comp
ensation” above, the Compensation Committee recommended, and the independent members of our Board of Directors approved, the grant of an RSU award and a PSU award under the 2021 Pl
an that may be settled for 2,178,650 and 726,217 shares of our Common Stock, respectively, to our CEO based on a target value equal to $24,000,000, with the number of RSUs and PSUs
 subject to the award determined by dividing the award’s total dollar value by the average of the closing market price on the NASDAQ of one share of our Common Stock over the trail
ing 30 calendar day period ending on March 11, 2024. In February 2024, after taking into consideration a competitive market analysis prepared by its compensation consultant, the re
commendation of our CEO, and the other factors set forth in “Compensation-Setting Process — Setting Target Total Direct Compensation” above, the Compensation Committee approved the
 grant of an RSU award under the 2021 Plan that may be settled for 847,253 shares of our Common Stock to our CFO based on a target value equal to $7,000,000, with the number of RSU
s subject to the award determined by dividing the award’s total dollar value by the average of the closing market price on the NASDAQ of one share of our Common Stock over the trai
ling 30 calendar day period ending on March 11, 2024. Named Executive Officer Nature of Equity Awards Percentage of Award as RSUs RSUs (number of shares) Percentage of Award as PSU
s Target PSUs (number of shares) Total Target Value ($) Mr. Noto Annual 75 % 2,178,650 25 % 726,217 $ 24,000,000 Mr. Lapointe Annual 100 % 847,253 — % — 7,000,000 Each RSU granted 
pursuant to the awards represents a contingent right to receive one share of our Common Stock for each RSU that vests. The RSU awards vest in 16 equal quarterly increments with a v
esting commencement date beginning on March 14, 2024, in each case subject to the Named Executive Officer remaining employed with us through each applicable vesting date. The PSU a
ward vests as described below under “ 2024 PSU Award to Mr. Noto ”. 2024 New Hire RSU Awards to Mr. Pinto, Mr. Schuppenhauer, and Mr. Simcock For the Named Executive Officers hired
 in 2024, the Compensation Committee determined the appropriate levels of their new hire equity compensation after reviewing analyses of competitive market data, compensation trend
s, and other key factors such as the executive’s role, experience, and expected impact on the Company. This decision took into account, but was not limited to, competitive market p
ractices, internal pay equity, and the need to attract and retain top talent in a highly competitive industry. As a result, the Compensation Committee granted the following RSU awa
rds to our new hire Named Executive Officers: Named Executive Officer Nature of Equity Awards Percentage of Award as RSUs RSUs (number of shares) Percentage of Award as PSUs Target
 PSUs (number of shares) Total Target Value ($) Mr. Pinto New Hire 100 % 726,217 — % — $ 6,000,000 Mr. Schuppenhauer New Hire 100 % 891,694 — % — 6,500,000 Mr. Simcock New Hire 100
 % 1,141,650 — % — 7,500,000 Each RSU granted pursuant to the awards represents a contingent right to receive one share of our Common Stock for each RSU that vests. The RSU awards 
vest as to 12.5% of the RSUs on the six-month anniversary of the vesting commencement date, and 6.25% of the RSUs quarterly thereafter, subject, in each case, to the Named Executiv
e Officer’s 39 SoFi Technologies, Inc. Table of Contents continuous service on the date of vesting, over a total period of four years. Mr. Pinto’s RSU award has a vesting commencem
ent date of February 14, 2024, Mr. Schuppenhauer’s RSU award has a vesting commencement date of August 14, 2024, and Mr. Simcock’s RSU award had a vesting commencement date of June
 14, 2024. 2024 PSU Award to Mr. Noto Under the PSU award, our CEO may earn between 0% and 150% of the target number of PSUs subject to the achievement of certain pre-established A
bsolute Growth in Tangible Book Value performance targets measured over a three-year performance period starting on January 1, 2024 and ending on December 31, 2026 (the “Measuremen
t Period”), subject to a modifier based on our total stockholder return (“TSR”) compared to the Nasdaq Composite Index also measured over the Measurement Period, which will increas
e or decrease the number of PSUs that vest by 25% (capped at 187.5% of the target number of PSUs subject to the award). For purposes of the TSR calculation, we will use a 90-tradin
g-day trailing average of the closing stock price at both the start and end dates of Measurement Period. This methodology ensures a consistent and fair calculation, minimizing the 
impact of short-term volatility in the stock price. Further, if our TSR over the Measurement Period is negative, the TSR modifier is capped at target (even if our TSR exceeds the 5
0th percentile of the pre-selected index). In the event of actual performance between the threshold and target, and target and maximum, performance levels, the percentage of PSUs t
hat will be earned and vest will be calculated between each designated segment using linear interpolation. Further, if the Company’s total risk weighted capital ratio falls below 1
0.5% at any point during the Measurement Period, 100% of the PSUs will immediately be forfeited in their entirety. No PSUs will be earned and vest, if any, until after the conclusi
on of the performance period. The table below summarizes the potential payout outcomes for the 2024 PSU award granted to Mr. Noto at various performance levels achieved under the A
bsolute Growth in Tangible Book Value and relative TSR metrics. Relative TSR Modifier Threshold Target Max 25th Percentile 50th Percentile ≥75th Percentile -25% +0% +25% Absolute G
rowth in Tangible Book Value Absolute Growth in Tangible Book Value ($B) Payout % Payout as a % of Target Threshold $ 1.05 40 % 30.0 % 40.0 % 50.0 % Target 1.20 100 % 75.0 % 100.0 
% 125.0 % Maximum 1.35 150 % 112.5 % 150.0 % 187.5 % In April 2025, we amended and restated Mr. Noto’s PSU award agreement to clarify that the termination rights outlined in his em
ployment agreement would also apply to this PSU award. Additionally, we clarified the target goal, the method for measuring performance using a 90-trading day trailing average, and
 the treatment provided in the event of death or disability, as outlined under the Company’s death and disability policy. Health and Welfare Benefits Our Named Executive Officers a
re eligible to participate in the same employee benefit plans, and on the same terms and conditions, as all other eligible employees. These benefits include medical, dental, and vi
sion insurance, paid time-off, holidays, basic life insurance and supplemental life insurance, short-term and long-term disability insurance, an employee stock purchase plan, and a
 Section 401(k) retirement savings plan (the “Section 401(k) Plan”). Our Section 401(k) Plan provides eligible U.S. employees, including our Named Executive Officers, with an oppor
tunity to save for retirement on a tax-advantaged basis. Under the Section 401(k) Plan, eligible employees may defer eligible compensation subject to applicable annual contribution
 limits imposed by the Internal Revenue Service. Our employees’ pre-tax contributions are allocated to each participant’s individual account and participants are immediately and fu
lly vested in their contributions. The Section 401(k) Plan is intended to be qualified under Section 401(a) of the Internal Revenue Code (the “Code”) with the Section 401(k) Plan’s
 related trust intended to be tax exempt under Section 501(a) of the Code. The Section 401(k) Plan does not permit us to make matching contributions or profit-sharing contributions
 to eligible participants at this time and would need to be amended to add such benefits. 40 SoFi Technologies, Inc. Table of Contents We believe these benefits are generally consi
stent with those offered by other companies and specifically those companies with which we compete for employees. We design our employee benefits programs to be affordable and comp
etitive in relation to the market as well as compliant with applicable laws and practices. We adjust our employee benefits programs as needed based upon regular monitoring of appli
cable laws and practices and the competitive market. Perquisites and Other Personal Benefits Currently, we do not view perquisites or other personal benefits as a significant compo
nent of our executive compensation program. Accordingly, we do not generally provide perquisites or other personal benefits to our Named Executive Officers, other than to our CEO a
s discussed below, except those that are generally made available to our employees or in situations where we believe it is appropriate to assist an individual in the performance of
 the individual’s duties, to make the individual more efficient and effective, and for recruitment and retention purposes. During 2024, our Named Executive Officers, other than our
 CEO, did not receive perquisites or other personal benefits that were, in the aggregate, $10,000 or more for each individual. In the future, we may provide perquisites or other pe
rsonal benefits in limited circumstances, such as those described in the preceding paragraph. All future practices with respect to perquisites or other personal benefits will be ap
proved and subject to periodic review by the Compensation Committee. In 2024, because of the high visibility of our Company, our Board of Directors continued to authorize a securit
y program for the protection of our CEO based on ongoing assessments of risk. We require these security measures for our benefit because of the importance of our CEO to the Company
, and we believe the costs of our security program are necessary and appropriate business expenses since they arise from the nature of our CEO’s employment at the Company. We provi
de residential security services to Mr. Noto as our CEO. Although we view the security services provided to our CEO as necessary and appropriate business expenses, we have reported
 the aggregate incremental cost of these services in the “All Other Compensation” column of the “2024 Summary Compensation Table” below. Employment Arrangements We have entered int
o a written employment agreement with our CEO and written employment offer letters with each of our other Named Executive Officers. Each of these agreements was approved on our beh
alf by our Board of Directors and/or the Compensation Committee. We believe that these arrangements were necessary to secure the service of these individuals in a highly competitiv
e job market. As a condition to entering into the employment agreement with our CEO and the employment offer letters with our other Named Executive Officers, each Named Executive O
fficer is subject to our standard confidential information and invention assignment agreement. In filling each of our Named Executive Officer positions, we recognized the need to d
evelop competitive compensation packages to attract qualified candidates in a dynamic labor market. At the same time, in formulating these compensation packages, we were sensitive 
to the need to integrate these individuals into the executive compensation structure that we were seeking to develop, balancing both competitive and internal equity considerations.
 Each of these employment arrangements does not have a specific term, provides for “at will” employment (meaning that either we or the Named Executive Officer may terminate the emp
loyment relationship at any time without cause), and generally set forth the Named Executive Officer’s initial base salary, a target annual cash bonus opportunity, the grant of one
 or more equity awards by our Board of Directors or the Compensation Committee, and eligibility to participate in our employee benefit plans and programs in effect for similarly si
tuated employees during his or her employment. Certain of these employment agreements or employment offer letters also contain provisions for certain payments and benefits in the e
vent of certain qualifying terminations of employment, including a termination of employment following a change of control of the Company. These post-employment compensation arrang
ements are discussed in “ Post-Employment Compensation Arrangements ” below. For a detailed description of the employment arrangements with our Named Executive Officers, see “ Exec
utive Compensation — Executive Employment Arrangements. ” 41 SoFi Technologies, Inc. Table of Contents Post-Employment Compensation Arrangements We have entered into an employment 
agreement with our CEO and CFO for certain protections in the event of certain involuntary terminations of employment, including a termination of employment in connection with a ch
ange of control of the Company, in exchange for a general release of claims in favor of the Company. In addition, in the case of our CEO and CFO, all equity awards (other than with
 respect to PSU awards received in connection with the Business Combination) are subject to automatic accelerated vesting upon a change of control of the Company if such awards are
 otherwise to be canceled for no consideration upon the change of control. Notwithstanding any terms to the contrary in an employment agreement or promotion letter (such as in the 
case of our CEO and CFO), our Named Executive Officers are provided post-employment compensation arrangements under the Executive Severance Plan. For the avoidance of doubt, the be
nefits under the Executive Severance Plan are not duplicative of the benefits provided for in such employment agreement or promotion letter, provided that the Named Executive Offic
er is entitled to the "better of" benefit between what is contained in such individual agreements versus the Executive Severance Plan. This plan provides for reasonable compensatio
n in the form of severance pay and certain limited benefits to a Named Executive Officer if he or she leaves our employ under certain circumstances to facilitate his or her transit
ion to new employment. Further, we seek to mitigate any potential employer liability and avoid future disputes or litigation by requiring a departing Named Executive Officer to sig
n a general release of all claims in favor of the Company as a condition to receiving any compensation payments or benefits. We believe that these agreements help maintain our Name
d Executive Officers’ continued focus on their assigned duties to maximize stockholder value if there is a potential change of control transaction and mitigate the risk of subseque
nt disputes or litigation. The terms and conditions of the Executive Severance Plan was approved by our Board of Directors. Under the Executive Severance Plan, all payments and ben
efits in the event of a change of control of the Company are payable only if there is a connected loss of employment by a Named Executive Officer (a so-called “double-trigger” arra
ngement). We use this double-trigger arrangement to protect against the loss of retention value following a change of control of the Company and to avoid windfalls, both of which c
ould occur if vesting of either equity or cash-based awards accelerated automatically as a result of the transaction. The Executive Severance Plan does not provide Named Executive 
Officers with excise tax payments, or “gross-ups.” We believe that having in place reasonable and competitive post-employment compensation arrangements, including in the event of a
 change of control of the Company, are essential to attracting and retaining highly-qualified executive officers. The Compensation Committee does not consider the specific amounts 
payable under the Executive Severance Plan when determining our Named Executive Officers’ compensation. We do believe, however, that these arrangements are necessary to offer compe
titive compensation packages. For descriptions of the post-employment compensation arrangements of our Named Executive Officers, as well as an estimate of the potential payments an
d benefits payable under these arrangements, see “ Executive Compensation — Potential Payments Upon Termination or Change of Control. ” Other Compensation Policies Stock Ownership 
Policy In July 2022, we adopted a Director and Officer Stock Ownership Policy (the “Stock Ownership Policy”), which requires our executive officers who are subject to Section 16 of
 the Exchange Act and the non-employee members of our Board of Directors (the “Covered Individuals”) to acquire and retain long-term ownership of our equity securities to further a
lign their personal financial interests with the long-term interests of our stockholders. Under the Stock Ownership Policy, as amended in July 2024, each Covered Individual is requ
ired to hold shares of our Common Stock having an aggregate value of at least the applicable multiple of the individual’s annual base salary or annual cash retainer (exclusive of a
ny committee service fees) as set forth in the following table: 42 SoFi Technologies, Inc. Table of Contents Covered Individual Minimum Required Ownership (based on annual base sal
ary or annual cash retainer) Chief Executive Officer 6.0x annual base salary Other Covered Executive Officers 3.0x annual base salary Non-Employee Directors 5.0x annual cash retain
er For purposes of determining whether a Covered Individual has satisfied the minimum required ownership threshold, eligible equity will include shares of Common Stock owned outrig
ht by the Covered Individual, shares of Common Stock held in trust for the benefit of the Covered Individual or such person’s family, shares of Common Stock held in our employee be
nefit plans, shares of Common Stock obtained through stock option exercise, and performance-based restricted stock and RSUs if the underlying performance condition has been achieve
d. Unexercised and unvested stock options and unvested RSUs and PSUs are not eligible. The value of each Covered Individual’s share ownership is based on the weighted average closi
ng price of a share of our Common Stock as reported on Nasdaq during the last 90 trading days of each year multiplied by the number of shares of Common Stock attributable to the Co
vered Individual. If a Covered Individual fails to satisfy the minimum required ownership threshold, the Covered Individual must retain at least 50% of any net profit shares. “Net 
profit shares” are those shares of Common Stock that remain after deducting the applicable tax withholdings and the payment of any exercise or purchase price (if applicable) upon t
he vesting or settlement of equity awards or the exercise of stock options. As of December 31, 2024, a majority of Covered Individuals are in compliance with the amended policy. Th
ose still in the process of aligning with the amended policy are retaining 50% of all net profit shares until compliance is met. We anticipate full compliance from all returning di
rectors and executives in 2025. Compensation Recovery Policy Effective as of October 2, 2023, our Board of Directors, upon the recommendation of the Compensation Committee, approve
d the Clawback Policy to comply with Exchange Act Rule 10D-1 and the applicable Nasdaq listing standards (collectively, the “Final Clawback Rules”). Our Board of Directors has dele
gated to the Compensation Committee the power and authority to administer the Clawback Policy. The Clawback Policy provides for the prompt recovery, subject to limited exceptions, 
of erroneously awarded incentive-based compensation from our current and former executive officers (as defined in Exchange Act Rule 10D-1) and other executive staff in the event we
 are required to prepare an accounting restatement, in accordance with the Final Clawback Rules. The recovery of such compensation applies regardless of whether an executive office
r engaged in misconduct or otherwise caused or contributed to the requirement of an accounting restatement. Under the Clawback Policy, our Board of Directors may recover from the c
urrent and former executive officers and executive staff erroneously awarded incentive-based compensation received within a lookback period of the three completed fiscal years prec
eding the date on which we are required to prepare an accounting restatement. This policy applies with respect to all incentive-based compensation received on or after October 2, 2
023. In July 2024, this policy was amended to apply to all Senior Vice Presidents and Vice Presidents, allow for recoupment of incentive compensation upon misconduct related matter
s (as defined within the Clawback Policy), and allow for the recoupment of time-based equity awards, in addition to incentive-based compensation. Insider Trading Policy We adopted 
a Securities Trading and Section 16 Compliance Policy governing the purchase, sale, and/or other dispositions of our securities by directors, officers and employees, that we believ
e is reasonably designed to promote compliance with insider trading laws, rules and regulations, and any listing standards applicable to the registrant. In addition, it is our poli
cy to comply with applicable insider trading laws, rules and regulations, and any exchange listing standards that apply to the Company when engaging in transactions in our securiti
es. Hedging and Pledging of Securities Under our Securities Trading and Section 16 Compliance Policy, our employees, including our executive officers, and the non-employee members 
of our Board of Directors and of the Board of Directors of SoFi Bank, including any person’s 43 SoFi Technologies, Inc. Table of Contents spouse, other persons living in such perso
n’s household and minor children and entities over which such person exercises control, are prohibited from engaging in the following transactions in our Common Stock and other sec
urities: • Short sales of our Common Stock and other securities; • Options trading, including buying or selling puts or calls or other derivative securities on our Common Stock and
 other securities; and • Subject to certain exceptions, hedging, including entering into hedging or monetization transactions or similar arrangements with respect to our securities
. The prohibition on hedging does not apply to approved forward- or option-based hedging or monetization contracts or transactions for any executive officer or director, so long as
 they meet certain requirements, including, but not limited to, that such contracts or transactions: (i) are reviewed and approved by our Compliance Officer prior to execution, (ii
) meet the exemption available under Rule 16c-4 of the Exchange Act and the executive officer or director meets defined continued ownership requirements, and (iii) are entered into
 in good faith when such executive staff member or director was not in possession of material non-public information. We also require that entry into any such contract is approved 
by the Compensation Committee. In addition, our executive officers who are subject to Section 16 of the Exchange Act, the non-employee members of our Board of Directors and the Boa
rd of Directors of SoFi Bank, members of the SoFi Senior Leadership Group, and designated employees in the Finance and Accounting function who have been notified by us that they ar
e a “Specially Covered Person,” and all of their respective family members (or family trust administrators) and household members, including any person’s spouse, other persons livi
ng in such person’s household and minor children, and entities over which such person exercises control, are additionally prohibited from engaging in the following transactions in 
our stock and other securities: • Selling any of our securities of the same class at a higher price than the purchase price for at least six months after the purchasing our securit
ies, and purchasing any of our securities of the same class at a lower price than the sale price for at least six months after selling our securities; • Trading on margin, includin
g holding our stock or other securities in a margin account; and • Pledging our securities as collateral for a loan unless both our Compliance Officer and our Board of Directors pr
ovide written approval. Equity Grant Timing It is not the current practice or policy of the Compensation Committee or the Company to either take material nonpublic information into
 account when determining the timing and terms of an option award or similar award or to time the disclosure of material nonpublic information for the purpose of affecting the valu
e of executive compensation. Specifically, equity awards are typically granted annually in the first quarter of the year. Equity awards may occasionally be granted off-cycle, inclu
ding awards to new hires. In 2024, we did not grant an option or option-like award to a Named Executive Officer within the four business days before the filing of a periodic report
 or current report disclosing material non-public information and ending one business day after the filing or furnishing of such report with the SEC. Tax and Accounting Considerati
ons The Compensation Committee takes the applicable tax and accounting requirements into consideration in designing and overseeing our executive compensation program. Deductibility
 of Executive Compensation For federal income tax purposes, publicly-traded companies may be prohibited from deducting employee enumeration in excess of $1 million paid to certain 
“covered employees,” which may include certain Named Executive Officers, including, but not limited to, our Chief Executive Officer and Chief Financial Officer, under Section 162(m
) of the Code. Even if Section 162(m) may limit the compensation deduction, our Board of Directors and the Compensation Committee believe our compensation policies and practices sh
ould be designed to help us meet our established goals and objectives. While the Compensation Committee considers the impact of the Section 162(m) deduction limitation, it continue
s to compensate our executive officers, including our Named Executive Officers, in a manner that is in the best interest of our 44 SoFi Technologies, Inc. Table of Contents stockho
lders and reserves the right to make compensation decisions that may not be deductible under Section 162(m) where the Compensation Committee determines the compensation to be appro
priate and in the best interests of the Company and our stockholders. Accounting for Stock-Based Compensation The Compensation Committee takes the accounting implications into acco
unt in designing compensation plans and arrangements for our executive officers and other employees. Chief among these is ASC 718, the standard which governs the accounting treatme
nt of certain stock-based compensation. Among other things, ASC 718 requires us to record compensation expense in our income statement for all equity awards granted to our executiv
e officers and other employees. This compensation expense is based on the grant date “fair value” of the equity award and, in most cases, will be recognized ratably over the award’
s requisite service period (which, generally, will correspond to the award’s vesting schedule). This compensation expense is also reported in the compensation tables below, even th
ough recipients may never realize any value from their equity awards. Compensation Risk Assessment The Compensation Committee, with assistance from its compensation consultant, car
efully evaluates potential risks when reviewing and approving our compensation programs, policies, and practices for executive officers. These programs, including incentive plans, 
are designed with features that mitigate risks while still rewarding executive officers for achieving financial and strategic objectives through sound business judgment and balance
d risk-taking. Based on this assessment, the Compensation Committee believes that the structure of our compensation programs does not create disproportionate incentives for employe
es to take excessive risks that could have a material adverse effect on the Company. 45 SoFi Technologies, Inc. Table of Contents COMPENSATION COMMITTEE REPORT The Compensation Com
mittee has reviewed and discussed the Compensation Discussion & Analysis with management. Based on this review and discussion, the Compensation Committee recommended to the Board o
f Directors that the Compensation Discussion & Analysis be included in this Proxy Statement. Submitted by the Compensation Committee of the Board of Directors: Steven Freiberg (Cha
ir) William Borden Clara Liang The material in this report is not “soliciting material,” is not deemed “filed” with the SEC and is not to be incorporated by reference in any filing
 of SoFi under the Securities Act or the Exchange Act, whether made before or after the date hereof and irrespective of any general incorporation language in any such filing. 46 So
Fi Technologies, Inc. Table of Contents EXECUTIVE COMPENSATION 2024 Summary Compensation Table The following table sets forth information with respect to compensation awarded to, e
arned by, or paid to our NEOs during the years indicated. Name and Principal Position Year Salary ($) (1) Bonus ($) (2) Stock Awards ($) (3) Non-Equity Incentive Plan Compensation 
($) (4) All Other Compensation ($) (5) Total ($) Anthony Noto 2024 $ 1,000,000 $ — $ 24,132,183 $ 2,585,000 $ 355,000 $ 28,072,183 Chief Executive Officer 2023 1,000,000 — 14,196,0
36 2,712,000 355,850 18,263,886 2022 965,385 — 9,400,414 2,340,559 186,935 12,893,293 Christopher Lapointe 2024 500,000 — 6,794,969 625,000 — 7,919,969 Chief Financial Officer 2023
 500,000 — 5,733,893 670,000 — 6,903,893 2022 500,000 100,000 3,310,062 660,000 — 4,570,062 Arun Pinto 2024 448,077 — 5,577,347 527,945 — 6,553,369 Chief Risk Officer Eric Schuppen
hauer 2024 192,308 150,000 6,313,194 226,952 — 6,882,454 Executive Vice President, Group Business Unit Leader, Borrow Stephen Simcock 2024 288,461 — 7,728,971 320,000 — 8,337,432 G
eneral Counsel _________________ (1) In March 2022, the independent members of our Board of Directors increased the annual base salary of Mr. Noto from $850,000 to $1,000,000. (2) 
Includes the amount of discretionary bonuses paid to certain of our NEOs. Mr. Lapointe received a discretionary bonus in May 2022 in recognition of efforts undertaken in assisting 
us to obtain our bank charter. Pursuant to his employment letter, Mr. Schuppenhauer received a new hire cash signing bonus of $150,000 in September 2024. The bonus is subject to fu
ll repayment if Mr. Schuppenhauer voluntarily resigns from the Company or the Company terminates his employment for “Cause” (as defined in his employment letter) within 24 months o
f his employment start date. (3) For awards granted to the NEOs in each respective year, the amount presented represents the aggregate of the grant date fair value of RSUs and the 
value of the PSU awards as calculated in accordance with ASC 718, and disregarding any estimate of forfeitures related to service-based vesting conditions. Assuming the highest lev
el of performance achievement, the grant date fair value of the PSU award granted to Mr. Noto in 2024 would be $12,486,395. The assumptions that were used to calculate the grant da
te fair values of stock awards are disclosed in our Annual Report on Form 10-K. (4) Includes annual cash incentive bonuses earned by the NEOs and paid in March of the following yea
r. Annual cash bonuses are awarded based on achievement of Company priorities and individual performance goals. The annual cash incentive bonus determinations are described in more
 detail below under “ Executive Employment Arrangements — Annual Cash Bonuses .” (5) Includes payments by the Company on behalf of our CEO for residential security services. 47 SoF
i Technologies, Inc. Table of Contents 2024 Grants of Plan-Based Awards The following table sets forth certain information with respect to grants of non-equity incentive plan and e
quity incentive plan awards for the year ended December 31, 2024 with respect to our NEOs. Estimated Future Payouts Under Non-Equity Incentive Plan Awards Estimated Future Payouts 
Under Equity Incentive Plan Awards Grant Date Fair Value of Stock Awards ($) (3) Name Type of Award Grant Date (1) Threshold ($) (2) Target ($) (2) Maximum ($) (2) Threshold (#) Ta
rget (#) Maximum (#) Anthony Noto Time-Vesting RSU 2/13/2024 $ — $ — $ — — 2,178,650 — $ 17,472,773 PSU 2/13/2024 — — — — 726,217 1,361,657 6,659,410 Annual Cash Bonus 1,000,000 2,
000,000 4,000,000 — — — — Christopher Lapointe Time-Vesting RSU 2/13/2024 — — — — 847,253 — 6,794,969 Annual Cash Bonus 250,000 500,000 1,000,000 — — — — Arun Pinto Time-Vesting RS
U 3/11/2024 — — — — 726,217 — 5,577,347 Annual Cash Bonus 224,658 449,315 898,630 — — — — Eric Schuppenhauer Time-Vesting RSU 9/9/2024 — — — — 891,694 — 6,313,194 Annual Cash Bonus
 96,575 193,151 386,301 — — — — Stephen Simcock Time-Vesting RSU 6/3/2024 — — — — 1,141,650 — 7,728,971 Annual Cash Bonus 144,521 289,041 578,082 — — — — __________________ (1) For
 additional information on the plan-based awards granted during 2024, including vesting commencement date and vesting conditions for equity incentive plan awards, see “ Outstanding
 Equity Awards at 2024 Year-End. ” (2) Estimated future payouts under non-equity incentive plan awards reflect the NEO’s target for their full year of service in 2024 determined on
 the NEO’s base salary and target annual cash bonus in effect throughout the year. The base salary and target annual cash bonus for Mr. Noto is based on a base salary of $1,000,000
 and target annual cash bonus percentage of 200%. The base salary and target annual cash bonus for Messrs. Lapointe, Pinto, Schuppenhauer, and Simcock are based on a base salary of
 $500,000 and target annual cash bonus percentage of 100% with the payouts prorated for Messrs. Pinto, Schuppenhauer, and Simcock based on their hire dates. The final annual cash b
onus payout may range from a threshold of 50% to a maximum of 200% of the target annual cash bonus. (3) Amounts represent the aggregate of the grant date fair value of RSUs and PSU
s as calculated in accordance with ASC 718, and disregarding any estimate of forfeitures related to service-based vesting conditions. The assumptions that were used to calculate th
e grant date fair values of stock awards are disclosed in our Annual Report on Form 10-K. 48 SoFi Technologies, Inc. Table of Contents Outstanding Equity Awards at 2024 Year-End Th
e following table summarizes information about the outstanding equity incentive plan awards for each NEO as of December 31, 2024. Option Awards (1) Stock Awards Equity Incentive Pl
an Awards Name Grant Date Number of Securities Underlying Unexercised Options Exercisable (#) Option Exercise Price ($/Share) Option Expiration Date Number of Shares or Units That 
Have Not Vested (#) Market Value of Shares or Units That Have Not Vested ($) (2) Number of Unearned Shares, Units or Other Rights That Have Not Vested (#) Market or Payout Value of
 Unearned Shares, Units or Other Rights That Have Not Vested ($) (2) Anthony Noto 3/13/2018 (3) 5,228,400 $ 6.19 3/12/2028 — $ — — $ — 3/13/2018 (4) 6,448,360 9.86 3/12/2028 — — — 
— 3/11/2020 (5) — — — 94,853 1,460,736 — — 6/2/2021 (6) — — — — — 2,142,859 33,000,034 3/28/2022 (7) — — — 1,016,261 15,650,419 — — 2/16/2023 (8) — — — 847,424 13,050,330 — — 2/13/
2024 (9) — — — — — 726,217 11,183,742 2/13/2024 (10) — — — 1,770,154 27,260,372 — — Christopher Lapointe 8/10/2021 (6) — — — — — 276,963 4,265,235 3/18/2022 (11) — — — 63,720 981,2
88 — — 2/8/2023 (12) — — — 331,823 5,110,074 — — 2/13/2024 (13) — — — 688,394 10,601,268 — — Arun Pinto 3/11/2024 (14) — — — 590,052 9,086,801 — — Eric Schuppenhauer 9/9/2024 (15) 
— — — 891,694 13,732,088 — — Stephen Simcock 6/3/2024 (16) — — — 998,944 15,383,738 — — __________________ (1) All stock options granted to Mr. Noto were immediately exercisable. A
s of December 31, 2024, all of Mr. Noto’s stock options were vested. (2) The fair value is calculated as the closing price of our Common Stock (ticker symbol “SOFI”) on December 31
, 2024 of $15.40, multiplied by either (i) the number of unvested RSUs, (ii) the number of unvested PSU awards that would vest upon the achievement of the “threshold” payout, which
 equates to 1/3 rd of the awards granted, or (iii) the number of unvested PSU awards that would vest upon the achievement of the “target” payout for PSUs awarded in 2024. (3) Mr. N
oto’s options had a vesting commencement date of February 26, 2018 and vest as to 20% of the shares subject to the option on the first anniversary of the vesting commencement date 
and as to 1/60th of the shares subject to the option on each monthly anniversary thereafter, subject to Mr. Noto’s continued service to us through each such date. The options are e
xercisable at grant date. (4) Mr. Noto’s options had a vesting commencement date of February 26, 2018 and vest as to 20% of the shares subject to the option on the first anniversar
y of the vesting commencement date and as to 1/60th of the shares subject to the option on each monthly anniversary thereafter, subject to Mr. Noto’s continued service to us throug
h each such date. The options are exercisable at grant date. (5) Mr. Noto’s RSUs had a vesting commencement date of March 14, 2020. The service-based vesting condition of the RSUs 
is satisfied as to 1/20th of the RSUs on each quarterly anniversary of the vesting commencement date, subject to Mr. Noto’s continued service to us through each such date. (6) The 
PSUs vest, if at all, during the period commencing on May 28, 2022 and ending on the fifth anniversary of such vesting commencement date, subject to the achievement of specified pe
rformance goals, including (i) the volume-weighted average closing price of our Common Stock attaining $25, $35 and $45 Target Hurdles, over a 90-trading day period, and (ii) now t
hat we are a bank holding company, maintaining certain minimum standards applicable to bank holding companies, subject to continued employment on the date of vesting. (7) Mr. Noto’
s RSUs vest beginning on March 14, 2025 and will vest in four equal parts beginning on the vesting commencement date and quarterly thereafter, subject to continued employment on th
e date of vesting. (8) Mr. Noto’s RSUs had a vesting commencement date of March 14, 2023. The service-based vesting condition of the RSUs is satisfied as to 1/12th of the RSUs on e
ach quarterly anniversary of the vesting commencement date, subject to Mr. Noto’s continued service to us through each such date. (9) Mr. Noto’s PSUs vest, if at all, during the pe
riod commencing on January 1, 2024 and ending on December 13, 2026, subject to the achievement of specific performance goals, such as Absolute Growth in Tangible Book Value, total 
risk weighted capital ratio, and relative total shareholder return. (10) Mr. Noto’s RSUs had a vesting commencement date of March 14, 2024. The service-based vesting condition of t
he RSUs is satisfied as to 1/16th of the RSUs on each quarterly anniversary of the vesting commencement date, subject to Mr. Noto’s continued service to us through each such date. 
(11) Mr. Lapointe’s RSUs had a vesting commencement date of March 14, 2022. The grant is subject to quarterly time-based vesting, with unvested RSUs vesting according to the follow
ing schedule and subject to Mr. Lapointe’s continued service to us through each such date: 25,991 RSUs on each of 49 SoFi Technologies, Inc. Table of Contents March 14, 2023, June 
14, 2023, September 14, 2023, and December 14, 2023; 15,930 RSUs on each of March 14, 2024, June 14, 2024, and September 14, 2024; 15,929 RSUs on December 14, 2024; and 15,930 on e
ach of March 14, 2025, June 14, 2025, September 14, 2025, and December 14, 2025. (12) Mr. Lapointe’s RSUs had a vesting commencement date of March 14, 2023. The grant is subject to
 quarterly time-based vesting, such that all awards are fully vested after the 12th quarter subsequent to the vesting commencement date, subject to Mr. Lapointe’s continued service
 to us through each such date. (13) Mr. Lapointe’s RSUs had a vesting commencement date of March 14, 2024. The service-based vesting condition of the RSUs is satisfied as to 1/16th
 of the RSUs on each quarterly anniversary of the vesting commencement date, subject to Mr. Lapointe’s continued service to us through each such date. (14) Mr. Pinto’s RSUs had a v
esting commencement date of February 14, 2024. The service-based vesting conditions of the RSUs is satisfied as to 12.5% of the RSUs on the six-month anniversary of the vesting com
mencement date, and 6.25% of the RSUs quarterly thereafter, subject to Mr. Pinto’s continuous service on the date of vesting. (15) Mr. Schuppenhauer’s RSUs had a vesting commenceme
nt date of August 14, 2024. The service-based vesting conditions of the RSUs is satisfied as to 12.5% of the RSUs on the six-month anniversary of the vesting commencement date, and
 6.25% of the RSUs quarterly thereafter, subject to Mr. Schuppenhauer’s continuous service on the date of vesting. (16) Mr. Simcock’s RSUs had a vesting commencement date of June 1
4, 2024. The service-based vesting conditions of the RSUs is satisfied as to 12.5% of the RSUs on the six-month anniversary of the vesting commencement date, and 6.25% of the RSUs 
quarterly thereafter, subject to Mr. Simcock’s continuous service on the date of vesting. Stock Vested During 2024 There were no stock options exercised by our NEOs during the year
 ended December 31, 2024. The following table summarizes the equity incentive plan awards stock vested for each NEO to which this table applies as of December 31, 2024: Stock Veste
d Name Number of Shares Acquired on Vesting (#) Value Realized on Vesting ($) (1) Anthony Noto 3,705,211 $ 35,651,405 Christopher Lapointe 838,341 8,114,357 Arun Pinto 136,165 1,21
5,497 Eric Schuppenhauer — — Stephen Simcock 142,706 2,318,973 __________________ (1) The values reflected in the table are determined by aggregating the values realized on stock v
ested throughout the year. The value realized on vesting at each vesting date is calculated as the number of shares acquired on vesting multiplied by the Common Stock per share val
ue covering such vesting date. Executive Employment Arrangements Anthony Noto On January 23, 2018, SoFi and Anthony Noto entered into an employment agreement, which was subsequentl
y amended effective February 26, 2018 (the “Noto Agreement”), to serve as SoFi’s Chief Executive Officer. The Noto Agreement provides for standard terms of employment, including ba
se salary, annual bonus eligibility and benefits eligibility, including a target annual cash bonus opportunity equal to 100% of Mr. Noto’s base salary with a maximum bonus opportun
ity of 200% of base salary, subject to the achievement of individual and company performance metrics. In addition, as a condition to entering into the Noto Agreement, Mr. Noto is s
ubject to SoFi’s standard confidential information and invention assignment agreement. As discussed above, the Board of Directors in 2022 approved an increase to Mr. Noto’s target 
annual cash bonus opportunity to 200% of his annual base salary. In the event of a financing or offering (including certain public offerings) of the Company’s equity, Mr. Noto has 
the right to purchase, on the same terms as apply to other purchasers, up to that number of shares or securities such that, assuming maximum participation in each transaction, Mr. 
Noto’s percentage ownership of the Company’s fully diluted capitalization would be no less after the final closing of such transaction than it was immediately prior to such transac
tion. The Noto Agreement provides for payments due upon the occurrence of a Qualifying Termination and/or Change of Control. See “ Potential Payments Upon Termination or Change of 
Control ” below for details. 50 SoFi Technologies, Inc. Table of Contents On February 13, 2024, Mr. Noto received an RSU grant for 2,178,650 shares of SoFi common stock, which will
 vest in 16 equal quarterly increments beginning on June 14, 2024, subject to Mr. Noto’s continued service with SoFi. On February 13, 2024, Mr. Noto received a PSU grant for 726,21
7 shares of SoFi common stock, which will vest, if at all, during the period commencing on January 1, 2024 and ending on December 13, 2026, subject to the achievement of specific p
erformance goals, such as Absolute Growth in Tangible Book Value, total risk weighted capital ratio, and relative total shareholder return. Christopher Lapointe On May 12, 2018, So
Fi and Christopher Lapointe entered into an offer letter, which was subsequently amended on May 29, 2018 (the “Lapointe Offer Letter”), to serve as SoFi’s Vice President, Head of B
usiness Operations. The Lapointe Offer Letter provides for standard terms of employment, including base salary, bonus eligibility and benefits eligibility. Beginning in 2019, Mr. L
apointe has been eligible to participate in the Company’s annual cash bonus plan. In addition, as a condition to entering into the Lapointe Offer Letter, Mr. Lapointe is subject to
 SoFi’s standard confidential information and invention assignment agreement. On April 1, 2020, Mr. Lapointe was appointed interim Chief Financial Officer. On September 14, 2020, M
r. Lapointe was appointed Chief Financial Officer. Mr. Lapointe’s grant agreements provide for payments due upon the occurrence of a Qualifying Termination and/or Change of Control
. See “ Potential Payments Upon Termination or Change of Control ” below for details. On February 13, 2024, Mr. Lapointe received an RSU grant for 847,253 shares of SoFi common sto
ck, which will vest in 16 equal quarterly increments beginning on June 14, 2024, subject to Mr. Lapointe’s continued service with SoFi. Arun Pinto On November 2, 2023, SoFi and Mr.
 Pinto entered into an offer letter (the “Pinto Offer Letter”) for Mr. Pinto to serve as Chief Risk Officer. The Pinto Offer Letter provides for standard terms of employment, inclu
ding base salary, annual cash bonus eligibility and benefits eligibility. The Pinto Offer Letter has no specific term and provided for at-will employment. In addition, as a conditi
on to entering into the Pinto Offer Letter, Mr. Pinto is subject to SoFi’s standard confidential information and invention assignment agreement. On March 11, 2024, Mr. Pinto receiv
ed an RSU grant for 726,217 shares of Common Stock, following time-based vesting over four years, subject to Mr. Pinto’s continued service with SoFi. Eric Schuppenhauer On July 8, 
2024, SoFi and Mr. Schuppenhauer entered into an offer letter (the “Schuppenhauer Offer Letter”) for Mr. Schuppenhauer to serve as Executive Vice President, Group Business Unit Lea
der, Borrow. The Schuppenhauer Offer Letter provides for standard terms of employment, including base salary, annual cash bonus eligibility and benefits eligibility. Mr. Schuppenha
uer was also eligible for a $150,000 signing bonus, which is not earned until the second anniversary of his start date. This bonus is subject to repayment to the Company if Mr. Sch
uppenhauer voluntarily terminates his employment within 24 months of his start date or is terminated for Cause as defined within the Schuppenhauer Offer Letter. The Schuppenhauer O
ffer Letter has no specific term and provided for at-will employment. In addition, as a condition to entering into the Schuppenhauer Offer Letter, Mr. Schuppenhauer is subject to S
oFi’s standard confidential information and invention assignment agreement. On September 9, 2024, Mr. Schuppenhauer received an RSU grant for 891,694 shares of Common Stock, follow
ing time-based vesting over four years, subject to Mr. Schuppenhauer’s continued service with SoFi. 51 SoFi Technologies, Inc. Table of Contents Stephen Simcock On February 29, 202
4, SoFi and Mr. Simcock entered into an offer letter (the “Simcock Offer Letter”) for Mr. Simcock to serve as General Counsel. The Simcock Offer Letter provides for standard terms 
of employment, including base salary, annual cash bonus eligibility and benefits eligibility. The Simcock Offer Letter has no specific term and provided for at-will employment. In 
addition, as a condition to entering into the Simcock Offer Letter, Mr. Simcock is subject to SoFi’s standard confidential information and invention assignment agreement. On June 3
, 2024, Mr. Simcock received an RSU grant for 1,141,650 shares of SoFi Common Stock, following time-based vesting over four years, subject to Mr. Simcock’s continued service with S
oFi. Annual Cash Bonuses Pursuant to their employment agreement or offer letter, as applicable, each NEO is eligible to earn a cash incentive bonus under the Annual Cash Bonus Plan
 based on company and individual achievement of performance targets established by our Board of Directors in its discretion. In 2024, each of our NEOs participated in the Annual Ca
sh Bonus Plan. For 2024, each of our NEOs was eligible to earn a target cash bonus amount, which reflects a percentage of their annual base salaries. With respect to the year ended
 December 31, 2024, the performance metrics used to determine the NEOs’ annual cash bonuses are set forth above in “ Cash Incentive Compensation. ” The annual cash bonuses paid to 
each NEO for the year ended December 31, 2024 are set forth above in the “ 2024 Summary Compensation Table ” in the “ Non-Equity Incentive Plan Compensation ” column. Our Board of 
Directors also has the authority to grant additional discretionary bonuses to our NEOs on a case-by-case basis. Any discretionary bonuses awarded to an NEO for the year ended Decem
ber 31, 2024 are set forth above in the “ 2024 Summary Compensation Table ” in the “ Bonus ” column. Equity Compensation — 2011 Stock Plan On January 7, 2021, Social Finance entere
d into a merger agreement (the “Agreement”) with Social Capital Hedosophia Holdings Corp. V (“SCH”), which closed on May 28, 2021 and in conjunction with which SCH changed its name
 to SoFi Technologies, Inc. The transactions contemplated in the Agreement are collectively referred to herein as the “Business Combination.” Prior to the Business Combination, the
 Company maintained the Social Finance, Inc. 2011 Stock Plan (as Amended and Restated effective as of November 5, 2019) (the “2011 Plan”), which allowed Social Finance to grant sha
res of its common stock to employees, non-employee directors and non-employee third party consultants. The 2011 Plan was originally adopted by the Social Finance Board of Directors
 and approved by its stockholders on June 10, 2011, and the amended and restated 2011 Plan was adopted by the Social Finance Board of Directors on November 5, 2019 and approved by 
its stockholders on February 6, 2020. Upon the closing of the merger between Social Finance and Social Capital Hedosophia Holdings Corp. V (“SCH”) on May 28, 2021 (the “Closing”) i
n conjunction with which SCH changed its name to SoFi Technologies, Inc., the remaining unallocated share reserve under the 2011 Plan was cancelled and no new awards may be granted
 under such plan. Awards outstanding under the 2011 Plan were assumed by SoFi upon the Closing, converted at the relevant exchange ratio into awards for shares of Common Stock, and
 continue to be governed by the terms of the 2011 Plan. Social Finance began issuing RSUs to executives in 2017. RSUs are equity awards granted to executives that entitle the holde
r to shares of the issuer’s common stock when the awards vest. RSU grants typically vest 25% on the first vesting date, which occurs approximately one year after the date of grant,
 and ratably each quarter of the ensuing 12-quarter period. RSUs have been issued under other vesting schedules, including, but not limited to: (i) vesting at a rate of 20% after o
ne year from vesting commencement date and then monthly over an additional four years, (ii) vesting at a rate of 25% after one year and then monthly over an additional three years,
 and (iii) other vesting schedules ranging in total duration from one to four years with even or uneven vesting patterns. RSUs are measured based on the fair value of our stock on 
the date of grant. 52 SoFi Technologies, Inc. Table of Contents On May 14, 2020, certain employees, including executive officers, were given the option to exchange certain unvested
 options to purchase Social Finance common stock for unvested RSUs. The primary purpose of this tender was to offer employees who primarily received options as part of their compen
sation package an opportunity to receive RSUs. 2021 Plan In connection with the consummation of the Business Combination, the Company adopted the 2021 Plan, under which we may gran
t equity incentive awards to officers, employees, non-employee directors and independent contractors in order to attract, motivate and retain the talent for which we compete. The 2
021 Plan provides for granting stock options, stock appreciation rights, restricted stock, restricted stock units (including performance stock units), dividend equivalents and othe
r stock or cash based awards for issuance. RSUs are equity awards granted to executives that entitle the holder to shares of our Common Stock when the awards vest. For executives h
ired before January 1, 2022, new hire RSU grants typically vest 25% on the first vesting date, which occurs approximately one year after the date of grant, and ratably each quarter
 of the ensuing 12-quarter period. For executives hired on or after January 1, 2022, new hire RSU grants typically vest 12.5% on the first vesting date, which occurs approximately 
six months after the date of grant, and ratably each quarter of the ensuing 14-quarter period. RSUs have been issued under other vesting schedules, including, but not limited to: (
i) vesting at a rate of 25% after one year and then monthly over an additional three years, (ii) vesting over three years in twelve equal installments, and (iii) other vesting sche
dules ranging in total duration from one to four years with even or uneven vesting patterns. RSUs are measured based on the fair value of our stock on the date of grant. We have gr
anted PSUs under the 2021 Plan to our CEO and CFO, of which 7,985,685 PSUs remained unvested and outstanding at year end 2024.The PSUs granted following the Business Combination sh
all vest, if at all, during the period commencing on the first anniversary of the Business Combination and ending on the fifth such anniversary, subject to the achievement of speci
fied performance goals including (i) the volume-weighted average closing price of our stock attaining $25, $35 and $45 Target Hurdles, over a 90-trading day period, and (ii) now th
at we are a bank holding company, maintaining certain minimum standards applicable to bank holding companies, subject to continued employment on the date of vesting. In the event o
f a Sale Event (as defined in the 2021 Plan), the PSUs may automatically vest subject to the satisfaction of the Target Hurdles by reference to the sale price, without regard to an
y other vesting conditions. In addition, in February 2024, the Compensation Committee granted PSU awards to our CEO pursuant to our long-term incentive compensation program as desc
ribed under “ Compensation Discussion and Analysis — Compensation Elements — 2024 PSU Award to Mr. Noto ”. To the extent any future awards subject to the 2021 Plan do not provide S
ale Event treatment, the 2021 Plan provides that, upon the consummation of any such Sale Event the parties thereto may cause the assumption, continuation, or substitution of such a
wards. To the extent the parties to such Sale Event do not provide for the assumption, continuation or substitution of awards, upon the effective time of the Sale Event, the 2021 P
lan and all outstanding awards granted thereunder shall terminate. Executive Notice Period In 2024, the Company amended the offer letters and employment agreements of our executive
 officers to include a requirement for a notice period of 60 days’ advance written notice before the termination of employment, applicable to both the Company and the executive off
icers. This means that any resignation by an executive or termination of an executive by the Company shall not become effective until 60 days after written notice of resignation or
 termination is provided. This notice period does not apply in the case of termination for Cause. Under the amendment, “Cause” is defined to mean: (i) the executive officer’s willf
ul failure to perform his or her duties and responsibilities to the Company, its affiliates or subsidiaries, (ii) the commission by the executive officer of any act of fraud, embez
zlement, material dishonesty or other misconduct that is detrimental to the Company, its affiliates or subsidiaries or that otherwise has caused or would reasonably be expected to 
result in material injury or harm to the Company or its subsidiaries, (iii) the unauthorized use or disclosure by the executive officer of any proprietary information or trade secr
ets of the Company or any party to whom an obligation of nondisclosure is owed, (iv) a material breach by the executive officer of any obligations under any written agreement or co
venant with the Company, or (v) any act deemed to constitute “cause” under a written agreement with the Company and the executive officer. 53 SoFi Technologies, Inc. Table of Conte
nts During the 60-day notice period, the executive officer shall continue to perform the duties of their position to the best of their abilities and shall remain an employee of the
 Company subject to the terms of the relevant offer letter and other agreements between the executive officer and the Company, including without limitation the Confidential Informa
tion and Invention Assignment Agreement, as well as the policies and procedures of the Company. Notwithstanding the above, in the sole discretion of the Company, the Company may re
lieve an executive officer from the performance of the regular duties of the executive officer’s position, in whole or in part, at any time during the 60-day notice period, upon pr
oviding written notice to the executive officer. In that event, the executive officer will remain employed by the Company until the end of the 60-day notice period and shall contin
ue to receive the base salary, annual cash bonus, and employee benefits that the executive officer was receiving before the notice of termination of employment was issued. Equity A
cceleration - Death and Disability Benefits In July 2024, the Board of Directors approved the adoption of a death and disability policy applicable to all employees and non-employee
 directors of the Company. Under the policy, in the event of death, all unvested RSUs will fully accelerate and vest immediately. In the event of disability, unvested RSUs will ves
t based on tenure, with one year of acceleration provided for every two years of service. In the event of death or disability, PSUs tied to financial metrics will be prorated at ta
rget, while PSUs based on market metrics (e.g., total shareholder return) will be assessed based on actual performance as of the date of death or disability. The PSUs granted in co
nnection with the Closing are not eligible for accelerated vesting. Potential Payments Upon Termination or Change of Control Our NEOs are eligible for certain payments or benefits 
in connection with certain covered or qualifying terminations, or a change of control, as described herein. Executive Severance Plan Termination Without Cause, Other Than In Connec
tion with a Sale Event Under the Executive Severance Plan, Covered Executives, as defined within the plan, including our Named Executive Officers, are eligible for separation benef
its, notwithstanding any terms to the contrary in an employment agreement or promotion letter, subject to compliance with the terms and conditions set out within the Executive Seve
rance Plan. NEOs are eligible for certain payments and benefits if terminated without Cause (as defined in the Executive Severance Plan), but only if the termination does not occur
 upon a Sale Event or during the twelve-month period following a Sale Event, as defined in the 2021 Plan, as amended. If such a termination occurs, the Covered Executive is entitle
d to the following: • Salary Continuation: The Covered Executive will receive salary continuation equal to their monthly base salary for a period of 12 months following the date of
 termination, referred to as the “Severance Period.” Severance payments will cease if the Covered Executive begins new employment during the Severance Period. • Bonus: The Covered 
Executive is eligible for a prorated annual cash bonus for the year in which the termination occurs. The annual cash bonus is contingent upon the achievement of applicable bonus cr
iteria as determined by the Board of Directors. The prorated annual cash bonus will be calculated by multiplying the target annual cash bonus by a fraction, where the numerator is 
the number of days in the calendar year up to the date of termination, and the denominator is 365. • Health Benefits: The Company contributes to the cost of COBRA coverage on behal
f of the Covered Executive and any applicable dependents for no longer than the Severance Period if the Covered Executive elects COBRA coverage, and only for so long as such covera
ge continues in force. Such costs shall be determined on the same basis as the Company’s contribution to Company-provided health, dental and vision insurance coverage in effect for
 an active employee with the same coverage elections; provided that if the Covered Executive commences new employment and is eligible for a new group health plan, the Company’s con
tinued contributions to the cost of COBRA coverage shall end when the new employment begins. 54 SoFi Technologies, Inc. Table of Contents Termination Without Cause In Connection wi
th a Sale Event Under the Executive Severance Plan and subject to compliance with the terms and conditions set out within the plan, a Covered Executive whose Covered Termination oc
curs upon a Sale Event or during the 12 month period following the Sale Event, as defined in the 2021 Plan, as amended, shall be entitled to the following separation payments and b
enefits: • Salary Continuation: The Covered Executive will receive a lump sum payment equal to twelve months (the “Double Trigger Severance Period”) of their monthly base salary fo
r a period of 12 months. • Bonus: The Covered Executive will receive a lump sum payment equal to 100% of their target annual cash bonus award for the year in which the termination 
occurs, without regard to the establishment or achievement of performance goals applicable to such target annual cash bonus. • Equity: Notwithstanding the terms of any stock option
 agreement, restricted stock agreement, restricted stock unit agreement, or other stock award (“Equity Awards”), all Equity Awards held by the Covered Executive on the date of term
ination (other than Equity Awards that vest on the basis of performance and do not provide solely for time-based vesting) shall become 100% vested. • Health Benefits: The Company c
ontributions to the cost of COBRA coverage on behalf of the Covered Executive and any applicable dependents for no longer than the Double Trigger Severance Period if the Covered Ex
ecutive elects COBRA coverage, and only for so long as such coverage continues in force. Such costs shall be determined on the same basis as the Company’s contribution to Company-p
rovided health, dental and vision insurance coverage in effect for an active employee with the same coverage elections; provided that if the Covered Executive commences new employm
ent and is eligible for a new group health plan, the Company’s continued contributions toward COBRA coverage shall end when the Covered Executive’s new employment begins. In additi
on, our CEO and CFO have additional benefits in their employment agreement and offer letter, as applicable, described below. Anthony Noto Pursuant to the Noto Agreement, if the emp
loyment of Mr. Noto is terminated by SoFi without Cause (as defined in the Noto Agreement) or he resigns for Good Reason (as defined in the Noto Agreement) (together, a “Qualifying
 Termination”), Mr. Noto shall be entitled to: (i) a lump-sum cash payment equal to the sum of (x) 12 months of Mr. Noto’s base salary, and (y) 100% of Mr. Noto’s annual cash bonus
 at the higher of (a) his target level and (b) his actual level of performance reasonably projected as of the termination of Mr. Noto’s employment, (ii) the continuation of health,
 dental and vision coverage under SoFi’s group insurance benefits at no cost to Mr. Noto for 12 months, and (iii) vesting acceleration of each of Mr. Noto’s then-outstanding equity
 incentives as if he had remained in continuous service to SoFi for an additional 12 months and as if all applicable performance-based vesting conditions (if any) were met at the t
arget achievement level or, if higher, the actual level of achievement reasonably projected as of the termination of his employment, with such acceleration effective as of immediat
ely prior to the termination of his employment. Pursuant to the Noto Agreement, if Mr. Noto experiences a Qualifying Termination three months prior to or any time after a Change of
 Control (as defined in the Noto Agreement), Mr. Noto shall, in lieu of the above, be entitled to: (i) a lump-sum cash payment equal to the sum of (x) 18 months of Mr. Noto’s base 
salary, and (y) 150% of Mr. Noto’s annual bonus at the higher of (a) his target level and (b) his actual level of performance reasonably projected as of the termination of Mr. Noto
’s employment, (ii) the continuation of health, dental and vision coverage under SoFi’s group insurance benefits at no cost to Mr. Noto for 18 months, and (iii) full vesting accele
ration of each of Mr. Noto’s then-outstanding equity incentives (including as to all applicable performance-based vesting conditions (if any), which will be deemed satisfied at max
imum achievement), with such acceleration effective as of immediately prior to the later of his Qualifying Termination and SoFi’s Change of Control. Additionally, all equity awards
 are subject to automatic accelerated vesting upon a Change of Control of SoFi, if such awards are otherwise to be canceled for no consideration upon such Change of Control. 55 SoF
i Technologies, Inc. Table of Contents Mr. Noto’s severance payments and benefits are subject to the execution of a general release of claims in favor of SoFi. Christopher Lapointe
 Effective September 14, 2020, when Mr. Lapointe was appointed Chief Financial Officer, and pursuant to his promotion letter (the “Lapointe Promotion Letter”), if the employment of
 Mr. Lapointe is terminated by SoFi without Cause (as defined in the Lapointe Promotion Letter) or he resigns for Good Reason (as defined in the Lapointe Promotion Letter), Mr. Lap
ointe shall be entitled to: (i) a lump-sum cash payment equal to the sum of (x) 12 months of Mr. Lapointe’s base salary, and (y) 100% of Mr. Lapointe’s annual cash bonus at the hig
her of (a) Mr. Lapointe’s target level and (b) Mr. Lapointe’s actual level of performance reasonably projected as of the termination of Mr. Lapointe’s employment, (ii) the continua
tion of health, dental and vision coverage under SoFi’s group insurance benefits at no cost to Mr. Lapointe for 12 months, and (iii) vesting acceleration of each of Mr. Lapointe’s 
then-outstanding RSUs as if he had remained in continuous service to SoFi for an additional 12 months. Additionally, pursuant to the Lapointe Promotion Letter, if the employment of
 Mr. Lapointe is terminated by SoFi without Cause or he resigns for Good Reason three months prior to or any time after a Change of Control (as defined in the Lapointe Promotion Le
tter), Mr. Lapointe shall, in lieu of the above, be entitled to: (i) a lump-sum cash payment equal to the sum of (x) 18 months of Mr. Lapointe’s base salary, and (y) 150% of Mr. La
pointe’s annual cash bonus at the higher of (a) his target level and (b) his actual level of performance reasonably projected as of the termination of Mr. Lapointe’s employment, (i
i) the continuation of health, dental and vision coverage under SoFi’s group insurance benefits at no cost to Mr. Lapointe for 18 months, and (iii) full vesting acceleration of eac
h of Mr. Lapointe’s then-outstanding RSUs. Additionally, all equity awards are subject to automatic accelerated vesting upon a Change of Control of SoFi, if such awards are otherwi
se to be canceled for no consideration upon such Change of Control. Mr. Lapointe’s severance payments and benefits are subject to the execution of a general release of claims in fa
vor of SoFi. The following table sets forth quantitative estimates of the payments and benefits that would have accrued to our NEOs pursuant to the Executive Severance Plan, employ
ment agreement or offer letters, as applicable, if their respective employment had been terminated under either a “Qualifying Termination” or a “Qualifying Termination with Change 
of Control”, as well as payments and benefits that would have accrued under solely a “Change of Control” as of December 31, 2024. Refer to the footnotes of the table for definition
s of these scenarios. 56 SoFi Technologies, Inc. Table of Contents Name Scenario Cash Severance Benefits ($) (1) Accelerated Vesting of Equity Awards ($) (2) Continued Health Benef
its ($) (3) Total ($) Anthony Noto Qualifying Termination (4) $ 3,585,000 $ 35,939,226 $ 39,897 $ 39,564,124 Qualifying Termination with Change of Control (5) 5,377,500 57,421,857 
59,846 62,859,202 Change of Control (6) — 57,421,857 — 57,421,857 Christopher Lapointe Qualifying Termination (4) 1,125,000 8,331,277 39,897 9,496,174 Qualifying Termination with C
hange of Control (5) 1,687,500 16,692,630 59,846 18,439,975 Change of Control (6) — 16,692,630 — 16,692,630 Arun Pinto Qualifying Termination (7) 1,000,000 — 39,897 1,039,897 Quali
fying Termination with Change of Control (8) 1,000,000 9,086,801 39,897 10,126,698 Eric Schuppenhauer Qualifying Termination (7) 1,000,000 — 39,897 1,039,897 Qualifying Termination
 with Change of Control (8) 1,000,000 13,732,088 39,897 14,771,985 Stephen Simcock Qualifying Termination (7) 1,000,000 — 13,053 1,013,053 Qualifying Termination with Change of Con
trol (8) 1,000,000 15,383,738 13,053 16,396,791 __________________ (1) Includes lump-sum base salary payments and non-equity incentive-based compensation payable to the NEO by SoFi
 as provided under the employment agreement or offer letters, as applicable. Additionally, in a Qualifying Termination, bonuses are determined to be the higher of the target or the
 actual level of performance reasonably projected at termination. (2) Includes the fair value of RSUs that would immediately vest pursuant to the specified termination scenario. Aw
ard fair values are determined based on the closing price of SOFI of $15.40 per share on December 31, 2024. The fair value of accelerated RSUs is calculated as $15.40, multiplied b
y the number of outstanding and unvested RSUs as of December 31, 2024. (3) Calculated as (i) the cost of health, dental and vision insurance premiums under COBRA applicable to each
 NEO, multiplied by (ii) the number of months of continued health benefits coverage as provided under the employment agreement or offer letters, as applicable. (4) A Qualifying Ter
mination is a termination of employment by SoFi without “cause” or a resignation for “good reason.” Cause typically includes certain violations causing material injury to the Compa
ny, such as fraud, dishonesty, unauthorized use or disclosure of proprietary information, other willful misconduct, or the like. Good reason typically includes the occurrence of ce
rtain conditions without written consent, such as 10% reduction in base salary, a material breach by the Company of any agreement between the Company and employee, and the like. (5
) A Qualifying Termination with Change of Control is a Qualifying Termination, as discussed in footnote (4) above, at any time after, or within three months prior to, a Change of C
ontrol. For Mr. Noto and Mr. Lapointe, “Change of Control” has the same meaning as the term is defined under the applicable stock option and incentive plan, with modifications that
 a Change of Control is triggered by consummation of a transaction in which any “person” becomes the “beneficial owner”, directly or indirectly, of a majority of SoFi’s then-outsta
nding voting securities, rather than all of the then-outstanding voting securities as prescribed in the applicable stock option and incentive plan. Additionally, the definition of 
Change of Control in Mr. Noto’s and Mr. Lapointe’s employment agreement, promotion letter and offer letter, as applicable, excludes certain transactions by a preferred series inves
tor. (6) “Change of Control” has the same meaning as the term is defined in the applicable stock option and incentive plan. The values reflected herein assume no termination has oc
curred in connection with such Change of Control. (7) A Qualifying Termination is a termination of employment by SoFi without “Cause.” “Cause” shall mean any of the following acts 
or omissions: (i) the Covered Executive’s willful failure to perform his or her duties and responsibilities to the Company or the Applicable Subsidiary, (ii) the commission by the 
Covered Executive of any act of fraud, embezzlement, material dishonesty or other misconduct that is detrimental to the Company, its affiliates or the Applicable Subsidiary or that
 otherwise has caused or would reasonably be expected to result in material injury or harm to the Company or its affiliates, (iii) the unauthorized use or disclosure by the Covered
 Executive of any proprietary information or trade secrets of the Company or any party to whom an obligation of nondisclosure is owed, (iv) a material breach by the Covered Executi
ve of any obligations under any written agreement or covenant with the Company, or (v) any act deemed to constitute “cause” under a written agreement with the Company or its affili
ates and the Covered Executive, in each case, whether or not such act or omission led to a termination of service and regardless of whether such act or omission was discovered prio
r to such termination of service. (8) A Qualifying Termination with Change of Control is a Qualifying Termination, as discussed in footnote (7) above, at any time upon, or within t
he twelve month period following, a Change of Control, as defined under the 2021 Plan, as amended. 57 SoFi Technologies, Inc. Table of Contents Estimated Ratio of CEO Compensation 
to Median Employee Compensation As required by Item 402(u) of Regulation S-K, we are providing the following information about the ratio of the annual total compensation, calculate
d in accordance with the requirements of Item 402(c)(2)(x) of Regulation S-K (“Annual Total Compensation”) of our median employee and the Annual Total Compensation of our CEO, Anth
ony Noto. The CEO pay ratio rules allow us to use the same median employee for comparison purposes for up to three years. For 2024, we used the same median employee who was identif
ied in 2023 since there has been no change in our employee population or employee compensation arrangements that we reasonably believe would result in a significant change in the p
ay ratio disclosure. For 2024, the Annual Total Compensation of our median employee was $91,520. The Annual Total Compensation of Mr. Noto was $28,072,183. Therefore, the ratio of 
Mr. Noto’s Annual Total Compensation to the median employee’s Annual Total Compensation was 307 to 1. The increase in our CEO pay ratio for 2024 is due to the return to a standard 
four-year vesting schedule and a corresponding increase in the size of his equity grant across that longer period. For 2023, the lower pay ratio was a result of a smaller grant siz
e across a shorter, three-year vesting period. Additionally, the pay ratio includes our CEO’s PSU grant which constitutes 25% of his equity compensation for 2024, even though this 
performance-based award will only vest if specific goals are achieved over a three-year period. This ratio is a reasonable estimate calculated in a manner consistent with Item 402(
u) of Regulation S-K. To identify our median employee, who is located in California, we used the following methodology: we had 4,412 total employees as of December 31, 2023 (the “D
etermination Date”), including full-time, part-time, seasonal and temporary workers, as appropriate, and excluding our CEO. We identified the median compensated employee as of the 
Determination Date by comparing a consistently applied compensation measure consisting of salary, wages (including overtime), bonuses and commissions paid to our employees over the
 twelve-month period ending on the Determination Date (the “Measurement Period”). For any employees hired during the Measurement Period, we annualized the non-equity based compensa
tion paid to the employees as if they had been active at the beginning of the Measurement Period. We then included the grant-date fair value of equity awards granted to our median 
employee over the Measurement Period. The SEC’s rules for identifying the median compensated employee and calculating the CEO pay ratio based on that employee’s Annual Total Compen
sation allow companies to adopt a variety of methodologies, to apply certain exclusions, and to make reasonable estimates and assumptions that reflect their employee populations an
d compensation practices. As a result, the CEO pay ratio reported by other companies may not be comparable to the CEO pay ratio reported above, as other companies have different em
ployee populations and compensation practices and may utilize different methodologies, exclusions, estimates, and assumptions in calculating their CEO pay ratios. 58 SoFi Technolog
ies, Inc. Table of Contents Pay Versus Performance Pay Versus Performance Table As required by Item 402(v) of Regulation S-K, we are providing the information below to illustrate t
he relationship between the compensation actually paid (“CAP”) to the Named Executive Officers and various measures used to gauge the Company’s financial performance. CAP is calcul
ated in accordance with Item 402(v) of Regulation S-K and differs from compensation disclosed in the “ 2024 Summary Compensation Table ” and the other compensation-related tables d
isclosed in this “ Executive Compensation. ” For further information concerning our compensation philosophy and how we align executive compensation with our performance, see the se
ction entitled “ Compensation Discussion and Analysis. ” Value of Initial Fixed $100 Invested Based on: Performance Year Summary Compensation Table Total for Principal Executive Of
ficer (1) Compensation Actually Paid to Principal Executive Officer (1) Average Summary Compensation Table Total for Non-PEO Named Executive Officers (1) Average Compensation Actua
lly Paid to Non-PEO Named Executive Officers (1) Total Shareholder Return (2) Peer Group Total Shareholder Return (2) Net Income (Loss) ($ in thousands) Company-Selected Measure —A
djusted Net Revenue ($ in thousands) 2024 $ 28,072,183 $ 64,579,825 $ 7,423,306 $ 15,505,155 67.99 144.52 $ 498,665 $ 2,606,170 2023 18,263,886 71,327,408 5,314,098 13,499,433 43.9
3 111.54 ( 300,742 ) 2,073,940 2022 12,893,293 ( 121,490,627 ) 10,363,699 ( 25,896,259 ) 20.35 77.11 ( 320,407 ) 1,540,492 2021 102,998,110 119,107,305 19,026,864 20,461,726 70.42 
114.30 ( 483,937 ) 1,010,325 2020 53,533,739 92,386,353 11,039,231 17,084,857 n/a n/a ( 224,053 ) 621,207 __________________ (1) Mr. Noto is represented as the principal executive 
officer (“PEO”) for each of the performance years presented. For the 2024 performance year, the non-PEO named executive officers (“non-PEO NEOs”) include Messrs. Lapointe, Pinto, S
chuppenhauer, and Simcock. For the 2023 performance year, the non-PEO NEOs include Mr. Lapointe, Chad Borton, Derek White, and Aaron Webster. For the 2022 performance year, the non
-PEO NEOs include Messrs. Lapointe, Borton, and Webster, Jeremy Rishel, and Michelle Gill. For the 2021 performance year, the non-PEO NEOs include Messrs. Lapointe and White, and M
s. Gill and Jennifer Nuckles. For the 2020 performance year, the non-PEO NEOs include Mr. Lapointe and Mses. Gill and Nuckles, and Maria Renz. (2) Total Shareholder Return (“TSR”) 
is cumulative for the measurement periods beginning on June 1, 2021 (the date our Common Stock commenced trading on Nasdaq) and ending on the last day in 2024, 2023, 2022 and 2021,
 calculated in accordance with Item 201(e) of Regulation S-K. “Peer Group” represents the Nasdaq Composite index for the years disclosed in the table. No information is provided fo
r 2020, as Social Finance common stock was not publicly traded. Our NEOs’ annual target total direct compensation is heavily weighted towards short and long-term performance. The m
ajority of our NEOs’ annual target total direct compensation is both variable in nature and “at-risk.” Adjusted net revenue is one of the primary measures in our performance-based 
Annual Cash Bonus Plan. Our long-term incentives are time-based RSUs, in addition to PSUs that we grant from time to time. The compensation actually paid to our NEOs largely reflec
ts the volatility in the Company’s stock price over the period of time covered in the table. 59 SoFi Technologies, Inc. Table of Contents Reconciliation of Summary Compensation Tab
le Total to Compensation Actually Paid The Compensation Committee does not utilize CAP as the basis for making compensation decisions. The calculation of CAP requires that we make 
adjustments to amounts previously reported in the Summary Compensation Table for the years presented. The SEC’s valuation and calculation methods for CAP differ from those required
 in the Summary Compensation Table. The table below summarizes compensation values presented in the Summary Compensation Table and the adjusted values required to reconcile these v
alues to the CAP presented above. The amounts shown below for non-PEO NEOs for each year represents an average of all non-PEO NEOs. CAP to the PEO and non-PEO NEOs represents Summa
ry Compensation Table total compensation adjusted by the following amounts: Reconciliation of Summary Compensation Table Total to Compensation Actually Paid (1) Summary Compensatio
n Table Total Summary Compensation Table Total (2) Plus Fair Value of Equity Awards Granted in Covered Year and Unvested at Year End Change in Fair Value of Equity Awards Granted i
n Prior Years and Unvested at Year End Plus Fair Value of Equity Awards Granted and Vested in Covered Year Less Fair Value of Equity Awards Reported in the Summary Compensation Tab
le in the Covered Year Change in Fair Value of Equity Awards Granted in Prior Years and Vested in Covered Year Less Fair Value of Equity Awards Granted in Prior Years and Forfeited
 in Covered Year (3) Compensation Actually Paid (4) 2024 - PEO $ 28,072,183 $ 40,688,124 $ 17,102,610 $ 4,192,528 $ ( 24,132,183 ) $ ( 1,343,437 ) $ — $ 64,579,825 2024 - non-PEO N
EOs 7,423,306 12,200,973 1,285,577 1,291,223 ( 6,603,620 ) ( 92,304 ) — 15,505,155 2023 - PEO 18,263,886 15,177,352 38,174,780 4,789,636 ( 14,196,036 ) 9,117,790 — 71,327,408 2023 
- non-PEO NEOs 5,314,098 4,320,061 5,182,666 1,363,314 ( 4,168,098 ) 1,487,392 — 13,499,433 2022 – PEO 12,893,293 4,684,963 ( 99,602,444 ) — ( 9,400,414 ) ( 30,066,025 ) — ( 121,49
0,627 ) 2022 – non-PEO NEOs 10,363,699 6,032,115 ( 11,117,288 ) 927,430 ( 9,026,274 ) ( 3,934,694 ) ( 19,141,247 ) ( 25,896,259 ) 2021 – PEO 102,998,110 46,631,650 45,712,042 — ( 1
01,187,079 ) 24,952,582 — 119,107,305 2021 – non-PEO NEOs 19,026,864 13,477,008 831,998 2,002,816 ( 17,674,364 ) 2,797,404 — 20,461,726 2020 – PEO 53,533,739 56,968,264 27,737,216 
2,406,701 ( 52,118,397 ) 3,858,830 — 92,386,353 2020 – non-PEO NEOs 11,039,231 13,250,711 1,257,859 1,297,375 ( 10,017,783 ) 257,464 — 17,084,857 __________________ (1) Fair values
 are calculated in accordance with ASC 718 as of the end of the respective year, other than awards that vest in the covered year, which are valued as of the applicable vesting date
s. (2) Reflects the total compensation amount for the PEO and average total compensation amount for the non-PEO NEOs as reported in the Summary Compensation Table for each year pre
sented. (3) Reflects awards that failed to meet vesting conditions during the covered year. (4) Reflects the actual CAP for the PEO and average CAP for the non-PEO NEOs. 60 SoFi Te
chnologies, Inc. Table of Contents Relationship Between CAP and Net Income (Loss) The following graph compares the CAP to our PEO, the average of the CAP to our non-PEO NEOs and th
e Company’s net income (loss). Relationship Between CAP and Adjusted Net Revenue The following graph compares the CAP to our PEO, the average of the CAP to our non-PEO NEOs and the
 Company’s adjusted net revenue. 61 SoFi Technologies, Inc. Table of Contents Relationship Between CAP and Total Shareholder Return The following graph compares the CAP to our PEO,
 the average of the CAP to our non-PEO NEOs and TSR for the Company and the Nasdaq Composite Index, which is cumulative based on the performance of a $100 investment from June 1, 2
021 (the date our Common Stock commenced trading on Nasdaq) to December 31, 2024. The graph below shows a connection between compensation actually paid and TSR. Tabular List of Per
formance Measures In accordance with Item 402(v) of Regulation S-K, the following are the performance measures, both financial and nonfinancial in nature, that the Company has dete
rmined to represent the most important performance measures used to link CAP (for both the PEO and the non-PEO NEOs) for the most recent year to Company performance: Most Important
 Performance Measures Adjusted Net Revenue (Company Selected Measure) Adjusted EBITDA New Members Absolute Growth in Tangible Book Value Return on Tangible Equity Adjusted net reve
nue (financial performance measure and Company-selected measure) Adjusted net revenue is a non-GAAP measure. Adjusted net revenue is defined as total net revenue, adjusted to exclu
de the fair value changes in servicing rights and residual interests classified as debt due to valuation inputs and assumptions changes, which relate only to our Lending segment, a
s well as gains and losses on extinguishment of debt. We adjust total net revenue to exclude these items, as they are non-cash charges that are not realized during the period or no
t indicative of our core operating performance, and therefore positive or negative changes do not impact the cash available to fund our operations. Management believes this measure
 is useful because it enables management and investors to assess our underlying operating performance and cash available to fund our operations. In addition, management uses this m
easure to better decide on the proper expenses to authorize for each of our operating segments, to ultimately help achieve target contribution profit margins. 62 SoFi Technologies,
 Inc. Table of Contents Refer to Appendix A for an additional discussion of adjusted net revenue, as well as a reconciliation to the most directly comparable GAAP measure. Adjusted
 EBITDA (financial performance measure) Adjusted EBITDA is a non-GAAP measure. Adjusted EBITDA is defined as net income (loss), adjusted to exclude, as applicable: (i) corporate bo
rrowing-based interest expense (our adjusted EBITDA measure is not adjusted for warehouse or securitization-based interest expense, nor deposit interest expense and finance lease l
iability interest expense, as these are direct operating expenses), (ii) income tax expense (benefit), (iii) depreciation and amortization, (iv) share-based expense (inclusive of e
quity-based payments to non-employees), (v) restructuring charges, (vi) impairment expense (inclusive of goodwill impairment and property, equipment and software abandonments), (vi
i) transaction-related expenses, (viii) foreign currency impacts related to operations in highly inflationary countries, (ix) fair value changes in each of servicing rights and res
idual interests classified as debt due to valuation assumptions, (x) gain on extinguishment of debt, and (xi) other charges, as appropriate, that are not expected to recur and are 
not indicative of our core operating performance. Management believes adjusted EBITDA is a useful measure for period-over-period comparisons of our business. This measure enables m
anagement and investors to assess our core operating performance or results of operations by removing the effects of certain non-cash items and charges, as well as the impact of ch
anges in volume over periods as applicable. In addition, management uses this measure to help evaluate cash flows generated from operations and the extent of additional capital, if
 any, required to invest in strategic initiatives. Refer to Appendix A for an additional discussion of adjusted EBITDA, as well as a reconciliation to the most directly comparable 
GAAP measure. New Members (non-financial performance measure) We refer to our customers as “members”. We define a member as someone who has a lending relationship with us through o
rigination and/or ongoing servicing, opened a financial services account, linked an external account to our platform or signed up for our credit score monitoring service. Our membe
rs have access to our CFPs, our member events, our content, educational material, news, and our tools and calculators, which are provided at no cost to the member. Beginning in the
 first quarter of 2024, we aligned our methodology for calculating member and product metrics with our member and product definitions to include co-borrowers, co-signers, and joint
- and co-account holders, as applicable. Quarterly amounts for prior periods were determined to be immaterial and were not recast. Once someone becomes a member, they are always co
nsidered a member unless they are removed in accordance with our terms of service, in which case, we adjust our total number of members. This could occur for a variety of reasons—i
ncluding fraud or pursuant to certain legal processes—and, as our terms of service evolve together with our business practices, product offerings and applicable regulations, our gr
ounds for removing members from our total member count could change. The determination that a member should be removed in accordance with our terms of service is subject to an eval
uation process, following the completion, and based on the results, of which, relevant members and their associated products are removed from our total member count in the period i
n which such evaluation process concludes. However, depending on the length of the evaluation process, that removal may not take place in the same period in which the member was ad
ded to our member count or the same period in which the circumstances leading to their removal occurred. For this reason, our total member count may not yet reflect adjustments tha
t may be made once ongoing evaluation processes, if any, conclude. “New member” metrics for the relevant period reflect actual growth or declines in members and products that occur
red in that period whereas the total number of members and products reflects not only the growth or decline of each metric in the current period but also additions or deletions due
 to prior period factors, if any. Absolute Growth in Tangible Book Value (financial performance measure) Absolute Growth in Tangible Book Value means the growth of the Company’s Ta
ngible Book Value, defined as the dollar amount representing the Company’s aggregate assets less the Company’s aggregate liabilities as set forth in the Company’s most recent audit
ed financial statements, measured over the Measurement Period, as defined in the individual award agreement, excluding the effects of any capital raises, acquisitions, intangible v
alue and goodwill. 63 SoFi Technologies, Inc. Table of Contents Return on Tangible Equity (financial performance measure) Return on tangible equity is defined as the Company’s net 
income (loss), adjusted to exclude certain items that are not expected to recur and are not indicative of our core operating performance, divided by average stockholders equity, ad
justed to exclude the effects of capital raises, intangible value, and goodwill. 64 SoFi Technologies, Inc. Table of Contents BENEFICIAL OWNERSHIP OF SECURITIES The following table
 sets forth information regarding the beneficial ownership of our voting shares by: • each person who is known to be the beneficial owner of more than 5% of our voting shares; • ea
ch of our named executive officers and directors; and • all of our executive officers and directors as a group. Beneficial ownership is determined according to the rules of the SEC
, which generally provide that a person has beneficial ownership of a security if he, she, they or it possesses sole or shared voting or investment power over that security, includ
ing options, RSUs and warrants that are currently exercisable or exercisable within 60 days of March 31, 2025. Percentage ownership of our voting securities is based on 1,104,104,2
03 shares of our Common Stock issued and outstanding as of the close of business on March 31, 2025. Unless otherwise indicated, we believe that all persons named in the table below
 have sole voting and investment power with respect to the voting securities beneficially owned by them. Name and Address of Beneficial Owner (1) Number of Shares % of Ownership 5%
 Holders The Vanguard Group (2) 81,459,501 7.4 % Directors and Named Executive Officers Anthony Noto (3) 21,501,778 1.9 % Christopher Lapointe (4) 1,372,576 * Arun Pinto (5) 156,48
2 * Eric Schuppenhauer (6) 181,930 * Stephen Simcock (7) 124,260 * Tom Hutton (8) 1,030,299 * Steven Freiberg (9) 979,924 * Ruzwana Bashir (10) 60,971 * William Borden (11) 35,034 
* Dana Green — * John Hele (12) 35,034 * Clara Liang (13) 401,760 * Gary Meltzer (14) 44,921 * Magdalena Yesil (15) 1,191,958 * All directors and current executive officers as a gr
oup (17 individuals) 28,905,000 2.6 % __________________ * Less than one percent (1) Unless otherwise noted, the business address of each of those listed in the table above is 234 
1st Street, San Francisco, CA 94105. (2) The address of The Vanguard Group is 100 Vanguard Blvd, Malvern, Pennsylvania 19355. The Vanguard Group has shared voting power over 325,21
7 shares of Common Stock, sole dispositive power over 80,145,625 shares of Common Stock and shared dispositive power over 1,313,876 shares of Common Stock. This information is base
d on a Schedule 13G/A filed with the SEC on February 13, 2024. (3) Includes 11,676,760 shares of Common Stock issuable upon the exercise of options exercisable as of March 31, 2025
 and 33,259 shares held of record by Kristin Noto, Mr. Noto’s spouse. (4) Consists of shares held of record by Mr. Lapointe. (5) Includes 45,388 shares of Common Stock issuable upo
n vesting of RSUs within 60 days of March 31, 2025 (6) Includes 55,730 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025. (7) Consists of shares
 held of record by Mr. Simcock. (8) Includes 211,361 shares of Common Stock issuable upon the exercise of options exercisable as of March 31, 2025 and 210,589 shares of Common Stoc
k held in a living trust directed by Mr. Hutton. 65 SoFi Technologies, Inc. Table of Contents (9) Includes 546,850 shares of Common Stock issuable upon the exercise of options exer
cisable as of March 31, 2025 and 44,844 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025. (10) Consists of shares held of record by Ms. Bashir 
and 35,034 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025. (11) Includes 35,034 shares of Common Stock issuable upon vesting of RSUs within 6
0 days of March 31, 2025. (12) Includes 35,034 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025. (13) Includes 304,503 shares of Common Stock i
ssuable upon the exercise of options exercisable as of March 31, 2025 and 35,034 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025. (14) Include
s 44,921 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025. (15) Includes (i) 313,704 shares of Common Stock issuable upon the exercise of optio
ns exercisable as of March 31, 2025 and 35,034 shares of Common Stock issuable upon vesting of RSUs within 60 days of March 31, 2025, (ii) 379,682 shares held of record by Ms. Yesi
l, (iii) 144,629 shares held of record by the Troy Kevork Wickett Trust, of which Ms. Yesil is a trustee, (iv) 144,629 shares held of record by the Justin Yesil Wickett Trust, of w
hich Ms. Yesil is a trustee, and (v) 174,280 shares held of record by James F. Wickett, Ms. Yesil’s spouse. 66 SoFi Technologies, Inc. Table of Contents CERTAIN RELATIONSHIPS AND R
ELATED PERSON TRANSACTIONS In addition to the compensation arrangements with directors and executive officers described under “ Executive Compensation ” and “ Management ” and the 
registration rights described elsewhere in this Proxy Statement, the following is a description of each transaction since January 1, 2024 and each currently proposed transaction in
 which: • we have been or are to be a participant; • the amount involved exceeds or will exceed $120,000; and • any of our directors, executive officers or beneficial holders of mo
re than 5% of our capital stock, or any immediate family member of, or person sharing the household with, any of these individuals (other than tenants or employees), had or will ha
ve a direct or indirect material interest. We also describe below certain other transactions and relationships with our directors, executive officers and stockholders. Shareholders
’ Agreement We, the Sponsor and certain former shareholders of Social Finance (the “SoFi Holders”) entered into the Shareholders’ Agreement. The SoFi Holders included entities affi
liated with SoftBank Group Corp. (“SoftBank”) and Red Crow Capital, LLC (“Red Crow”), entities affiliated with Michael Bingle, one of our directors until his resignation in January
 2025, and an entity affiliated with Mr. Al-Hammadi, one of our directors until his resignation in November 2024. Pursuant to the Shareholders’ Agreement, we also entered into the 
Share Repurchase Agreement with SoftBank Group Capital Limited (the “Share Repurchase Agreement”) committing us to repurchase, in the aggregate, $150 million of shares of Common St
ock owned by SoftBank investors at a price per share equal to $10.00. Following such repurchase, in the event the combined ownership of shares of Common Stock by the SoftBank inves
tors and Renren SF Holdings Inc., or their affiliates, exceeded a specified regulatory ownership threshold, the SoftBank investors would convert a number of shares of Common Stock 
into non-voting Common Stock such that, the combined ownership of the SoftBank investors, Renren SF Holdings Inc. and their affiliates would not exceed such threshold. The Sharehol
ders’ Agreement further set forth ongoing rights to designate seats on the Board of Directors that entitled (i) SCH Sponsor to nominate up to two (2) independent directors, (ii) th
e SoftBank investors to nominate up to two (2) directors, (iii) the Silver Lake investors to nominate one (1) director, (iv) the QIA investors to nominate one (1) director, and (v)
 the Red Crow investors to nominate one (1) director, in each case so long as such entity or its affiliates owned a certain percentage of our Common Stock. Certain of these entitie
s were also entitled to certain designation rights with respect to committees of our Board of Directors. In April 2021, the SoftBank investors and Red Crow investors waived their r
ights to designate seats on the Board of Directors. In December 2021, as a result of a series of transactions pursuant to which SCH Sponsor’s ownership interest in the Company was 
reduced to below the ownership threshold, both of SCH Sponsor’s designation rights terminated. Pursuant to the Shareholders’ Agreement, if, as of the Closing, we maintained an amou
nt of available cash that exceeded a certain minimum threshold, and our Board of Directors approved the repurchase of our Common Stock, then until the earlier of 180 days following
 the Closing and such time as the amount of such repurchases equals $250 million, we were required to offer the SoFi Holders the right to sell to us shares of our Common Stock owne
d by the SoFi Holders at a price per share equal to $10.00, subject to certain prioritization between such stockholders, and in each case on the terms, and subject to the condition
s, set forth in the Shareholders’ Agreement. As of the date of this Proxy Statement, the Shareholders’ Agreement has been terminated. Series 1 Registration Rights Agreement At the 
Closing, we and holders of Series 1 preferred stock entered into the Series 1 Registration Rights Agreement, pursuant to which we agreed to register for resale, pursuant to Rule 41
5 under the Securities Act, the Series 1 preferred stock and any other of our equity securities or securities of our subsidiaries issued or issuable with respect to shares of Serie
s 1 preferred stock. The Series 1 Registration Rights Agreement provided for certain customary piggyback registration rights. The Series 1 Registration Rights Agreement terminated 
on May 29, 2024, the date that all outstanding Series 1 preferred stock was redeemed. The holders of Series 1 Preferred included certain parties related to us, including Mr. Noto, 
and entities affiliated with Michael Bingle and Ahmed Al-Hammadi, two of our directors who have since resigned. 67 SoFi Technologies, Inc. Table of Contents Amended and Restated Re
gistration Rights Agreement At the Closing, we, the Sponsor, certain affiliates of the SCH Sponsor and certain SoFi stockholders entered into an Amended and Restated Registration R
ights Agreement, pursuant to which we agree to register for resale, pursuant to Rule 415 under the Securities Act, certain shares of our Common Stock and other of our equity securi
ties that are held by the parties thereto from time to time. The Amended and Restated Registration Rights Agreement amended and restated the registration rights agreement that was 
entered into by SCH, the SCH Sponsor and the other parties thereto in connection with the SCH initial public offering. The Amended and Restated Registration Rights Agreement also p
rovides for certain customary piggyback registration rights. The Amended and Restated Registration Rights Agreement will terminate on the date that no party holds any Registrable S
ecurities (as defined therein). The SoFi stockholders party to the agreement include parties related to us, including entities affiliated with SoftBank and Red Crow, entities affil
iated with Michael Bingle and Ahmed Al-Hammadi, two of our directors who have since resigned, Jay Parikh and Jennifer Dulski, former directors of SCH, certain entities affiliated w
ith Chamath Palihapitiya, the former Chairman of the Board of Directors of SCH and certain entities affiliated with Ian Osborne, the former President and a former director of SCH. 
Amended and Restated Series H Warrants On May 29, 2019, in connection with issuances of Social Finance Series H preferred stock and Social Finance Series 1 preferred stock, Social 
Finance issued 12,170,990 Series H Warrants to parties related to us, including QIA FIG Holding LLC, entities affiliated with Silver Lake, and Anthony Noto. On May 28, 2021, in con
nection with the Business Combination, we entered into an amended and restated warrant with each holder of Series H Warrants, which warrants superseded the outstanding warrants to 
purchase shares of Social Finance Series H preferred stock, and pursuant to which each holder had the right to purchase a number of shares of our Common Stock set forth therein. Th
e Series H Warrants expired in May 2024. Compensation Arrangements See “ Executive Compensation ” and “ Corporate Governance — Non-Employee Director Compensation ” for information 
regarding compensation arrangements with the executive officers and directors of SoFi, which include, among other things, employment, termination of employment and change of contro
l arrangements, stock awards and certain other benefits. Additionally, Marisa Noto, the daughter of our Chief Executive Officer, Mr. Noto, currently serves as Senior Director, Corp
orate Development of the Company. During the year ended December 31, 2024, she received total compensation of greater than $120,000, which is at a level consistent with that provid
ed to employees in comparable positions and tenure. Director and Officer Indemnification Our Certificate of Incorporation and Bylaws provide for indemnification for our directors a
nd officers to the fullest extent permitted by applicable law. We have entered into indemnification agreements with each of our directors and executive officers. For additional inf
ormation, see “ Corporate Governance — Limitations of Liability and Indemnification Matters. ” Pre-Business Combination Related Party Transactions of Social Finance In connection w
ith the execution of the Merger Agreement in January 2021, SCH and holders of the Series 1 redeemable preferred stock, including Anthony Noto, entered into the Amended and Restated
 Series 1 Preferred Stock Investors’ Agreement (the “Series 1 Agreement”). The Series 1 Agreement amends and restates in its entirety the original Series 1 Preferred Stock Investor
s’ Agreement (the “Original Series 1 Agreement”) and assigns all of Social Finance’s rights, remedies, obligations and liabilities under the Original Series 1 Agreement to SoFi. Th
e Series 1 Agreement contains financial and other covenants, provided for certain information rights and provided for the cash payment of $21.2 million to the holders of the Series
 1 redeemable preferred stock, immediately upon the Closing, in full satisfaction of the special payment rights set forth in the Original Series 1 Agreement, which was subject to a
djustment in accordance with the Merger Agreement. The Series 1 Agreement further provides that if the holders of a majority of the outstanding shares of Series 1 redeemable prefer
red stock are entitled to appoint a director designated by QIA FIG Holding LLC to our Board of Directors, as provided in our Certificate of Incorporation, then each holder of Serie
s 1 redeemable preferred stock shall vote such 68 SoFi Technologies, Inc. Table of Contents number of shares of Series 1 redeemable preferred stock as is necessary to ensure that t
he person designated by QIA FIG Holding LLC is so elected. As of the date of this Proxy Statement, the Series 1 Agreement has been terminated. Policies and Procedures for Related P
arty Transactions Our Nominating and Corporate Governance Committee has the responsibility for reviewing and approving or disapproving “related party transactions.” We adopted a wr
itten policy following the Closing for the review and approval of related party transactions that sets forth the following policies and procedures for the review and approval or ra
tification of related party transactions. A related party transaction means any transaction, arrangement or relationship in which the Company or any of its subsidiaries is a party,
 the amount involved exceeds $120,000 and any related party has or will have a direct or indirect material interest (other than solely as a result of being a director, officer or a
 less than 10 percent beneficial owner of another entity). Our Policy on Related Party Transactions provides, among other things: • The Nominating and Corporate Governance Committe
e reviews the material facts of all proposed related party transactions. • In reviewing any proposed related party transaction, the Nominating and Corporate Governance Committee ta
kes into account, among other factors that it deems appropriate, whether the related party transaction is on terms no less favorable to us than terms generally available in a trans
action with an unaffiliated third-party under the same or similar circumstances and the extent of the related party’s interest in the transaction. • In connection with its review o
f any proposed related party transaction, we will provide the Nominating and Corporate Governance Committee with all material information regarding such related party transaction, 
the interest of the related party and any potential disclosure obligations we have in connection with such related party transaction. If a related party transaction will be ongoing
, the Nominating and Corporate Governance Committee may establish guidelines for our management to follow in its ongoing dealings with the related party. 69 SoFi Technologies, Inc.
 Table of Contents AUDIT COMMITTEE REPORT Management is responsible for the Company’s internal controls, financial reporting process and compliance with laws, regulations and ethic
al business standards. The Company’s independent registered public accounting firm, Deloitte & Touche LLP, is responsible for performing an independent audit of the Company’s conso
lidated financial statements in accordance with the standards of the Public Company Accounting Oversight Board (United States) (“PCAOB”) and issuing a report thereon. The Audit Com
mittee\'s responsibility is to monitor and oversee these processes and to report its findings to our Board of Directors. The Audit Committee members are not professional accountant
s and their functions are not intended to duplicate or to certify the activities of management or Deloitte & Touche LLP, nor can the Audit Committee certify that Deloitte & Touche 
LLP is “independent” under applicable rules. The Audit Committee serves a board-level oversight role and provides advice, counsel and direction to management on the basis of the in
formation it receives, discussions with management and Deloitte & Touche LLP and the experience of its members in business, financial and accounting matters. In this context, the A
udit Committee reviewed and discussed the audited financial statements for the year ended December 31, 2024 with Company management. Management represented to the Audit Committee t
hat the Company’s audited consolidated financial statements were prepared in accordance with U.S. generally accepted accounting principles (“GAAP”). The Audit Committee has discuss
ed with Deloitte & Touche LLP the matters required to be discussed by the applicable requirements of the PCAOB and the SEC. Deloitte & Touche LLP also provided to the Audit Committ
ee the written disclosures and letter required by applicable requirements of the PCAOB regarding its independence, and the Audit Committee discussed with Deloitte & Touche LLP its 
independence. Based upon the Audit Committee’s discussions with management and Deloitte & Touche LLP and the Audit Committee’s review of the representation of management and the re
port of Deloitte & Touche LLP to the Audit Committee, the Audit Committee recommended that our Board of Directors include the audited consolidated financial statements in the Compa
ny’s Annual Report on Form 10-K for the year ended December 31, 2024 for filing with the SEC. Submitted by the Audit Committee of the Board of Directors: Gary Meltzer (Chair) Steve
n Freiberg Tom Hutton Clara Liang The material in this report is not “soliciting material,” is not deemed “filed” with the SEC and is not to be incorporated by reference in any fil
ing of SoFi under the Securities Act or the Exchange Act, whether made before or after the date hereof and irrespective of any general incorporation language in any such filing. 70
 SoFi Technologies, Inc. Table of Contents OTHER MATTERS 2024 Annual Report and SEC Filings Our financial statements for the year ended December 31, 2024 are included in our Annual
 Report on Form 10-K. Our Annual Report and this Proxy Statement are posted on our website at https://investors.sofi.com and are available from the SEC at its website at www.sec.go
v. You may also obtain a copy of our Annual Report without charge by sending a written request to Investor Relations, SoFi Technologies, Inc., 234 1st Street, San Francisco, Califo
rnia 94105. Stockholder Communications We provide an informal process for stockholders to send communications to our Board of Directors and its members. We make an effort to ensure
 that the views of stockholders are heard by our Board of Directors or individual directors, as applicable. Stockholders who wish to contact our Board of Directors or any of its me
mbers may do so by writing to ir@sofi.org. Our investor relations team, in consultation with our General Counsel or an Associate General Counsel, will review all incoming stockhold
er communications and, if appropriate, will route such communications to the appropriate director(s) or, if none is specified, to our Chief Executive Officer. Communications deemed
 inappropriate will not be forwarded, including, but not limited to, solicitations, advertisements, surveys, mass mailings or communications consisting of individual grievances or 
other interests that are personal to the writer and could not be reasonably construed to be of concern to stockholders or other constituencies of the Company. Delinquent Section 16
(a) Reports Section 16(a) of the Exchange Act requires our directors and certain officers, as well as persons who own more than 10 percent of our Common Stock, to file with the SEC
 initial reports of beneficial ownership on Form 3 and reports of subsequent changes in beneficial ownership on Form 4 or Form 5. Based solely on our review of these forms filed wi
th the SEC, and certifications from our executive officers and directors that no other reports were required for such persons, we believe that all directors and officers and greate
r than 10 percent shareholders complied with the filing requirements applicable to them for the year ended December 31, 2024 in a timely manner; except that one report on Form 4, c
overing one equity grant vest transaction, was filed late on behalf of Arun Pinto, and two reports on Form 4, covering an aggregate of two equity grant-related transactions, were f
iled late on behalf of Steven Freiberg. 71 SoFi Technologies, Inc. Table of Contents APPENDIX A Non-GAAP Financial Measures Our management and Board of Directors use non-GAAP measu
res to evaluate our operating performance, formulate business plans, help better assess our overall liquidity position, and make strategic decisions, including those relating to op
erating expenses and the allocation of internal resources. Accordingly, we believe that these non-GAAP measures provide useful information to investors and others in understanding 
and evaluating our operating results in the same manner as our management and Board of Directors. These non-GAAP measures have limitations as analytical tools, and should not be co
nsidered in isolation from, or as a substitute for, the analysis of other GAAP financial measures. Other companies may not use these non-GAAP measures or may use similar measures t
hat are defined in a different manner. Therefore, our non-GAAP measures may not be directly comparable to similarly titled measures of other companies. Adjusted Net Revenue Adjuste
d net revenue is a non-GAAP measure. Adjusted net revenue is defined as total net revenue, adjusted to exclude the fair value changes in servicing rights and residual interests cla
ssified as debt due to valuation inputs and assumptions changes, which relate only to our Lending segment, as well as gains and losses on extinguishment of debt. We adjust total ne
t revenue to exclude these items, as they are non-cash charges that are not realized during the period or not indicative of our core operating performance, and therefore positive o
r negative changes do not impact the cash available to fund our operations. Management believes this measure is useful because it enables management and investors to assess our und
erlying operating performance and cash available to fund our operations. In addition, management uses this measure to better decide on the proper expenses to authorize for each of 
our operating segments, to ultimately help achieve target contribution profit margins. The following table reconciles adjusted net revenue to total net revenue, the most directly c
omparable GAAP measure: Year Ended December 31, ($ in thousands) 2024 2023 2022 Total net revenue (GAAP) $ 2,674,859 $ 2,122,789 $ 1,573,535 Servicing rights – change in valuation 
inputs or assumptions (1) (6,280) (34,700) (39,651) Residual interests classified as debt – change in valuation inputs or assumptions (2) 108 425 6,608 Gain on extinguishment of de
bt (3) (62,517) (14,574) — Adjusted net revenue (non-GAAP) $ 2,606,170 $ 2,073,940 $ 1,540,492 __________________ (1) Reflects changes in fair value inputs and assumptions on servi
cing rights, including conditional prepayment, default rates and discount rates. These assumptions are highly sensitive to market interest rate changes and are not indicative of ou
r performance or results of operations. Moreover, these non-cash charges are unrealized during the period and, therefore, have no impact on our cash flows from operations. (2) Refl
ects changes in fair value inputs and assumptions on residual interests classified as debt, including conditional prepayment, default rates and discount rates. When third parties f
inance our consolidated securitization VIEs by purchasing residual interests, we receive proceeds at the time of the closing of the securitization and, thereafter, pass along contr
actual cash flows to the residual interest owner. These residual debt obligations are measured at fair value on a recurring basis, but they have no impact on our initial financing 
proceeds, our future obligations to the residual interest owner (because future residual interest claims are limited to contractual securitization collateral cash flows), or the ge
neral operations of our business. (3) Reflects gain on extinguishment of debt. Gains and losses are recognized during the period of extinguishment for the difference between the ne
t carrying amount of debt extinguished and the fair value of equity securities issued. Adjusted EBITDA Adjusted EBITDA is a non-GAAP measure. Adjusted EBITDA is defined as net inco
me (loss), adjusted to exclude, as applicable: (i) corporate borrowing-based interest expense (our adjusted EBITDA measure is not adjusted for warehouse or securitization-based int
erest expense, nor deposit interest expense and finance lease liability interest expense, as these are direct operating expenses), (ii) income tax expense (benefit), (iii) deprecia
tion and amortization, (iv) share-based expense (inclusive of equity-based payments to non-employees), (v) restructuring charges, (vi) impairment expense (inclusive of goodwill imp
airment and property, equipment and software abandonments), (vii) transaction-related expenses, (viii) foreign currency impacts related to operations in highly inflationary countri
es, (ix) fair value changes in each of servicing rights and A-1 SoFi Technologies, Inc. Table of Contents residual interests classified as debt due to valuation assumptions, (x) ga
in on extinguishment of debt, and (xi) other charges, as appropriate, that are not expected to recur and are not indicative of our core operating performance. Management believes a
djusted EBITDA is a useful measure for period-over-period comparisons of our business. This measure enables management and investors to assess our core operating performance or res
ults of operations by removing the effects of certain non-cash items and charges, as well as the impact of changes in volume over periods as applicable. In addition, management use
s this measure to help evaluate cash flows generated from operations and the extent of additional capital, if any, required to invest in strategic initiatives. The following table 
reconciles adjusted EBITDA to net income (loss), the most directly comparable GAAP measure: Year Ended December 31, ($ in thousands) 2024 2023 2022 Net income (loss) (GAAP) $ 498,6
65 $ (300,742) $ (320,407) Non-GAAP adjustments: Interest expense – corporate borrowings (1) 48,346 36,833 18,438 Income tax (benefit) expense (2) (265,320) (416) 1,686 Depreciatio
n and amortization (3) 203,498 201,416 151,360 Share-based expense 246,152 271,216 305,994 Restructuring charges (4) 1,530 12,749 — Impairment expense (5) — 248,417 — Foreign curre
ncy impact of highly inflationary subsidiaries (6) 1,683 10,971 — Transaction-related expense (7) 615 142 19,318 Servicing rights – change in valuation inputs or assumptions (8) (6
,280) (34,700) (39,651) Residual interests classified as debt – change in valuation inputs or assumptions (9) 108 425 6,608 Gain on extinguishment of debt (10) (62,517) (14,574) — 
Total adjustments 167,815 732,479 463,753 Adjusted EBITDA (non-GAAP) $ 666,480 $ 431,737 $ 143,346 ___________________ (1) Our adjusted EBITDA measure adjusts for corporate borrowi
ng-based interest expense, as these expenses are a function of our capital structure. Corporate borrowing-based interest expense includes interest on our revolving credit facility,
 as well as interest expense and the amortization of debt discount and debt issuance costs on our convertible notes. Revolving credit facility interest expense in 2024 and 2023 inc
reased due to elevated average interest rates relative to the prior year on identical outstanding debt. Convertible note interest expense in 2024 increased related to the issuance 
of interest-bearing convertible senior notes during the first quarter of 2024. (2) Our income tax position in 2024 was primarily due to the release in the fourth quarter of a $258 
million valuation allowance against certain deferred tax assets based on our reassessment of their realizability. Income taxes in 2023 were primarily attributable to income tax ben
efits from foreign losses in jurisdictions with net deferred tax liabilities related to Technisys, offset by income tax expense associated with the profitability of SoFi Bank in st
ate jurisdictions where separate filings are required, as well as federal taxes where our tax credits and loss carryforwards may be limited. Income taxes in 2022 were primarily att
ributable to tax expense at SoFi Lending Corp and SoFi Bank due to profitability in state jurisdictions where separate filings are required and recognition of expense from Technisy
s in certain Latin American countries where separate returns are filed. The expense was partially offset by deferred tax benefits from the amortization of intangible assets acquire
d in the Technisys Merger. (3) Depreciation and amortization expense in 2024 was primarily related to our internally-developed software and intangibles. Depreciation and amortizati
on expense in 2023 increased compared to 2022 primarily in connection with acquisitions and growth in our internally-developed software balance. (4) Restructuring charges in 2024 r
elate to legal entity restructuring. Restructuring charges in 2023 primarily included employee-related wages, benefits and severance associated with a small reduction in headcount 
in our Technology Platform segment in the first quarter of 2023 and expenses in the fourth quarter of 2023 related to a reduction in headcount across the Company, which do not refl
ect expected future operating expenses and are not indicative of our core operating performance. (5) Impairment expense in 2023 includes $247,174 related to goodwill impairment, an
d $1,243 related to a sublease arrangement, which are not indicative of our core operating performance. (6) Foreign currency charges reflect the impacts of highly inflationary acco
unting for our operations in Argentina, which are related to our Technology Platform segment and commenced in the first quarter of 2022 with the Technisys Merger. For the year ende
d December 31, 2023, all amounts were reflected in the fourth quarter, as inter-quarter amounts were determined to be immaterial. Amounts in 2022 were determined to be immaterial. 
(7) Transaction-related expenses in 2024 and 2023 included financial advisory and professional services costs associated with our acquisition of Wyndham. Transaction-related expens
es in 2022 primarily included financial advisory and professional services costs associated with our acquisition of Technisys. A-2 SoFi Technologies, Inc. Table of Contents (8) Ref
lects changes in fair value inputs and assumptions, including market servicing costs, conditional prepayment, default rates and discount rates. This non-cash change is unrealized d
uring the period and, therefore, has no impact on our cash flows from operations. As such, these positive and negative changes in fair value attributable to assumption changes are 
adjusted out of net income (loss) to provide management and financial users with better visibility into the earnings available to finance our operations. (9) Reflects changes in fa
ir value inputs and assumptions, including conditional prepayment, default rates and discount rates. When third parties finance our consolidated VIEs through purchasing residual in
terests, we receive proceeds at the time of the securitization close and, thereafter, pass along contractual cash flows to the residual interest owner. These obligations are measur
ed at fair value on a recurring basis, which has no impact on our initial financing proceeds, our future obligations to the residual interest owner (because future residual interes
t claims are limited to contractual securitization collateral cash flows), or the general operations of our business. As such, these positive and negative non-cash changes in fair 
value attributable to assumption changes are adjusted out of net income (loss) to provide management and financial users with better visibility into the earnings available to finan
ce our operations. (10) Reflects gain on extinguishment of debt. Gains and losses are recognized during the period of extinguishment for the difference between the net carrying amo
unt of debt extinguished and the fair value of equity securities issued. A-3 SoFi Technologies, Inc. Table of Contents SoFi Technologies, Inc. Table of Contents
"""