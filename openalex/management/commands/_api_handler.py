import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlencode
from ._parser import OpenAlexWorkParser

class OpenAlexAPIHandler:
    """
    Handler class to interact with the OpenAlex Works API,
    retrieve records, and update the database via Django ORM.
    """

    def __init__(self, email=None):
        """
        Initialize the API handler with the base OpenAlex API URL
        and a resilient HTTP session.
        """
        self.base_url = "https://api.openalex.org/works"
        self.email = email 

        # ==========================================
        # CONFIGURAÇÃO DE SESSÃO E RETENTATIVAS
        # ==========================================
        self.session = requests.Session()
        
        # Configura a estratégia de Retry: Tenta até 5 vezes, 
        # com um tempo de espera (backoff) progressivo se falhar.
        retry_strategy = Retry(
            total=5,  # Número máximo de tentativas
            backoff_factor=1,  # Tempo de espera: 1s, 2s, 4s...
            status_forcelist=[429, 500, 502, 503, 504], # Códigos HTTP para insistir
            allowed_methods=["GET"]
        )
        
        # Aplica a estratégia na nossa sessão
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _process_and_update_db(self, results):
        for record in results:
            try:
                parser = OpenAlexWorkParser(record)
                parser.parse_and_save()
            except Exception as e:
                work_id = record.get('id', '[unknown]')
                print(f"Error processing record {work_id}: {str(e)}")

    def _build_filter_string(self, filters: dict) -> str:
        return ",".join(f"{k}:{v}" for k, v in filters.items() if v is not None)

    def _build_select_string(self, fields: list) -> str:
        return ",".join(fields)
    
    def _get_total_record_count(self, filters=None) -> int:
        query_params = {"per-page": 1, "cursor": "*"}
        if filters:
            query_params["filter"] = self._build_filter_string(filters)
        if self.email:
            query_params["mailto"] = self.email

        url = self.base_url + "?" + urlencode(query_params)
        
        # Usa a SESSÃO em vez de requests.get
        response = self.session.get(url, timeout=15)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch metadata: {response.status_code} - {response.text}")

        meta = response.json().get("meta", {})
        return meta.get("count", 0)

    def update_db_from_api(self, filters=None, select=None, per_page=200, max_pages=None):
        if per_page > 200:
            raise ValueError("The per_page parameter cannot be greater than 200.")

        total_records = self._get_total_record_count(filters)
        print(f"Total records to be retrieved: {total_records}")

        query_params = {
            "per-page": per_page,
            "cursor": "*" 
        }

        if filters:
            query_params["filter"] = self._build_filter_string(filters)
        if select:
            query_params["select"] = self._build_select_string(select)
        if self.email:
            query_params["mailto"] = self.email

        base_url = self.base_url
        cursor = query_params["cursor"]
        count = 0 
        count_records = 0 

        while cursor:
            if max_pages is not None and count >= max_pages:
                break

            query_params["cursor"] = cursor
            url = base_url + "?" + urlencode(query_params)
            print(f"\nFetching data from: {url}")

            try:
                # Usa a SESSÃO com timeout de 15 segundos para evitar travamentos
                response = self.session.get(url, timeout=15)
                
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

                page_data = response.json()
                results = page_data.get("results", [])
                count_records += len(results)

                if total_records > 0:
                    percent = (count_records / total_records) * 100
                    print(f"Retrieved {count_records} of {total_records} records ({percent:.2f}%)")

                print("Updating database...")
                self._process_and_update_db(results)

                cursor = page_data.get("meta", {}).get("next_cursor")
                count += 1
                
                # Opcional: Uma pausa microscópica por cortesia à API
                time.sleep(0.1) 

            # Captura especificamente a quebra de conexão, aguarda e continua
            except requests.exceptions.ConnectionError as e:
                print(f"\nConnection broken. Waiting 5 seconds before retrying... Error: {e}")
                time.sleep(5)
                continue # Volta para o início do while tentando o mesmo cursor