"""
Django management command for updating directory data.
"""

from django.core.management.base import BaseCommand, CommandError
from normieapp.services.directory_service import get_directory_service


class Command(BaseCommand):
    help = 'Update directory data from Excel source'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run update once and exit'
        )
        parser.add_argument(
            '--continuous',
            action='store_true', 
            help='Run continuous updates in background'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Update interval in minutes (default: 5)'
        )

    def handle(self, *args, **options):
        service = get_directory_service()
        
        if service.updater is None:
            raise CommandError("Directory updater service not available")

        try:
            if options['once']:
                self.stdout.write("Running single directory update...")
                success = service.run_single_update()
                if success:
                    self.stdout.write(self.style.SUCCESS('Directory update completed successfully'))
                else:
                    raise CommandError('Directory update failed')

            elif options['continuous']:
                interval = options['interval']
                self.stdout.write(f"Starting continuous updates (every {interval} minutes)...")
                self.stdout.write("Press Ctrl+C to stop")
                
                # Set custom interval and start
                service.interval = interval * 60
                service.start()
                
                try:
                    # Keep the command running
                    while True:
                        import time
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stdout.write("\nStopping service...")
                    service.stop()
                    self.stdout.write("Stopped by user")

            else:
                # Default: run once
                self.stdout.write("Running single directory update (use --continuous for background mode)...")
                success = service.run_single_update()
                if success:
                    self.stdout.write(self.style.SUCCESS('Directory update completed successfully'))
                else:
                    raise CommandError('Directory update failed')

        except Exception as e:
            raise CommandError(f'Update failed: {str(e)}')
