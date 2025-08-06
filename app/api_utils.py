import asyncio
import json
import logging
from typing import Dict, List

import aiohttp
from tenacity import (before_sleep_log, retry, retry_if_exception_type,
                      retry_if_result, stop_after_attempt, wait_exponential)

from . import schemas
from .config import api_config, settings

# Setup detailed logging
logger = logging.getLogger(__name__)

API_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent",
    "openai": "https://api.openai.com/v1/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
}

def get_generation_prompt(section: str, topic: str, grade_level: str = "high school", difficulty: str = "medium") -> str:
    difficulty_map = {
        "easy": "basic level with simple concepts",
        "medium": "intermediate level with moderate complexity", 
        "hard": "advanced level with complex reasoning"
    }
    
    return f'''Generate a unique, high-quality multiple-choice question for exam preparation.

Requirements:
- Section: "{section}"
- Topic: "{topic}" 
- Grade Level: "{grade_level}"
- Difficulty: "{difficulty_map.get(difficulty, 'intermediate level')}"

IMPORTANT INSTRUCTIONS:
1. Create an original question that tests understanding of the concept
2. Provide exactly 4 unique options with only one correct answer
3. Include a detailed explanation

Your response MUST be a single, valid JSON object with these exact keys:
- "question_text": Clear, well-formed question
- "options": Array of exactly 4 unique answer choices
- "correct_answer": Must match one of the options exactly
- "explanation": Detailed explanation of why the answer is correct
- "section": The section name
- "topic": The topic name

Do not include any text or formatting outside the JSON object.'''

def get_generation_prompt_for_manual_mode(num_questions: int, topics: Dict[str, List[str]], grade_level: str = "high school", difficulty: str = "medium") -> str:
    sections = list(topics.keys())
    topics_list = [t for sublist in topics.values() for t in sublist]
    difficulty_map = {
        "easy": "basic level with simple concepts",
        "medium": "intermediate level with moderate complexity",
        "hard": "advanced level with complex reasoning"
    }
    
    return f'''Generate exactly {num_questions} unique multiple-choice questions for exam preparation.

Requirements:
- Sections: {', '.join(sections)}
- Topics: {', '.join(topics_list)}
- Grade Level: "{grade_level}"
- Difficulty: "{difficulty_map.get(difficulty, 'intermediate level')}"

IMPORTANT INSTRUCTIONS:
1. Generate exactly {num_questions} questions, no more, no less
2. Each question must have exactly 4 unique options with only one correct answer
3. Distribute questions evenly across the provided topics
4. Include detailed explanations for each answer

Response format: Return a JSON array of exactly {num_questions} objects, each with:
- "question_text": Clear, well-formed question
- "options": Array of exactly 4 unique answer choices  
- "correct_answer": Must match one of the options exactly
- "explanation": Detailed explanation
- "section": The section name
- "topic": The topic name

Ensure the response is valid JSON with exactly {num_questions} question objects.'''

def is_error_result(result):
    """Check if the result contains an error key."""
    return isinstance(result, dict) and "error" in result

