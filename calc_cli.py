# *** imports

from tiferet import App

# *** code

# Create an instance of the App class with the specified settings.
app = App(settings=dict(
    app_repo_module_path='tiferet.proxies.yaml.app',
    app_repo_class_name='AppYamlProxy',
    app_repo_params=dict(
        app_config_file='tiferet/configs/tests/test_calc.yml'
    )
))

# Load the CLI interface for the calculator.
calc_cli = app.load_interface('test_calc_cli')

# Run the CLI interface according to the provided arguments.
if __name__ == '__main__':
    calc_cli.run()
