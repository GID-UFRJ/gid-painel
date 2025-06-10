from django.db import transaction
from openalex.models import Year, WorkType, OAStatus, PrimarySource, Work, Institution, Author, Authorship, AuthorshipInstitution, CitedByYear, Topic, WorkTopic

class OpenAlexWorkParser:
    def __init__(self, json_data):
        self.json_data = json_data
        self._source = ((json_data.get("primary_location") or {}).get("source") or {})
        self.work_obj = None  # Will hold created Work instance
        self.primary_source_obj = None  # Will hold created PrimarySource instance

    def _clean_id(self, id_str):
        if not id_str:
            return None
        id_str = id_str.rstrip('/')
        if 'doi.org/' in id_str.lower():
            return id_str.split('doi.org/')[-1]
        return id_str.split('/')[-1]

    def parse_and_save(self):
        """Run the full save pipeline inside a transaction."""
        with transaction.atomic():
            self._save_primary_source()
            self._save_work()
            self._save_authorships()
            self._save_cited_by_year()
            self._save_topics()

    def _save_primary_source(self):
        source_data = self._source
        if not source_data:
            return None
        source_id = self._clean_id(source_data.get("id"))
        self.primary_source_obj, _ = PrimarySource.objects.get_or_create(
            source_id=source_id,
            defaults={
                "source_name": source_data.get("display_name"),
                "source_issn_l": source_data.get("issn_l"),
                "is_oa": source_data.get("is_oa"),
                "host_organization_id": self._clean_id(source_data.get("host_organization")),
                "host_organization_name": source_data.get("host_organization_name"),
                "type": source_data.get("type")
            }
        )

    def _save_work(self):
        data = self.json_data
        year_obj, _ = Year.objects.get_or_create(year=str(data.get("publication_year")))
        worktype_obj, _ = WorkType.objects.get_or_create(worktype=data.get("type"))
        oa_status_obj, _ = OAStatus.objects.get_or_create(oa_status=data.get("open_access", {}).get("oa_status") or "unknown")

        self.work_obj, _ = Work.objects.update_or_create(
            work_id=self._clean_id(data.get("id")),
            defaults={
                "doi": self._clean_id(data.get("doi")),
                "work_title": data.get("title"),
                "pubyear": year_obj,
                "worktype": worktype_obj,
                "cited_by_count": data.get("cited_by_count"),
                "primary_source": self.primary_source_obj,
                "is_oa": data.get("open_access", {}).get("is_oa"),
                "oa_status": oa_status_obj,
                "referenced_works_count": data.get("referenced_works_count")
            }
        )

    def _save_authorships(self):

        for auth in self.json_data.get("authorships", []):
            author_id = self._clean_id(auth.get("author", {}).get("id"))

            author_obj, _ = Author.objects.get_or_create(
                author_id=author_id
            )

            authorship_obj, _ = Authorship.objects.get_or_create(
                work=self.work_obj,
                author=author_obj,
                defaults={
                    "is_corresponding": auth.get("is_corresponding", False)
                }
            )

            for inst in auth.get("institutions", []):
                inst_obj, _ = Institution.objects.get_or_create(
                    institution_id=self._clean_id(inst.get("id")),
                    defaults={
                        "institution_name": inst.get("display_name"),
                        "country_code": inst.get("country_code") or ""
                    }
                )
                AuthorshipInstitution.objects.get_or_create(
                    authorship=authorship_obj,
                    institution=inst_obj
                )

    def _save_cited_by_year(self):
        for c in self.json_data.get("counts_by_year", []):
            year_obj, _ = Year.objects.get_or_create(year=str(c.get("year")))

            CitedByYear.objects.update_or_create(
                work=self.work_obj,
                year=year_obj,
                defaults={
                    "cited_count": c.get("cited_by_count")
                }
            )

    def _save_topics(self):
        topics = self.json_data.get("topics", [])
        work_topic_objs = []

        for t in topics:
            topic_id = self._clean_id(t.get("id"))
            topic_obj, _ = Topic.objects.get_or_create(
                topic_id=topic_id,
                defaults={
                    "topic_name": t.get("display_name"),
                    "subfield_name": t.get("subfield", {}).get("display_name", ""),
                    "field_name": t.get("field", {}).get("display_name", ""),
                    "domain_name": t.get("domain", {}).get("display_name", "")
                }
            )
            work_topic_objs.append(WorkTopic(
                work=self.work_obj,
                topic=topic_obj,
                score=t.get("score")
            ))
        WorkTopic.objects.bulk_create(work_topic_objs, ignore_conflicts=True)


