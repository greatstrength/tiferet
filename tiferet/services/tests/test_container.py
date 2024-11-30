from ...services import container_service

def test_import_dependency():
    '''
    Test the import_dependency function.
    '''
    # Import dependency.
    dependency = container_service.import_dependency('tiferet.contexts.app', 'AppInterfaceContext')
    assert dependency.__name__ == 'AppInterfaceContext'


def test_create_injector():

    class Dependency1:
        
        def __init__(self, dependency1: str):
            self.dependency1 = dependency1

    class Dependency2:

        def __init__(self, dep_obj1: Dependency1, dependency2: str):
            self.dep_obj1 = dep_obj1
            self.dependency2 = dependency2

    # Create injector.
    injector = container_service.create_injector(
        'test',
        dependency1='dependency1',
        dependency2='dependency2',
        dep_obj1=Dependency1,
        dep_obj2=Dependency2,
    )

    # Get dependencies.
    dep_obj2 = getattr(injector, 'dep_obj2')

    # Check dependencies.
    assert dep_obj2.dep_obj1.dependency1 == 'dependency1'
    assert dep_obj2.dependency2 == 'dependency2'