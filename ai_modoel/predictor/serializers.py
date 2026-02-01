# predictor/serializers.py
from rest_framework import serializers


class MergeConflictSerializer(serializers.Serializer):
    conflict_text = serializers.CharField(required=True)
    language = serializers.CharField(
        required=False,
        default="python",
        help_text="Programming language: python, javascript, java, etc."
    )
    max_length = serializers.IntegerField(
        required=False,
        default=512,
        min_value=10,
        max_value=1024
    )


class BatchMergeConflictSerializer(serializers.Serializer):
    conflicts = serializers.ListField(child=serializers.CharField())
    language = serializers.CharField(required=False, default="python")
    max_length = serializers.IntegerField(required=False, default=512)


class MergeResolutionResponseSerializer(serializers.Serializer):
    input = serializers.CharField(help_text="Original conflict text")
    language = serializers.CharField(
        help_text="Programming language used for resolution")
    resolved = serializers.CharField(help_text="Resolved code")
    status = serializers.CharField(help_text="Status: success/error")
    processing_time = serializers.FloatField(
        required=False,
        help_text="Time taken to process in seconds"
    )


class BatchMergeResolutionResponseSerializer(serializers.Serializer):
    results = MergeResolutionResponseSerializer(many=True)
    total = serializers.IntegerField()
    successful = serializers.IntegerField()
    failed = serializers.IntegerField()
    language = serializers.CharField(
        help_text="Programming language used for resolution")
    total_time = serializers.FloatField()
