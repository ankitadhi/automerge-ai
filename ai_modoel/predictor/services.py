# predictor/services.py - CORRECTED FOR AutoMerge AI
import torch
import logging
from transformers import T5ForConditionalGeneration, RobertaTokenizer

logger = logging.getLogger(__name__)


class MergeResolverModel:
    """
    Service class for the AutoMerge AI CodeT5 model
    Based on the README: Uses T5ForConditionalGeneration and RobertaTokenizer
    """
    _instance = None
    _model = None
    _tokenizer = None
    _device = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MergeResolverModel, cls).__new__(cls)
            cls._instance.initialize_model()
        return cls._instance

    def initialize_model(self):
        """Initialize the PyTorch CodeT5 model and tokenizer"""
        try:
            logger.info(
                "Loading AutoMerge AI model: ankit-ml11/automerge-codet5")

            # Use GPU if available
            self._device = torch.device(
                'cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Using device: {self._device}")

            # CORRECT: Use T5ForConditionalGeneration and RobertaTokenizer per README
            self._tokenizer = RobertaTokenizer.from_pretrained(
                "ankit-ml11/automerge-codet5")
            self._model = T5ForConditionalGeneration.from_pretrained(
                "ankit-ml11/automerge-codet5")

            # Move model to device
            self._model = self._model.to(self._device)
            self._model.eval()

            logger.info("AutoMerge AI model loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def parse_git_conflict(self, conflict_text: str):
        """
        Parse standard Git conflict markers into base, ours, theirs.
        According to README, model needs three separate code versions.
        """
        lines = conflict_text.split('\n')
        ours_lines, base_lines, theirs_lines = [], [], []
        section = None

        for line in lines:
            if line.startswith('<<<<<<<'):
                section = 'ours'
            elif line.startswith('|||||||'):
                section = 'base'
            elif line.startswith('======='):
                section = 'theirs'
            elif line.startswith('>>>>>>>'):
                section = None
            elif section == 'ours':
                ours_lines.append(line)
            elif section == 'base':
                base_lines.append(line)
            elif section == 'theirs':
                theirs_lines.append(line)

        # Join lines and handle missing sections
        base_code = '\n'.join(
            base_lines) if base_lines else '\n'.join(ours_lines)
        ours_code = '\n'.join(ours_lines)
        theirs_code = '\n'.join(theirs_lines)

        return {
            'base': base_code,
            'ours': ours_code,
            'theirs': theirs_code
        }

    def resolve_merge_conflict(self, conflict_text: str, language: str = "python", max_length: int = 512) -> str:
        """
        Resolve a merge conflict using the AutoMerge AI model.
        
        Args:
            conflict_text: Git conflict text with markers
            language: Programming language (python, javascript, java, etc.)
            max_length: Maximum length of generated output
        
        Returns:
            Resolved code
        """
        try:
            # 1. Parse the Git conflict into three parts
            parsed = self.parse_git_conflict(conflict_text)

            # 2. Format input EXACTLY as shown in README
            input_text = f"""Resolve the following merge conflict in {language}.

BASE VERSION:
{parsed['base']}

OURS VERSION:
{parsed['ours']}

THEIRS VERSION:
{parsed['theirs']}
"""

            # 3. Tokenize with RobertaTokenizer
            inputs = self._tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self._device)

            # 4. Generate resolution
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=5,
                    early_stopping=True,
                    no_repeat_ngram_size=3
                )

            # 5. Decode and return
            resolved_code = self._tokenizer.decode(
                outputs[0], skip_special_tokens=True)

            return resolved_code

        except Exception as e:
            logger.error(f"Error during inference: {str(e)}")
            raise

    def batch_resolve(self, conflict_texts: list, language: str = "python", max_length: int = 512) -> list:
        """
        Resolve multiple merge conflicts
        
        Args:
            conflict_texts: List of Git conflict texts
            language: Programming language
            max_length: Maximum length of generated output
        
        Returns:
            List of resolution results
        """
        results = []
        for conflict_text in conflict_texts:
            try:
                resolved = self.resolve_merge_conflict(
                    conflict_text, language, max_length)
                results.append({
                    "input": conflict_text,
                    "resolved": resolved,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "input": conflict_text,
                    "resolved": "",
                    "status": "error",
                    "error": str(e)
                })

        return results


# Global instance - KEEP THIS
merge_resolver = MergeResolverModel()
