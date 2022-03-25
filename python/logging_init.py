import logging


def generate_logging(log_name: str = "Hovedlogger", log_file_name: str="Hovedlogg.log"):
    logging.basicConfig(level=logging.DEBUG, filename=log_file_name, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S' ) #setter hovedloggeren til det laveste nivået
    main_logger = logging.getLogger(log_name)
    # Setter opp fil logging med format som vist under
    #f_handler = logging.FileHandler(log_file_name)
    #f_handler.setLevel(logging.NOTSET)
    #f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #f_handler.setFormatter(f_format)
    #main_logger.addHandler(f_handler)
    
    # Setter opp shell logging med format som vist under
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%d/%m/%Y %H:%M:%S' )
    c_handler.setFormatter(c_format)
    main_logger.addHandler(c_handler)
    

    return main_logger