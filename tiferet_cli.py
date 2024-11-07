# *** imports

# ** app
from app.contexts import EnvironmentContext


# *** main

# ** function: main
def main():
    '''Main entry point for the Tiferet console application.'''

    # Load the environment context.
    env = EnvironmentContext()

    # Start the environment context.
    env.start(interface_id='cli')


# Run the main entry point.
if __name__ == '__main__':
    main()
