"""
Template-based question generator
"""

import random
from typing import List, Dict, Set
from dataclasses import dataclass

from .parser import Application
from .templates import (
    TEMPLATES,
    ANSWER_EXTRACTORS,
    DIFFICULTY_BY_CATEGORY,
)


@dataclass
class Question:
    """Represents a generated question"""

    id: str
    question: str
    expected_answer: str
    category: str
    difficulty: str
    app_name: str
    app_id: str = None
    source_section: str = None
    generated_by: str = "template"
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {
            "id": self.id,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "category": self.category,
            "difficulty": self.difficulty,
            "app_name": self.app_name,
            "generated_by": self.generated_by,
        }

        if self.app_id:
            result["app_id"] = self.app_id

        if self.source_section:
            result["source_section"] = self.source_section

        if self.metadata:
            result["metadata"] = self.metadata

        return result


class TemplateQuestionGenerator:
    """Generate questions using templates"""

    def __init__(
        self,
        categories: List[str] = None,
        questions_per_section: int = 3,
        difficulty: List[str] = None,
        verbose: bool = False,
    ):
        self.categories = categories or ["all"]
        self.questions_per_section = questions_per_section
        self.difficulty_filter = difficulty or ["easy", "medium", "hard"]
        self.verbose = verbose
        self.question_counter = 0

    def generate(self, applications: List[Application]) -> List[Question]:
        """Generate questions from applications"""
        questions = []

        for app in applications:
            if self.verbose:
                print(f"[GENERATE] Application: {app.name}")

            app_questions = self._generate_for_app(app)
            questions.extend(app_questions)

            if self.verbose:
                print(f"  [OK] Generated {len(app_questions)} questions")

        if self.verbose:
            print(f"[OK] Total questions generated: {len(questions)}")

        return questions

    def _generate_for_app(self, app: Application) -> List[Question]:
        """Generate questions for a single application"""
        questions = []

        # Determine which categories to use
        categories = self._get_categories(app)

        for category in categories:
            category_questions = self._generate_for_category(app, category)
            questions.extend(category_questions)

        return questions

    def _get_categories(self, app: Application) -> List[str]:
        """Determine which categories to generate based on available data"""
        if "all" in self.categories:
            # Auto-detect available categories
            available = []

            if app.status:
                available.append("status")
            if app.full_name:
                available.append("full_info")
            if app.app_id:
                available.append("app_id")
            if app.geographic_scope:
                available.append("geographic_scope")
            if app.domains:
                available.append("domains")
            if app.description:
                available.append("description")
            if app.contacts:
                available.append("contacts")
            if app.events:
                available.append("events")
            if app.websites:
                available.append("websites")
            if app.actors:
                available.append("actors")
            if app.related_apps:
                available.append("related_apps")
            if app.related_data:
                available.append("related_data")
            if app.metadata:
                available.append("metadata")

            return available
        else:
            return self.categories

    def _generate_for_category(self, app: Application, category: str) -> List[Question]:
        """Generate questions for a specific category"""
        if category not in TEMPLATES:
            if self.verbose:
                print(f"  [WARNING] No templates for category: {category}")
            return []

        if category not in ANSWER_EXTRACTORS:
            if self.verbose:
                print(f"  [WARNING] No answer extractor for category: {category}")
            return []

        # Get answer
        answer_extractor = ANSWER_EXTRACTORS[category]
        answer = answer_extractor(app)

        if not answer or answer == "None":
            if self.verbose:
                print(f"  [SKIP] No data for category: {category}")
            return []

        # Get difficulty
        difficulty = DIFFICULTY_BY_CATEGORY.get(category, "medium")

        # Filter by difficulty
        if difficulty not in self.difficulty_filter:
            return []

        # Get templates for this category
        templates = TEMPLATES[category]

        # Select questions (up to questions_per_section)
        num_questions = min(self.questions_per_section, len(templates))
        selected_templates = random.sample(templates, num_questions)

        questions = []
        for template in selected_templates:
            question_text = template.format(app_name=app.name)

            self.question_counter += 1
            question = Question(
                id=f"q{self.question_counter:03d}",
                question=question_text,
                expected_answer=str(answer),
                category=category,
                difficulty=difficulty,
                app_name=app.name,
                app_id=app.app_id,
                source_section=category,
                generated_by="template",
            )

            questions.append(question)

        return questions

    def validate(self, questions: List[Question]) -> List[Question]:
        """Validate generated questions"""
        valid_questions = []

        for q in questions:
            # Check basic validity
            if not q.question.endswith('?'):
                if self.verbose:
                    print(f"[INVALID] Question doesn't end with '?': {q.question}")
                continue

            if len(q.question) < 10:
                if self.verbose:
                    print(f"[INVALID] Question too short: {q.question}")
                continue

            if not q.expected_answer or q.expected_answer == "None":
                if self.verbose:
                    print(f"[INVALID] No answer for question: {q.question}")
                continue

            valid_questions.append(q)

        if self.verbose:
            print(f"[VALIDATION] {len(valid_questions)}/{len(questions)} questions valid")

        return valid_questions
