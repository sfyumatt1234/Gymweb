from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from tracker.note_import import import_transcript_note


class Command(BaseCommand):
    help = "Import a transcript file into the knowledge note system."

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="Absolute path to the transcript text file.")
        parser.add_argument("--title", help="Optional title override for the imported note.")

    def handle(self, *args, **options):
        source_path = options["path"]
        title = options.get("title")
        file_path = Path(source_path)
        if not file_path.exists():
            raise CommandError(f"File not found: {source_path}")

        raw_text = file_path.read_text(encoding="utf-8")
        note = import_transcript_note(source_path=source_path, raw_text=raw_text, title=title)
        self.stdout.write(
            self.style.SUCCESS(f"Imported knowledge note: {note.title} ({note.slug})")
        )
