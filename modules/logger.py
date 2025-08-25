import logging

def run(log_name='app_logger', log_file='app.log', level=logging.INFO):
    """
    Logger yapılandırmasını yapar.
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(level)

    # Eğer daha önce handler eklenmişse temizle
    if logger.hasHandlers():
        logger.handlers.clear()

    # Dosya handler'ı
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Console handler'ı
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Handler'ları ekle
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Logger objesini oluştur
logger = run()

# Örnek kullanım
def perform_task():
    logger.debug("Bu bir debug mesajıdır.")
    logger.info("Bu bir bilgi mesajıdır.")
    logger.warning("Bu bir uyarı mesajıdır.")
    logger.error("Bu bir hata mesajıdır.")
    logger.critical("Bu bir kritik mesajdır.")

# Test
perform_task()
