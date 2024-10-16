from typing import Dict, Any

from app.contexts import EnvironmentContext

# Define the base key for the application environment variables.
APP_ENV_BASE_KEY = 'TIFERET'


def main():
    '''Main entry point for the Tiferet console application.'''

    # Load the environment context.
    EnvironmentContext(
        env_base_key=APP_ENV_BASE_KEY)


if __name__ == '__main__':
    main()
