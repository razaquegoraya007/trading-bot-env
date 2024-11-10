import logging
import os

# Set up the logging configuration
log_file_path = os.path.join(os.path.dirname(__file__), '../../data/trade_log.txt')
logging.basicConfig(
    filename=log_file_path,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def log_trade(signal, decision, execution_price):
    """Logs trade signal, decision, and execution details."""
    logging.info(f"Signal: {signal}, Decision: {decision}, Execution Price: {execution_price}")
