"""
Logger Configuration - Olist E-Commerce
----------------------------------------
Configuração centralizada de logging usando loguru.
Suporta console colorido, arquivos rotativos, e níveis customizados.

Autor: Andre Bomfim
Data: Outubro 2025
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
    colorize: bool = True,
    format_string: Optional[str] = None
) -> logger:
    """
    Configura o logger global do projeto
    
    Args:
        log_level: Nível de log (DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL)
        log_file: Caminho do arquivo de log (None = apenas console)
        rotation: Rotação de arquivo ("10 MB", "1 day", "1 week")
        retention: Tempo de retenção ("7 days", "1 month")
        colorize: Colorir output no console
        format_string: Formato customizado (None = usa padrão)
        
    Returns:
        Logger configurado
        
    Example:
        >>> from python.utils.logger import setup_logger
        >>> logger = setup_logger(log_level="DEBUG", log_file="logs/app.log")
        >>> logger.info("Aplicação iniciada")
    """
    
    # Remover handlers padrão
    logger.remove()
    
    # Formato padrão
    if format_string is None:
        if colorize:
            format_string = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            )
        else:
            format_string = (
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} - "
                "{message}"
            )
    
    # Handler para console
    logger.add(
        sys.stderr,
        format=format_string,
        level=log_level,
        colorize=colorize,
        backtrace=True,
        diagnose=True
    )
    
    # Handler para arquivo (se especificado)
    if log_file:
        # Criar diretório se não existir
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format=format_string,
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        logger.info(f"Logger configurado - arquivo: {log_file}")
    
    logger.info(f"Logger configurado - nível: {log_level}")
    
    return logger


def get_logger(name: str = __name__) -> logger:
    """
    Obtém uma instância do logger com contexto
    
    Args:
        name: Nome do módulo/contexto
        
    Returns:
        Logger com contexto
        
    Example:
        >>> from python.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processando dados...")
    """
    return logger.bind(name=name)


def setup_etl_logger() -> logger:
    """
    Configuração específica para ETL
    
    Returns:
        Logger configurado para ETL
    """
    return setup_logger(
        log_level="INFO",
        log_file="logs/etl.log",
        rotation="50 MB",
        retention="30 days"
    )


def setup_analytics_logger() -> logger:
    """
    Configuração específica para Analytics
    
    Returns:
        Logger configurado para Analytics
    """
    return setup_logger(
        log_level="INFO",
        log_file="logs/analytics.log",
        rotation="20 MB",
        retention="14 days"
    )


def setup_debug_logger() -> logger:
    """
    Configuração para debug (verbose)
    
    Returns:
        Logger em modo debug
    """
    return setup_logger(
        log_level="DEBUG",
        log_file="logs/debug.log",
        rotation="100 MB",
        retention="3 days"
    )


class LoggerContext:
    """Context manager para logging temporário com nível diferente"""
    
    def __init__(self, level: str = "DEBUG"):
        """
        Inicializa context manager
        
        Args:
            level: Nível temporário de log
        """
        self.level = level
        self.handler_id = None
    
    def __enter__(self):
        """Entra no contexto"""
        logger.remove()
        self.handler_id = logger.add(
            sys.stderr,
            level=self.level,
            format="<level>{level: <8}</level> | <level>{message}</level>"
        )
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sai do contexto"""
        if self.handler_id is not None:
            logger.remove(self.handler_id)


def log_execution_time(func):
    """
    Decorator para logar tempo de execução de função
    
    Example:
        >>> from python.utils.logger import log_execution_time
        >>> @log_execution_time
        >>> def process_data():
        >>>     # processing...
        >>>     pass
    """
    from functools import wraps
    import time
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Iniciando: {func.__name__}")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.success(
                f"✓ Concluído: {func.__name__} "
                f"(tempo: {elapsed_time:.2f}s)"
            )
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(
                f"✗ Erro em: {func.__name__} "
                f"(tempo: {elapsed_time:.2f}s) - {str(e)}"
            )
            raise
    
    return wrapper


def log_function_call(func):
    """
    Decorator para logar chamadas de função com argumentos
    
    Example:
        >>> from python.utils.logger import log_function_call
        >>> @log_function_call
        >>> def calculate_ltv(customer_id):
        >>>     # calculation...
        >>>     pass
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        logger.debug(f"Chamando: {func.__name__}({signature})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Retorno: {func.__name__} -> {result!r}")
            return result
        except Exception as e:
            logger.error(f"Exceção em: {func.__name__} - {str(e)}")
            raise
    
    return wrapper


# Aliases convenientes
def log_info(message: str):
    """Atalho para logger.info"""
    logger.info(message)


def log_success(message: str):
    """Atalho para logger.success"""
    logger.success(message)


def log_warning(message: str):
    """Atalho para logger.warning"""
    logger.warning(message)


def log_error(message: str):
    """Atalho para logger.error"""
    logger.error(message)


def log_debug(message: str):
    """Atalho para logger.debug"""
    logger.debug(message)


def log_critical(message: str):
    """Atalho para logger.critical"""
    logger.critical(message)


# Configuração padrão ao importar
# Pode ser sobrescrita chamando setup_logger() novamente
_default_logger = setup_logger(
    log_level="INFO",
    colorize=True
)


if __name__ == "__main__":
    """Testes do logger"""
    
    # Configurar logger
    logger = setup_logger(
        log_level="DEBUG",
        log_file="logs/test.log"
    )
    
    # Testar níveis
    logger.debug("Mensagem de DEBUG")
    logger.info("Mensagem de INFO")
    logger.success("Mensagem de SUCCESS ✓")
    logger.warning("Mensagem de WARNING ⚠️")
    logger.error("Mensagem de ERROR ✗")
    
    # Testar decorator
    @log_execution_time
    def exemplo_funcao():
        import time
        time.sleep(0.5)
        return "resultado"
    
    resultado = exemplo_funcao()
    
    # Testar context manager
    with LoggerContext("DEBUG"):
        logger.debug("Dentro do contexto DEBUG")
    
    logger.info("Fora do contexto")
    
    print("\n✓ Testes concluídos. Veja logs/test.log")