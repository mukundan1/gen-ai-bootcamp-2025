import boto3
import json
from typing import Dict, List, Optional
from backend.vector_store import QuestionVectorStore

class JLPTQuestionCreator:
    def __init__(self):
        self.aws_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.question_db = QuestionVectorStore()
        self.llm_model = "amazon.nova-lite-v1:0"

    def _query_llm(self, input_text: str) -> Optional[str]:
        try:
            msg_format = [{
                "role": "user",
                "content": [{"text": input_text}]
            }]
            
            result = self.aws_client.converse(
                modelId=self.llm_model,
                messages=msg_format,
                inferenceConfig={"temperature": 0.7}
            )
            
            return result['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"LLM query failed: {str(e)}")
            return None

    def create_question(self, section: int, category: str) -> Dict:
        example_questions = self.question_db.search_similar_questions(section, category, n_results=3)
        if not example_questions:
            return None

        prompt_template = self._build_prompt(example_questions, section, category)
        raw_response = self._query_llm(prompt_template)
        if not raw_response:
            return None

        return self._process_response(raw_response, section)

    def _build_prompt(self, examples: List[Dict], section: int, category: str) -> str:
        prompt = f"Create a new JLPT {category} listening question based on these examples:\n\n"
        
        for i, ex in enumerate(examples, 1):
            prompt += f"Example {i}:\n"
            if section == 2:
                prompt += self._format_section_2(ex)
            else:
                prompt += self._format_section_3(ex)
            prompt += "\n"

        prompt += "\nGenerate a unique question following the same structure."
        return prompt

    def _format_section_2(self, example: Dict) -> str:
        return (f"Introduction: {example.get('Introduction', '')}\n"
                f"Conversation: {example.get('Conversation', '')}\n"
                f"Question: {example.get('Question', '')}\n"
                f"Options: {self._format_options(example.get('Options', []))}")

    def _format_section_3(self, example: Dict) -> str:
        return (f"Situation: {example.get('Situation', '')}\n"
                f"Question: {example.get('Question', '')}\n"
                f"Options: {self._format_options(example.get('Options', []))}")

    def _format_options(self, options: List[str]) -> str:
        return "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))

    def _process_response(self, response: str, section: int) -> Dict:
        result = {}
        current_field = None
        field_content = []

        for line in response.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            field = self._identify_field(line)
            if field:
                if current_field:
                    result[current_field] = self._clean_field_content(field_content)
                current_field = field
                field_content = []
            else:
                field_content.append(line)

        if current_field:
            result[current_field] = self._clean_field_content(field_content)

        self._validate_question(result)
        return result

    def _identify_field(self, line: str) -> Optional[str]:
        fields = {
            "Introduction:", "Conversation:", "Situation:",
            "Question:", "Options:"
        }
        return next((f.replace(":", "") for f in fields if line.startswith(f)), None)

    def _clean_field_content(self, content: List[str]) -> str:
        return ' '.join(content)

    def _validate_question(self, question: Dict) -> None:
        if 'Options' not in question:
            question['Options'] = [
                "はい、そうです。",
                "いいえ、違います。",
                "わかりません。",
                "もう一度お願いします。"
            ]

    def generate_feedback(self, question: Dict, user_choice: int) -> Dict:
        prompt = self._create_feedback_prompt(question, user_choice)
        response = self._query_llm(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "correct": False,
                "explanation": "フィードバックを生成できませんでした。",
                "correct_answer": 1
            }

    def _create_feedback_prompt(self, question: Dict, choice: int) -> str:
        return f"""Analyze this answer:
Question: {question.get('Question')}
Selected: Option {choice}
Provide feedback in JSON with: correct (boolean), explanation (string), correct_answer (int)"""
