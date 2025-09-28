from django.core.management.base import BaseCommand
from music_app.models import Music, MusicStatistics

class Command(BaseCommand):
    help = 'Create missing statistics for music entries'

    def handle(self, *args, **options):
        musics_without_stats = Music.objects.filter(statistics__isnull=True)
        stats_created = 0
        
        for music in musics_without_stats:
            MusicStatistics.objects.create(music=music)
            stats_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {stats_created} missing statistics entries'
            )
        )
