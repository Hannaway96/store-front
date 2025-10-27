""""
Django command to wait for the DB to be available
"""

import time
from django.db.utils import OperationalError
from psycopg import OperationalError as PsyCopgError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django Command to wait for Database"""

    def handle(self, *args, **kwargs):
        """Entrypoint for command"""
        self.stdout.write("Waiting for database...")
        db_up = False

        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, PsyCopgError):
                self.stdout.write('Database Unavailable, waiting for 3 seconds')
                time.sleep(3)

        self.stdout.write('Database Available')