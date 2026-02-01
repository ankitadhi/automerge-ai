import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import (
    MergeConflictSerializer,
    BatchMergeConflictSerializer,
    MergeResolutionResponseSerializer,
    BatchMergeResolutionResponseSerializer
)
# Correct import: import the instance, not the class
from .services import merge_resolver


class ResolveMergeConflictView(APIView):
    """
    API endpoint to resolve a single merge conflict
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MergeConflictSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        conflict_text = serializer.validated_data['conflict_text']
        language = serializer.validated_data.get(
            'language', 'python')  # Get language, default to python
        max_length = serializer.validated_data.get('max_length', 512)

        try:
            start_time = time.time()

            # Resolve merge conflict using the instance - ADD LANGUAGE PARAMETER
            resolved_code = merge_resolver.resolve_merge_conflict(
                conflict_text=conflict_text,
                language=language,
                max_length=max_length
            )

            processing_time = time.time() - start_time

            response_data = {
                "input": conflict_text,
                "language": language,
                "resolved": resolved_code,
                "status": "success",
                "processing_time": round(processing_time, 3)
            }

            response_serializer = MergeResolutionResponseSerializer(
                data=response_data)
            response_serializer.is_valid()

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": "Failed to resolve merge conflict",
                    "message": str(e),
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchResolveMergeConflictView(APIView):
    """
    API endpoint to resolve multiple merge conflicts in batch
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BatchMergeConflictSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        conflicts = serializer.validated_data['conflicts']
        language = serializer.validated_data.get(
            'language', 'python')  # Get language, default to python
        max_length = serializer.validated_data.get('max_length', 512)

        try:
            start_time = time.time()

            # Process all conflicts using the instance - ADD LANGUAGE PARAMETER
            results = merge_resolver.batch_resolve(
                conflict_texts=conflicts,
                language=language,
                max_length=max_length
            )

            total_time = time.time() - start_time

            # Calculate statistics
            successful = sum(1 for r in results if r['status'] == 'success')
            failed = len(results) - successful

            response_data = {
                "results": results,
                "total": len(results),
                "successful": successful,
                "failed": failed,
                "language": language,
                "total_time": round(total_time, 3)
            }

            response_serializer = BatchMergeResolutionResponseSerializer(
                data=response_data)
            response_serializer.is_valid()

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "error": "Failed to process batch request",
                    "message": str(e),
                    "status": "error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """
    Health check endpoint to verify model is loaded
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Create a test merge conflict to pass to the model
            test_input = """<<<<<<< HEAD
def calculate_sum(a, b):
    return a + b
=======
def calculate_sum(x, y):
    result = x + y
    return result
>>>>>>> feature-branch"""

            # Use the instance to call the method - ADD LANGUAGE PARAMETER
            resolved = merge_resolver.resolve_merge_conflict(
                conflict_text=test_input,
                language="python",
                max_length=100
            )

            return Response({
                "status": "healthy",
                "model_loaded": True,
                "model_name": "ankit-ml11/code-t5-merge-resolver",
                "framework": "PyTorch (T5ForConditionalGeneration)",
                "test_resolution": resolved[:100] + "..." if len(resolved) > 100 else resolved,
                "language_support": ["python", "javascript", "java", "c++", "go", "ruby", "php"]
            })
        except Exception as e:
            return Response({
                "status": "unhealthy",
                "error": str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
