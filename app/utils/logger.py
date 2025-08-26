import os
import logging
import logging.config

DEFAULT_LOGGING_CONF = os.path.join(
    os.path.dirname(__file__), "..", "..", "logging.conf"
)


def setup_logging(
    default_path: str = DEFAULT_LOGGING_CONF,
    default_level: int = logging.INFO,
    env_key: str = "LOG_CFG",
):
    """
    Configura logging a partir de um arquivo logging.conf.
    Se não encontrar o arquivo, usa basicConfig.

    Args:
        default_path (str): caminho para logging.conf.
        default_level (int): nível de log padrão se o arquivo não existir.
        env_key (str): variável de ambiente opcional que pode sobrescrever o caminho.
    """
    path = os.getenv(env_key, default_path)
    if os.path.exists(path):
        logging.config.fileConfig(path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=default_level)
        logging.getLogger(__name__).warning(
            "Arquivo logging.conf não encontrado em %s, usando basicConfig().", path
        )

    noisy_loggers = [
        "autogen.io.base",
        "autogen.oai.client",
        "httpx",
    ]
    for nl in noisy_loggers:
        logging.getLogger(nl).setLevel(logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger configurado.

    Args:
        name (str): nome do logger (geralmente __name__ ou domínio do módulo).

    Returns:
        logging.Logger
    """
    return logging.getLogger(name)
