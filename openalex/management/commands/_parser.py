from django.db import transaction
from openalex.models import Year, WorkType, OAStatus, PrimarySource, Work, Institution, Author, Authorship, AuthorshipInstitution, CitedByYear, Topic, WorkTopic, AuthorPosition

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

        # update_or_create para absorver correções da revista/fonte
        self.primary_source_obj, _ = PrimarySource.objects.update_or_create(
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

        # Imutáveis: get_or_create funciona bem aqui
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
                "referenced_works_count": data.get("referenced_works_count"),
                "fwci": data.get("fwci")
            }
        )

    #def _save_authorships(self):

    #    # Limpa as autorias antigas deste trabalho para evitar autores fantasmas
    #    # caso a OpenAlex tenha removido um autor erroneamente atribuído.
    #    Authorship.objects.filter(work=self.work_obj).delete()

    #    # Segurança para evitar autores duplicados no mesmo artigo
    #    seen_authors = set()

    #    for auth in self.json_data.get("authorships", []):
    #        author_id = self._clean_id(auth.get("author", {}).get("id"))

    #        # ========================================================================
    #        # DECISÃO ARQUITETURAL: Descarte de Autores sem ID
    #        # ------------------------------------------------------------------------
    #        # Como este é um painel gerencial (e não apenas um catálogo),
    #        # a rastreabilidade da entidade é estritamente necessária. 
    #        # A OpenAlex, apesar de ter muitas vantagens, peca na qualidade de parte 
    #        # dos metadados. Um exemplo disso são os autores sem ID.
    #        # Aceita-se a perda destas autorias específicas em troca de garantir 
    #        # 100% de confiabilidade, integridade referencial e performance no banco.
    #        # ========================================================================

    #        # Se a OpenAlex mandou um autor sem ID, ignoramos
    #        if not author_id:
    #            raw_name = auth.get("raw_author_name", "Desconhecido")
    #            print(f"⚠️ Aviso: Autor sem ID ignorado no trabalho {self.work_obj.work_id} (Nome bruto: {raw_name})") #Polui bastante a saída
    #            continue
    #            
    #        # Se a OpenAlex mandou o mesmo autor duplicado, ignoramos a duplicata
    #        if author_id in seen_authors:
    #            print(f"🔁 Aviso: Autor {author_id} duplicado no trabalho {self.work_obj.work_id}. Ignorando duplicata.") #Polui bastante a saída
    #            continue
    #        
    #        seen_authors.add(author_id)

    #        author_obj, _ = Author.objects.get_or_create(
    #            author_id=author_id
    #        )

    #        position_str = auth.get("author_position")
    #        position_obj = None
    #        if position_str:
    #            position_obj, _ = AuthorPosition.objects.get_or_create(position=position_str)

    #        authorship_obj = Authorship.objects.create(
    #            work=self.work_obj,
    #            author=author_obj,
    #            is_corresponding=auth.get("is_corresponding", False),
    #            author_position=position_obj
    #        )

    #        # update_or_create para absorver correções de nome e país
    #        for inst in auth.get("institutions", []):
    #            inst_obj, _ = Institution.objects.update_or_create(
    #                institution_id=self._clean_id(inst.get("id")),
    #                defaults={
    #                    "institution_name": inst.get("display_name"),
    #                    "country_code": inst.get("country_code") or None
    #                }
    #            )
    #            AuthorshipInstitution.objects.create(
    #                authorship=authorship_obj,
    #                institution=inst_obj
    #            )
    
    def _save_authorships(self):
        # Limpa as autorias antigas deste trabalho
        Authorship.objects.filter(work=self.work_obj).delete()

        authorships_data = self.json_data.get("authorships", [])
        if not authorships_data:
            return

        # Sets para evitar duplicações internas dentro do mesmo JSON
        seen_authors = set()
        seen_institutions = set()

        # Listas que segurarão os objetos instanciados apenas na memória
        authors_to_create = []
        positions_to_create = []
        institutions_to_create = []

        # Um mapa temporal para sabermos qual autor está ligado a qual instituição 
        # após os objetos serem salvos no banco de dados
        authorship_map = []

        for auth in authorships_data:
            author_id = self._clean_id(auth.get("author", {}).get("id"))

            if not author_id or author_id in seen_authors:
                # Mantemos a decisão arquitetural de ignorar autores sem ID ou duplicados
                continue
            
            seen_authors.add(author_id)

            # 1. Instancia o Autor (apenas na memória)
            authors_to_create.append(Author(author_id=author_id))

            # 2. Instancia a Posição
            position_str = auth.get("author_position")
            if position_str:
                positions_to_create.append(AuthorPosition(position=position_str))

            # 3. Instancia as Instituições vinculadas a este autor
            inst_ids_for_this_author = []
            for inst in auth.get("institutions", []):
                inst_id = self._clean_id(inst.get("id"))
                if inst_id:
                    if inst_id not in seen_institutions:
                        seen_institutions.add(inst_id)
                        institutions_to_create.append(
                            Institution(
                                institution_id=inst_id,
                                institution_name=inst.get("display_name"),
                                country_code=inst.get("country_code") or None
                            )
                        )
                    inst_ids_for_this_author.append(inst_id)

            # Guarda o "rascunho" dessa relação para usarmos no final
            authorship_map.append({
                'author_id': author_id,
                'is_corresponding': auth.get("is_corresponding", False),
                'position': position_str,
                'inst_ids': inst_ids_for_this_author
            })

        # =========================================================
        # FASE 1: BULK CREATE (Enviando tudo de uma vez para o BD)
        # =========================================================

        # O parâmetro 'ignore_conflicts=True' manda o Postgres ignorar 
        # silenciosamente as linhas que já existem (baseado nas restrições UNIQUE).
        if authors_to_create:
            Author.objects.bulk_create(authors_to_create, ignore_conflicts=True)

        if positions_to_create:
            AuthorPosition.objects.bulk_create(positions_to_create, ignore_conflicts=True)

        if institutions_to_create:
            # MAGIA DO POSTGRESQL + DJANGO: Substitui o 'update_or_create'.
            # Se a Instituição não existe, ele cria. Se existe, ele faz o 'update' apenas nos campos especificados.
            Institution.objects.bulk_create(
                institutions_to_create,
                update_conflicts=True,
                unique_fields=['institution_id'],
                update_fields=['institution_name', 'country_code']
            )

        # =========================================================
        # FASE 2: RECUPERAR OS OBJETOS PARA AS CHAVES ESTRANGEIRAS
        # =========================================================
    
        # Fazemos 1 QUERY por tabela com a cláusula IN para buscar todo mundo de uma vez
        authors_db = {
            a.author_id: a for a in Author.objects.filter(author_id__in=seen_authors)
        }
        positions_db = {
            p.position: p for p in AuthorPosition.objects.filter(position__in=[d['position'] for d in authorship_map if d['position']])
        }
        institutions_db = {
            i.institution_id: i for i in Institution.objects.filter(institution_id__in=seen_institutions)
        }

        # =========================================================
        # FASE 3: MONTAR E SALVAR AS TABELAS RELACIONAIS
        # =========================================================
    
        authorships_to_create = []

        for data in authorship_map:
            author_obj = authors_db.get(data['author_id'])
            if not author_obj:
                continue

            pos_obj = positions_db.get(data['position']) if data['position'] else None

            authorships_to_create.append(Authorship(
                work=self.work_obj,
                author=author_obj,
                is_corresponding=data['is_corresponding'],
                author_position=pos_obj
            ))

        # Salva as autorias de uma vez. No Postgres, o bulk_create retorna os IDs recém-criados!
        created_authorships = Authorship.objects.bulk_create(authorships_to_create)

        # Prepara a tabela associativa (AuthorshipInstitution)
        authorship_inst_to_create = []

        # Como a lista 'created_authorships' tem a exata mesma ordem da nossa 'authorship_map', 
        # podemos emparelhá-las (zip) para ligar as Instituições.
        for authorship_obj, data in zip(created_authorships, authorship_map):
            for inst_id in data['inst_ids']:
                inst_obj = institutions_db.get(inst_id)
                if inst_obj:
                    authorship_inst_to_create.append(AuthorshipInstitution(
                        authorship=authorship_obj,
                        institution=inst_obj
                    ))

        # Salva todas as relações Autor-Instituição de uma vez
        if authorship_inst_to_create:
            AuthorshipInstitution.objects.bulk_create(authorship_inst_to_create, ignore_conflicts=True)

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

        # Limpa os tópicos antigos deste trabalho para garantir fidelidade à API
        WorkTopic.objects.filter(work=self.work_obj).delete()

        topics = self.json_data.get("topics", [])
        work_topic_objs = []

        for t in topics:
            topic_id = self._clean_id(t.get("id"))

            # update_or_create para absorver mudanças de nomenclatura do tópico
            topic_obj, _ = Topic.objects.update_or_create(
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