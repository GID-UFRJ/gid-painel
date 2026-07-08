import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = 'Exporta o banco de dados PostgreSQL no formato exato para upload no Zenodo, excluindo dados sensíveis.'

    def add_arguments(self, parser):
        # Permite passar o nome do arquivo, mas já deixa o padronizado
        parser.add_argument(
            '--output',
            type=str,
            default='gid_db.dump',
            help='Nome ou caminho do arquivo de saída (padrão: gid_db.dump)'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        # Puxa as credenciais diretamente do seu settings.py
        db_settings = settings.DATABASES['default']
        
        # Garante que estamos usando PostgreSQL
        if 'postgresql' not in db_settings['ENGINE']:
            raise CommandError("Este comando foi construído especificamente para PostgreSQL.")

        db_user = db_settings.get('USER')
        db_password = db_settings.get('PASSWORD')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = str(db_settings.get('PORT', '5432'))
        db_name = db_settings.get('NAME')

        # Constrói o comando do pg_dump que combinamos (usando -f em vez de > para o subprocess)
        comando = [
            'pg_dump',
            '-U', db_user,
            '-h', db_host,
            '-p', db_port,
            '-d', db_name,
            '-Fc',                   # Formato custom/comprimido
            '--no-privileges'        # Remove os privilégios (GRANT/REVOKE)
            '-T', 'auth_*',          # Exclui usuários e senhas
            '-T', 'django_session',  # Exclui sessões ativas
            '-T', 'django_admin_log',# Exclui histórico de auditoria do admin
            '-T', 'django_content_type', # Exclui registro de models (evita erro de dependência no pg_restore --clean)
            '-f', output_file        # Arquivo de saída
        ]

        # Segurança: Passa a senha do banco como variável de ambiente do sistema operacional,
        # em vez de deixá-la visível na string do comando.
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password

        self.stdout.write(self.style.WARNING(f'Iniciando exportação para {output_file}...'))

        try:
            # Executa o comando no terminal do sistema
            subprocess.run(comando, env=env, check=True)
            self.stdout.write(self.style.SUCCESS(f'✅ Sucesso! Banco de dados exportado: {output_file}'))
            
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Erro fatal durante a execução do pg_dump: {e}')
        except FileNotFoundError:
            raise CommandError('Utilitário pg_dump não encontrado. Certifique-se de estar rodando isso dentro do contêiner onde o cliente PostgreSQL está instalado.')