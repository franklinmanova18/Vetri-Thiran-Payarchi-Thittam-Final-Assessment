from ai_core.gemini_generator import (
    GeminiDocumentGenerator,
    GenerationResult,
)


class DocumentService:
    def __init__(self):
        self.generator = GeminiDocumentGenerator()

    def generate(self, **kwargs) -> GenerationResult:
        return self.generator.generate_document(**kwargs)
