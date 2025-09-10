"""
Django management command for optimizing JSON files.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path

from normieapp.services.directory_service import get_directory_service


class Command(BaseCommand):
    help = 'Optimize JSON files for faster loading'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            help='Input JSON file path (defaults to Verzeichnis.json)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output JSON file path (defaults to adding _compressed suffix)'
        )

    def handle(self, *args, **options):
        service = get_directory_service()
        
        # Default paths
        data_dir = Path(settings.BASE_DIR) / "normieapp" / "static" / "normieapp" / "data"
        input_file = options.get('input') or str(data_dir / "Verzeichnis.json")
        
        if not options.get('output'):
            input_path = Path(input_file)
            output_file = str(input_path.with_name(input_path.stem + '_compressed.json'))
        else:
            output_file = options['output']

        try:
            self.stdout.write(f"Optimizing {input_file}...")
            
            if not Path(input_file).exists():
                raise CommandError(f"Input file not found: {input_file}")
            
            size_info = service.optimize_json(input_file, output_file)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Optimization complete:\n"
                    f"  Original: {size_info['original_mb']:.1f}MB\n"
                    f"  Compressed: {size_info['compressed_mb']:.1f}MB\n"
                    f"  Savings: {size_info['savings_percent']:.1f}%\n"
                    f"  Output: {output_file}"
                )
            )

        except Exception as e:
            raise CommandError(f'Optimization failed: {str(e)}')

