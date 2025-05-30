import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import traceback
import datetime
import json
import socket

class EnhancedLogger:
    """
    Enhanced logging module with:
    - Custom logging levels
    - Improved formatting with colors
    - Customizable file handlers with rotation
    - JSON formatting option
    - Context manager for tracking execution time
    """
    
    # Custom log levels
    TRACE = 5
    VERBOSE = 15
    SUCCESS = 25
    
    # ANSI color codes for terminal output
    COLORS = {
        'TRACE': '\033[38;5;8m',      # Gray
        'DEBUG': '\033[38;5;4m',      # Blue
        'VERBOSE': '\033[38;5;6m',    # Cyan
        'INFO': '\033[38;5;2m',       # Green
        'SUCCESS': '\033[38;5;10m',   # Bright Green
        'WARNING': '\033[38;5;3m',    # Yellow
        'ERROR': '\033[38;5;1m',      # Red
        'CRITICAL': '\033[48;5;1m\033[38;5;15m',  # White on Red background
        'RESET': '\033[0m'            # Reset
    }
    
    def __init__(self, name=None, level=logging.INFO, 
                 console=True, colored=True, 
                 file_path=r"C:\Users\u8064927\Desktop\Rolls-Royce X Ali\.coding\Normstelle\ChemScan\scripts\data", file_level=None,
                 json_format=False, hostname=False,
                 max_file_size=10*1024*1024, backup_count=5,
                 timed_rotation=False, rotation_when='midnight',
                 add_caller_info=True):
        """
        Initialize the enhanced logger.
        
        Args:
            name: Logger name (defaults to __name__ of caller)
            level: Console logging level
            console: Whether to log to console
            colored: Whether to use colored output in console
            file_path: Path for log file (if None, no file logging)
            file_level: Level for file logging (defaults to same as console)
            json_format: Whether to log in JSON format
            hostname: Whether to include hostname in log records
            max_file_size: Maximum file size before rotation (in bytes)
            backup_count: Number of backup files to keep
            timed_rotation: Whether to use time-based rotation instead of size-based
            rotation_when: When to rotate (if timed_rotation is True)
            add_caller_info: Whether to add detailed caller information
        """
        # Register custom log levels
        logging.addLevelName(self.TRACE, 'TRACE')
        logging.addLevelName(self.VERBOSE, 'VERBOSE')
        logging.addLevelName(self.SUCCESS, 'SUCCESS')
        
        # Use provided name or get from caller
        self.name = name if name else __name__
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.TRACE if hasattr(logging, 'TRACE') else self.TRACE)
        self.logger.handlers = []  # Clear any existing handlers
        
        self.colored = colored
        self.json_format = json_format
        self.hostname = socket.gethostname() if hostname else None
        self.add_caller_info = add_caller_info
        
        # Create formatters
        if json_format:
            self.formatter = self._create_json_formatter()
        else:
            self.console_formatter = self._create_console_formatter(colored)
            self.file_formatter = self._create_file_formatter()
        
        # Set up console handler
        if console:
            self._setup_console_handler(level)
        
        # Set up file handler
        if file_path:
            file_level = file_level if file_level is not None else level
            if timed_rotation:
                self._setup_timed_rotating_file_handler(file_path, file_level, rotation_when, backup_count)
            else:
                self._setup_rotating_file_handler(file_path, file_level, max_file_size, backup_count)
    
    def _create_console_formatter(self, colored):
        """Create formatter for console output."""
        if colored:
            format_str = '%(asctime)s - %(levelcolor)s%(levelname)s%(reset)s - %(message)s'
            if self.add_caller_info:
                format_str += ' [%(filename)s:%(lineno)d]'
            return ColoredFormatter(format_str, '%Y-%m-%d %H:%M:%S', self.COLORS)
        else:
            format_str = '%(asctime)s - %(levelname)s - %(message)s'
            if self.add_caller_info:
                format_str += ' [%(filename)s:%(lineno)d]'
            return logging.Formatter(format_str, '%Y-%m-%d %H:%M:%S')
    
    def _create_file_formatter(self):
        """Create formatter for file output."""
        format_str = '%(asctime)s - %(levelname)s - %(message)s'
        if self.hostname:
            format_str = f'%(asctime)s - {self.hostname} - %(levelname)s - %(message)s'
        if self.add_caller_info:
            format_str += ' - [%(filename)s:%(lineno)d:%(funcName)s]'
        return logging.Formatter(format_str, '%Y-%m-%d %H:%M:%S')
    
    def _create_json_formatter(self):
        """Create JSON formatter."""
        return JsonFormatter(hostname=self.hostname, add_caller_info=self.add_caller_info)
    
    def _setup_console_handler(self, level):
        """Set up console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(self.console_formatter if not self.json_format else self.formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_rotating_file_handler(self, file_path, level, max_size, backup_count):
        """Set up size-based rotating file handler."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        file_handler = RotatingFileHandler(
            file_path, maxBytes=max_size, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(self.file_formatter if not self.json_format else self.formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_timed_rotating_file_handler(self, file_path, level, when, backup_count):
        """Set up time-based rotating file handler."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            file_path, when=when, backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(self.file_formatter if not self.json_format else self.formatter)
        self.logger.addHandler(file_handler)
    
    def _get_caller_info(self, stacklevel=3):
        """Get caller information for better context."""
        frame = sys._getframe(stacklevel)
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name
        return {
            'filename': filename,
            'lineno': lineno,
            'funcName': func_name
        }
    
    # Custom level logging methods
    def trace(self, msg, *args, **kwargs):
        """Log at TRACE level (lower than DEBUG)."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.log(self.TRACE, msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        """Log at DEBUG level."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.debug(msg, *args, **kwargs)
    
    def verbose(self, msg, *args, **kwargs):
        """Log at VERBOSE level (between DEBUG and INFO)."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.log(self.VERBOSE, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """Log at INFO level."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.info(msg, *args, **kwargs)
    
    def success(self, msg, *args, **kwargs):
        """Log at SUCCESS level (between INFO and WARNING)."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.log(self.SUCCESS, msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """Log at WARNING level."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """Log at ERROR level."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        """Log at CRITICAL level."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg, *args, exc_info=True, **kwargs):
        """Log an exception with traceback."""
        if self.add_caller_info and 'extra' not in kwargs:
            kwargs['extra'] = self._get_caller_info()
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs)
    
    def log_exception(self, exc_type=None, exc_value=None, exc_traceback=None, level=logging.ERROR):
        """Log exception details more thoroughly."""
        if exc_type is None and exc_value is None and exc_traceback is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        if exc_type is not None:
            trace_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.log(level, f"Exception occurred:\n{trace_message}")
    
    class ExecutionTimer:
        """Context manager for timing code execution."""
        def __init__(self, logger, label="Execution time", level=logging.INFO):
            self.logger = logger
            self.label = label
            self.level = level
            self.start_time = None
        
        def __enter__(self):
            self.start_time = datetime.datetime.now()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = datetime.datetime.now()
            duration = end_time - self.start_time
            self.logger.log(self.level, f"{self.label}: {duration.total_seconds():.3f} seconds")
    
    def timer(self, label="Execution time", level=logging.INFO):
        """Create a context manager to measure and log execution time."""
        return self.ExecutionTimer(self.logger, label, level)


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to log levels for console output."""
    
    def __init__(self, fmt, datefmt, colors):
        super().__init__(fmt, datefmt)
        self.colors = colors
    
    def format(self, record):
        levelname = record.levelname
        if not hasattr(record, 'levelcolor'):
            record.levelcolor = self.colors.get(levelname, '')
        if not hasattr(record, 'reset'):
            record.reset = self.colors['RESET']
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """Formatter that outputs logs in JSON format."""
    
    def __init__(self, hostname=None, add_caller_info=True):
        super().__init__()
        self.hostname = hostname
        self.add_caller_info = add_caller_info
    
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record, '%Y-%m-%d %H:%M:%S'),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        
        if self.hostname:
            log_data['hostname'] = self.hostname
        
        if self.add_caller_info:
            log_data['file'] = record.filename if hasattr(record, 'filename') else None
            log_data['line'] = record.lineno if hasattr(record, 'lineno') else None
            log_data['function'] = record.funcName if hasattr(record, 'funcName') else None
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Example usage
def get_logger(name=None, **kwargs):
    """Helper function to get a configured logger."""
    return EnhancedLogger(name, **kwargs)


# Backward compatibility with standard logging
logging.TRACE = EnhancedLogger.TRACE
logging.VERBOSE = EnhancedLogger.VERBOSE
logging.SUCCESS = EnhancedLogger.SUCCESS

# Add methods to the logging module for backward compatibility
def trace(msg, *args, **kwargs):
    logging.log(logging.TRACE, msg, *args, **kwargs)

def verbose(msg, *args, **kwargs):
    logging.log(logging.VERBOSE, msg, *args, **kwargs)

def success(msg, *args, **kwargs):
    logging.log(logging.SUCCESS, msg, *args, **kwargs)

# Add the new methods to the logging module
logging.trace = trace
logging.verbose = verbose
logging.success = success