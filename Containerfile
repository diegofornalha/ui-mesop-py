FROM registry.access.redhat.com/ubi8/python-312

# Definir diretório de trabalho
WORKDIR /ui-mesop-py

# Copiar arquivos do projeto Python (o contexto do Container deve ser o diretório `python`)
COPY ../.. /opt/app-root

USER root

# Instalar dependências de build do sistema e gerenciador de pacotes UV
RUN dnf -y update && dnf install -y gcc gcc-c++ \
 && pip install uv

# Definir variáveis de ambiente para uv:
# UV_COMPILE_BYTECODE=1: Compila arquivos Python para .pyc para inicialização mais rápida
# UV_LINK_MODE=copy: Garante que os arquivos sejam copiados, não linkados simbolicamente, o que pode evitar problemas
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Instalar dependências usando uv sync.
# --frozen: Garante que uv respeite o arquivo uv.lock
# --no-install-project: Impede a instalação do projeto em si nesta etapa
# --no-dev: Exclui dependências de desenvolvimento
# --mount=type=cache: Aproveita o cache de build do Docker para uv, acelerando builds repetidos
RUN --mount=type=cache,target=/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Instalar o projeto
RUN --mount=type=cache,target=/.cache/uv \
    uv sync --frozen --no-dev

# Permitir que usuário não-root acesse tudo em app-root
RUN chgrp -R root /opt/app-root/ && chmod -R g+rwx /opt/app-root/

# Expor porta padrão (altere se necessário)
EXPOSE 8888

USER 1001

# Executar o agente
CMD ["uv", "run", "main.py", "--host", "0.0.0.0"]