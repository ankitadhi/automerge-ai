from django.core.management.base import BaseCommand
from predictor.services import MergeResolverModel


class Command(BaseCommand):
    help = 'Pre-load the merge resolver model at startup'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            'Loading merge resolver model...'))
        try:
            model = MergeResolverModel()
            self.stdout.write(self.style.SUCCESS(
                f'Model loaded successfully on {model._device}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Failed to load model: {str(e)}'))