@retry(
    stop=stop_after_attempt(api_config.MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=15),
    retry=(retry_if_exception_type((aiohttp.ClientResponseError, aiohttp.ServerDisconnectedError, asyncio.TimeoutError)) | retry_if_result(is_error_result)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def _generate_single_question(session: aiohttp.ClientSession, topic: str, section: str, api_provider: str, api_key: str, grade_level: str = "high school", difficulty: str = "medium") -> dict:
    logger.info(f"Generating question for topic '{topic}' in section '{section}' using {api_provider}.")
    
    # Validate inputs
    if not api_key or api_key == "null":
        logger.error(f"Invalid API key for {api_provider}")
        return {"error": f"Invalid API key for {api_provider}"}
    
    if not topic or not section:
        logger.error(f"Invalid topic or section: topic='{topic}', section='{section}'")
        return {"error": "Topic and section must not be empty"}
    
    if api_provider not in api_config.SUPPORTED_PROVIDERS:
        logger.error(f"Unsupported API provider: {api_provider}")
        return {"error": f"Unsupported API provider: {api_provider}. Supported: {api_config.SUPPORTED_PROVIDERS}"}
    
    url = API_URLS.get(api_provider)
    if not url:
        logger.error(f"Invalid API provider: {api_provider}")
        return {"error": f"Invalid API provider: {api_provider}"}

    headers, payload = {"Content-Type": "application/json"}, {}
    prompt = get_generation_prompt(section, topic, grade_level, difficulty)

    if api_provider == "gemini":
        url = f"{url}?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
    else:
        headers["Authorization"] = f"Bearer {api_key}"
        model = "gpt-3.5-turbo" if api_provider == "openai" else "mixtral-8x7b-32768"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }

    try:
        async with session.post(url, headers=headers, json=payload, timeout=api_config.TIMEOUT) as response:
            status = response.status
            headers_str = str(response.headers)
            response_text = await response.text()
            
            if settings.DEBUG:
                logger.debug(f"API response from {api_provider}: status={status}, headers={headers_str}, body={response_text[:200]}...")

            if status == 429:
                logger.warning(f"Rate limit exceeded for {api_provider}")
                return {"error": f"Rate limit exceeded for {api_provider}"}
            
            if status != 200:
                logger.error(f"API request to {api_provider} failed with status {status}. Response: {response_text[:200]}")
                return {"error": f"API request failed with status {status}: {response_text[:100]}"}

            if not response_text.strip():
                logger.error(f"Empty response from {api_provider}.")
                return {"error": "Empty response from AI provider"}

            try:
                result = json.loads(response_text)
                content_str = None
                if api_provider == "gemini":
                    content_str = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text")
                else:
                    content_str = result.get("choices", [{}])[0].get("message", {}).get("content")

                if not content_str:
                    logger.error(f"Missing content in {api_provider} response. Full response: {json.dumps(result)[:200]}")
                    return {"error": "Missing content in AI provider response"}

                try:
                    question_data = json.loads(content_str)
                    required_fields = ["question_text", "options", "correct_answer", "explanation", "section", "topic"]
                    if not all(field in question_data for field in required_fields):
                        logger.error(f"Invalid question format from {api_provider}. Missing fields in: {json.dumps(question_data)[:200]}")
                        return {"error": "Invalid question format: missing required fields"}
                    if not isinstance(question_data["options"], list) or len(question_data["options"]) != 4:
                        logger.error(f"Invalid options format from {api_provider}: {question_data.get('options', [])}")
                        return {"error": "Invalid question format: options must be a list of 4 strings"}
                    if question_data["correct_answer"] not in question_data["options"]:
                        logger.error(f"Correct answer not in options: {question_data['correct_answer']} not in {question_data['options']}")
                        return {"error": "Invalid question format: correct answer must be one of the options"}
                    
                    if settings.DEBUG:
                        logger.debug(f"Generated valid question: {question_data['question_text'][:50]}...")
                    return question_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse content as JSON from {api_provider}. Content: '{content_str[:200]}'")
                    return {"error": f"Invalid JSON content from {api_provider}: {str(e)}"}
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse API response as JSON from {api_provider}. Raw response: '{response_text[:200]}'")
                return {"error": f"Invalid JSON response from {api_provider}: {str(e)}"}
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected API response structure from {api_provider}: {str(e)}. Full response: {json.dumps(result)[:200]}")
                return {"error": f"Unexpected response structure: {str(e)}"}
    except aiohttp.ClientResponseError as e:
        if e.status in [401, 403]:
            logger.error(f"Authentication error for {api_provider}: {str(e)}")
            return {"error": f"Authentication failed for {api_provider}: {str(e)}"}
        raise
    except Exception as e:
        logger.error(f"Error in _generate_single_question for {api_provider}: {str(e)}", exc_info=True)
        return {"error": f"Failed to generate question: {str(e)}"}

async def get_questions(request: schemas.StartQuizRequest) -> List[dict]:
    logger.info(f"Starting question generation for {request.num_questions} questions with provider {request.api_provider}.")
    
    # Validate inputs
    if not request.topics:
        logger.error("No topics provided for question generation.")
        return [{"error": "No topics provided"}]
    
    if request.num_questions > api_config.MAX_QUESTIONS:
        logger.error(f"Too many questions requested: {request.num_questions} > {api_config.MAX_QUESTIONS}")
        return [{"error": f"Maximum {api_config.MAX_QUESTIONS} questions allowed"}]
    
    # Extract grade_level and difficulty with defaults
    grade_level = getattr(request, 'grade_level', 'high school')
    difficulty = getattr(request, 'difficulty', 'medium')
    
    used_questions, generated_questions = set(), []
    max_retries = 5
    retry_count = 0
    
    async with aiohttp.ClientSession() as session:
        while len(generated_questions) < request.num_questions and retry_count < max_retries:
            remaining_questions = request.num_questions - len(generated_questions)
            logger.info(f"Attempt {retry_count + 1}: Generating {remaining_questions} more questions")
            
            tasks = [
                _generate_single_question(
                    session, 
                    topic_dict['topic'], 
                    topic_dict['section'], 
                    request.api_provider, 
                    request.api_key,
                    grade_level,
                    difficulty
                )
                for _ in range(remaining_questions)
                for topic_dict in [request.topics[_ % len(request.topics)]]
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, res in enumerate(results):
                if isinstance(res, Exception):
                    logger.error(f"Task {i} failed in question generation: {res}", exc_info=True)
                    continue
                if is_error_result(res):
                    logger.warning(f"Task {i} returned an error: {res['error']}")
                    continue
                if isinstance(res, dict):
                    question_signature = res.get("question_text", "").strip().lower()
                    if question_signature and question_signature not in used_questions:
                        if settings.DEBUG:
                            logger.debug(f"Successfully generated and added question: {question_signature[:50]}...")
                        generated_questions.append(res)
                        used_questions.add(question_signature)
                    else:
                        logger.warning(f"Duplicate or empty question was generated. Discarding.")
                else:
                    logger.warning(f"Task {i} resulted in an invalid result: {res}")
            
            retry_count += 1
            
            if len(generated_questions) < request.num_questions:
                logger.warning(f"Only generated {len(generated_questions)} out of {request.num_questions} questions. Retrying...")
                await asyncio.sleep(2)  # Brief pause before retry

    if not generated_questions:
        logger.error("No valid questions generated for the request.")
        return [{"error": "No valid questions could be generated. Please check your API key or try again later."}]

    logger.info(f"Finished generation. Total unique questions: {len(generated_questions)}")
    return generated_questions[:request.num_questions]

async def get_ai_explanation(question_context: dict, user_query: str, api_key: str) -> str:
    logger.info(f"Generating AI explanation for query: {user_query[:50]}...")
    
    # Validate inputs
    if not user_query:
        logger.error("User query is empty.")
        return "Error: User query cannot be empty."
    
    if not question_context or not all(key in question_context for key in ["question_text", "explanation"]):
        logger.error("Invalid question context provided.")
        return "Error: Question context must include question_text and explanation."
    
    prompt = f"Context:\n- Question: {question_context.get('question_text')}\n- Explanation: {question_context.get('explanation')}\n\nBased on the context, answer the user query concisely.\nUser Query: \"{user_query}\""
    async with aiohttp.ClientSession() as session:
        url = f"{API_URLS['gemini']}?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "text/plain"}
        }
        try:
            async with session.post(url, json=payload, timeout=api_config.TIMEOUT) as response:
                status = response.status
                response_text = await response.text()
                
                if settings.DEBUG:
                    logger.debug(f"AI explanation response: status={status}, body={response_text[:200]}...")
                
                if status == 429:
                    logger.warning("Rate limit exceeded for Gemini API.")
                    return "Error: Rate limit exceeded for Gemini API."
                
                if status != 200:
                    logger.error(f"AI explanation request failed with status {status}. Response: {response_text[:200]}")
                    return f"Error: AI provider returned status {status}: {response_text[:100]}"

                if not response_text.strip():
                    logger.error("Empty AI explanation response.")
                    return "Error: The AI provider returned an empty response."

                try:
                    result = json.loads(response_text)
                    content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sorry, I couldn't get an explanation for that.")
                    if settings.DEBUG:
                        logger.debug(f"AI explanation extracted: {content[:50]}...")
                    return content
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON from AI explanation response. Raw text: '{response_text[:200]}'")
                    return f"Error: Invalid JSON response from AI provider: {str(e)}"
        except aiohttp.ClientResponseError as e:
            if e.status in [401, 403]:
                logger.error(f"Authentication error for Gemini: {str(e)}")
                return f"Error: Authentication failed for Gemini: {str(e)}"
            raise
        except Exception as e:
            logger.error(f"Error in get_ai_explanation: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"