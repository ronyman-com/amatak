#!/usr/bin/env python3
"""Amatak Language Daemon Process"""

import sys
import os
import time
import signal
import logging
from typing import Optional
from daemon import DaemonContext
from pid import PidFile
from amatak.runtime import AMatakRuntime
from amatak.errors import AmatakError

# Configuration
PID_FILE = '/var/run/amatakd.pid'
LOG_FILE = '/var/log/amatakd.log'
WORKING_DIR = '/'

class AmatakDaemon:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.runtime = AMatakRuntime(debug=debug)
        self.running = False
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure logging for the daemon"""
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.DEBUG if self.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('amatakd')

    def handle_signal(self, signum, frame) -> None:
        """Handle system signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def run(self) -> None:
        """Main daemon execution loop"""
        self.running = True
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        self.logger.info("Amatak daemon started")
        
        try:
            while self.running:
                # Main processing loop
                self.process_requests()
                time.sleep(0.1)  # Prevent CPU overload
        except Exception as e:
            self.logger.error(f"Daemon error: {str(e)}")
            raise
        finally:
            self.logger.info("Amatak daemon stopped")

    def process_requests(self) -> None:
        """Process incoming requests"""
        # TODO: Implement actual request processing
        pass

def start_daemon(debug: bool = False) -> None:
    """Start the daemon process"""
    daemon = AmatakDaemon(debug=debug)
    context = DaemonContext(
        working_directory=WORKING_DIR,
        pidfile=PidFile(PID_FILE),
        umask=0o002,
        stdout=sys.stdout if debug else None,
        stderr=sys.stderr if debug else None,
    )

    with context:
        daemon.run()

def stop_daemon() -> None:
    """Stop the running daemon process"""
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read())
        os.kill(pid, signal.SIGTERM)
        print("Daemon stopped successfully")
    except FileNotFoundError:
        print("Daemon not running (no PID file found)")
    except ProcessLookupError:
        print("Daemon not running (process not found)")
        os.remove(PID_FILE)
    except Exception as e:
        print(f"Error stopping daemon: {str(e)}")

def daemon_status() -> bool:
    """Check if daemon is running"""
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read())
        os.kill(pid, 0)  # Check if process exists
        print("Daemon is running (pid: {pid})")
        return True
    except (FileNotFoundError, ProcessLookupError):
        print("Daemon is not running")
        return False
    except Exception as e:
        print(f"Error checking daemon status: {str(e)}")
        return False

def print_usage() -> None:
    """Print command usage information"""
    print("""Amatak Language Daemon

Usage: amatakd [command]

Commands:
  start     Start the daemon
  stop      Stop the daemon
  restart   Restart the daemon
  status    Check daemon status
  help      Show this help message

Options:
  --debug   Enable debug output
""")

def main() -> None:
    """Main entry point for the daemon CLI"""
    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_usage()
        sys.exit(0)

    debug = '--debug' in sys.argv
    command = sys.argv[1]

    try:
        if command == 'start':
            start_daemon(debug)
        elif command == 'stop':
            stop_daemon()
        elif command == 'restart':
            stop_daemon()
            time.sleep(1)  # Give time for shutdown
            start_daemon(debug)
        elif command == 'status':
            daemon_status()
        else:
            raise AmatakError(f"Unknown command: {command}")
    except AmatakError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        print_usage()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()