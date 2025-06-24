from django.core.management.base import BaseCommand
from ._api_handler import OpenAlexAPIHandler 


class Command(BaseCommand):
    help = 'Update the database using data from the OpenAlex Works API.'

    def handle(self, *args, **options):
        handler = OpenAlexAPIHandler(
            email='gabrieldeusdeth@gmail.com' # Optional, but recommended for API calls
            )

        # Set your default query parameters here
        filters = {
            "institutions.ror": "03490as77"
            # Add more filters if needed
        }

        select = [
            "id",
            "doi",
            "title",
            "publication_year",
            "type",
            "open_access",
            "authorships",
            "primary_location",
            "counts_by_year",
            "topics",
            "referenced_works_count",
            "cited_by_count"
        ]

        try:
            handler.update_db_from_api(
                filters=filters,
                select=select,
                per_page=200, #Recommended to be 200 (max value allowed by OpenAlex)
                max_pages=None  # Optional limit
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during update: {e}"))
        else:
            self.stdout.write(self.style.SUCCESS("OpenAlex database update completed."))