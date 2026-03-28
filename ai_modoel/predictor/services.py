# predictor/services.py - FINAL (RAW CONFLICT, NO PROMPT)

import torch
import logging
from transformers import T5ForConditionalGeneration, RobertaTokenizer

logger = logging.getLogger(__name__)


class MergeResolverModel:
    """
    AutoMerge AI Service (FINAL VERSION)

    ✔ Uses RAW Git conflict markers directly
    ✔ No prompt (matches training format)
    ✔ Removes input echo issue
    ✔ Cleans leftover markers
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
        """Load model and tokenizer"""
        try:
            logger.info("Loading AutoMerge AI model...")

            # Device setup
            self._device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
            logger.info(f"Using device: {self._device}")

            # Load tokenizer + model
            self._tokenizer = RobertaTokenizer.from_pretrained(
                "ankit-ml11/codet5p-220_conflict_resolver"
            )
            self._model = T5ForConditionalGeneration.from_pretrained(
                "ankit-ml11/codet5p-220_conflict_resolver"
            )

            self._model.to(self._device)
            self._model.eval()

            logger.info("✅ Model loaded successfully!")

        except Exception as e:
            logger.error(f"❌ Model loading failed: {str(e)}")
            raise

    def clean_output(self, text: str) -> str:
        """
        Remove unwanted artifacts from model output
        """
        markers = ["<<<<<<<", "=======", ">>>>>>>", "|||||||"]

        for marker in markers:
            text = text.replace(marker, "")

        return text.strip()

    def remove_input_echo(self, output: str, input_text: str) -> str:
        """
        Remove copied input from model output
        """
        if input_text in output:
            output = output.replace(input_text, "")

        return output.strip()

    def resolve_merge_conflict(
        self,
        conflict_text: str,
        language: str = "python",
        max_length: int = 512
    ) -> str:
        """
        Resolve merge conflict using RAW input only

        Args:
            conflict_text: Raw Git conflict text
            language: (unused but kept for API compatibility)
            max_length: max output tokens

        Returns:
            Clean resolved code
        """
        try:
            # 🔥 CRITICAL: NO PROMPT (matches training)
            input_text = conflict_text

            inputs = self._tokenizer(
                input_text,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            ).to(self._device)

            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=5,
                    early_stopping=True
                )

            resolved_code = self._tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )

            # 🔥 FIX 1: Remove echoed input
            resolved_code = self.remove_input_echo(
                resolved_code,
                input_text
            )

            # 🔥 FIX 2: Clean leftover markers
            resolved_code = self.clean_output(resolved_code)

            return resolved_code

        except Exception as e:
            logger.error(f"❌ Inference error: {str(e)}")
            raise

    def batch_resolve(
        self,
        conflict_texts: list,
        language: str = "python",
        max_length: int = 512
    ) -> list:
        """
        Resolve multiple conflicts
        """
        results = []

        for conflict_text in conflict_texts:
            try:
                resolved = self.resolve_merge_conflict(
                    conflict_text,
                    language,
                    max_length
                )

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


# ✅ Global instance (DO NOT REMOVE)
merge_resolver = MergeResolverModel()
