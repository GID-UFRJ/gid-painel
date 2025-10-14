# common/utils/cache.py

# Importamos 'wraps' do módulo 'functools'. A função 'wraps' é um decorador
# que usaremos para garantir que nossa função decorada mantenha sua identidade
# original (como o nome e a docstring), o que é crucial para depuração.
from functools import wraps

# Importamos o objeto 'cache' do Django. Este é o "controle remoto universal"
# que nos permite interagir com o sistema de cache, independentemente do backend
# que configuramos no settings.py (seja Redis, Memcached ou outro).
from django.core.cache import cache


# --- INÍCIO DA DEFINIÇÃO DO DECORADOR ---

# Esta é a função "fábrica" do nosso decorador. A chamamos com argumentos
# para configurar o comportamento do cache. Ela não decora a função diretamente,
# mas sim retorna o decorador que fará o trabalho.
def cache_context_data(key_prefix, timeout=3600):
    """
    Uma fábrica de decoradores para fazer cache do dicionário retornado por uma função.

    :param key_prefix: Um prefixo único para a chave de cache (ex: 'pessoal_ppg').
                       Isso evita que diferentes views colidam no cache.
    :param timeout: O tempo de expiração do cache em segundos. O padrão é 3600s (1 hora).
    """

    # 'decorator' é a função que o Python realmente usará como decorador.
    # Ela é executada apenas uma vez, quando o Python lê o arquivo, e sua única
    # responsabilidade é "capturar" a função que está sendo decorada (func).
    def decorator(func):
        """
        Este é o decorador real. Ele recebe a função a ser decorada (`func`)
        e a "envolve" com a lógica de cache definida na função 'wrapper'.
        """

        # '@wraps(func)' é aplicado à nossa função 'wrapper'. Ele copia os metadados
        # da função original ('func') para a 'wrapper'. Graças a isso, a função
        # decorada ainda pensará que se chama 'get_cached_context', e não 'wrapper'.
        @wraps(func)
        # 'wrapper' é a função que substituirá a original. Ela será executada
        # TODA VEZ que a função decorada for chamada.
        # '*args' e '**kwargs' permitem que esta 'wrapper' aceite QUALQUER
        # argumento que a função original aceitaria, tornando o decorador universal.
        def wrapper(*args, **kwargs):
            """
            Esta função 'wrapper' contém a lógica principal do cache.
            Ela intercepta a chamada à função original.
            """

            # --- ETAPA 1: CONSTRUIR UMA CHAVE DE CACHE ÚNICA E DINÂMICA ---

            # Converte todos os argumentos posicionais ('args') em uma lista de strings.
            # Converte todos os argumentos de palavra-chave ('kwargs') em uma lista de
            # strings no formato 'chave_valor'.
            # Ex: se a chamada for `funcao(227)`, arg_parts será ['227'].
            # Ex: se a chamada for `funcao(prog_id=227)`, arg_parts será ['prog_id_227'].
            arg_parts = list(map(str, args)) + [f'{k}_{v}' for k, v in kwargs.items()]

            # Junta todas as partes dos argumentos com um underscore para criar uma
            # "impressão digital" única para esta chamada específica.
            # Ex: 'prog_id_227'
            dynamic_part = '_'.join(arg_parts)
            
            # Monta a chave de cache final, combinando todas as partes.
            # Ela será única e legível, o que ajuda na depuração.
            # Exemplo final: 'ppg_detalhe:get_cached_context:prog_id_227'
            full_key = f"{key_prefix}:{func.__name__}:{dynamic_part}"
            
            # --- ETAPA 2: TENTAR BUSCAR OS DADOS DO CACHE ---

            # Usamos a API do Django para pedir ao Redis (ou outro backend)
            # se ele tem algum valor armazenado para esta chave.
            context = cache.get(full_key)
            
            # --- ETAPA 3: A LÓGICA PRINCIPAL - CACHE MISS OU CACHE HIT ---

            # Verificamos se o cache retornou algo. 'None' significa "não encontrei".
            # Este é o cenário de "CACHE MISS" (o caminho lento).
            if context is None:
                # Se não encontramos nada no cache, agora é a hora de fazer o trabalho pesado.
                # Executamos a função original ('func') que capturamos, passando
                # exatamente os mesmos argumentos que a 'wrapper' recebeu.
                context = func(*args, **kwargs)
                
                # Após o trabalho pesado ser feito, salvamos o resultado ('context')
                # no cache. Na próxima vez que esta função for chamada com os mesmos
                # argumentos, o 'cache.get()' acima encontrará este valor.
                cache.set(full_key, context, timeout=timeout)
            
            # Se 'context' não era 'None', significa que tivemos um "CACHE HIT".
            # O bloco 'if' inteiro foi pulado, e a função original 'func' NUNCA
            # foi executada, economizando tempo e processamento.

            # --- ETAPA 4: RETORNAR O RESULTADO ---

            # Retornamos o 'context', seja ele o valor que acabamos de buscar do cache
            # (rápido) ou o valor que acabamos de gerar e salvar (lento na primeira vez).
            return context

        # A função 'decorator' retorna a 'wrapper'. Agora, o nome da função original
        # (ex: 'get_cached_context') aponta para esta 'wrapper'.
        return wrapper

    # A função "fábrica" retorna o 'decorator' configurado.
    return decorator

# --- FIM DA DEFINIÇÃO DO DECORADOR ---