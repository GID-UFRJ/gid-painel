import requests
from urllib.parse import urlencode
from ._parser import OpenAlexWorkParser
#import logging
#
#logger = logging.getLogger(__name__)

class OpenAlexAPIHandler:
    """
    Handler class to interact with the OpenAlex Works API,
    retrieve records, and update the database via Django ORM.
    """

    def __init__(self, email = None):
        """
        Initialize the API handler with the base OpenAlex API URL.

        Args:
        email (str, optional): Email address for polite API usage (recommended).
        """
        self.base_url = "https://api.openalex.org/works"
        self.email = email #Defined in the constructor to allow for multiple api queries without inserting email over and over again

    def _process_and_update_db(self, results):
        """
        Process a list of OpenAlex work records and update the database.

        For each record, it uses the OpenAlexWorkParser to parse
        and save the record via Django ORM.

        Args:
            results (list): List of work records (dictionaries) from the API.
        """
        for record in results:
            try:
                parser = OpenAlexWorkParser(record)
                parser.parse_and_save()
            except Exception as e:
                work_id = record.get('id', '[unknown]')
                print(f"Error processing record {work_id}: {str(e)}")
                #logger.error("Error processing record %s: %s", work_id, str(e), exc_info=True)


    def _build_filter_string(self, filters: dict) -> str:
        """
        Construct the OpenAlex API filter query string from a dictionary.

        Args:
            filters (dict): Dictionary of filter keys and values.

        Returns:
            str: Comma-separated filter string suitable for the API.
        """
        return ",".join(f"{k}:{v}" for k, v in filters.items() if v is not None)

    def _build_select_string(self, fields: list) -> str:
        """
        Construct the OpenAlex API select query string from a list of fields.

        Args:
            fields (list): List of field names to select.

        Returns:
            str: Comma-separated select string suitable for the API.
        """
        return ",".join(fields)
    
    def _get_total_record_count(self, filters=None) -> int:
        """
        Fetch the total number of records that match the given filters,
        without downloading all data.

        Args:
            filters (dict, optional): Dictionary of filter conditions.

        Returns:
            int: Total number of matching records.
        """
        query_params = {"per-page": 1, "cursor": "*"}
        if filters:
            query_params["filter"] = self._build_filter_string(filters)

        url = self.base_url + "?" + urlencode(query_params)
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch metadata: {response.status_code} - {response.text}")

        meta = response.json().get("meta", {})
        return meta.get("count", 0)

    def update_db_from_api(self, filters=None, select=None, per_page=200, max_pages=None):
        """
        Retrieve works from the OpenAlex API using optional filters and select fields,
        then parse and insert them into the database using Django ORM.

        Args:
            filters (dict, optional): Dictionary of filter conditions for API.
            select (list, optional): List of fields to retrieve per record.
            per_page (int, optional): Number of records per page (max 200).
            max_pages (int, optional): Maximum number of pages to retrieve.

        Raises:
            ValueError: If per_page is greater than 200.
            Exception: For HTTP request failures.
        """
        if per_page > 200:
            raise ValueError("The per_page parameter cannot be greater than 200.")

        # Get total number of records that match the filters (for progress tracking)
        total_records = self._get_total_record_count(filters)
        print(f"Total records to be retrieved: {total_records}")

        # Prepare initial query parameters
        query_params = {
            "per-page": per_page,
            "cursor": "*"  # OpenAlex uses cursor-based pagination starting with "*"
        }

        if filters:
            query_params["filter"] = self._build_filter_string(filters)
        if select:
            query_params["select"] = self._build_select_string(select)
        if self.email:
            query_params["mailto"] = self.email

        base_url = self.base_url
        cursor = query_params["cursor"]
        count = 0  # Page counter
        count_records = 0  # Total records processed so far

        # Loop through pages until no more data or max_pages reached
        while cursor:
            if max_pages is not None and count >= max_pages:
                break

            query_params["cursor"] = cursor
            url = base_url + "?" + urlencode(query_params)
            print(f"\nFetching data from: {url}")

            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

            page_data = response.json()
            results = page_data.get("results", [])
            count_records += len(results)

            # Print progress if total is known
            if total_records > 0:
                percent = (count_records / total_records) * 100
                print(f"Retrieved {count_records} of {total_records} records ({percent:.2f}%)")

            print("Updating database...")
            self._process_and_update_db(results)

            # Update cursor for next page
            cursor = page_data.get("meta", {}).get("next_cursor")
            count += 1
