from schematics.transforms import wholelist, whitelist, blacklist

from ..objects.sync import *
from ..objects.data import ModelData


class CodeBlockData(ModelData, CodeBlock):
    '''
    A data representation of a code block.
    '''

    class Options():
        '''
        The options for the code block data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the code block data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }

    def map(self, role: str = 'to_object', **kwargs) -> CodeBlock:
        '''
        Maps the code block data to a code block object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new code block object.
        :rtype: CodeBlockData
        '''

        # Map the code block data to a code block object.
        return super().map(CodeBlock, role, **kwargs)
    
    def to_primitive(self, role=None, app_data=None, tab: int = 0, **kwargs):
        '''
        Converts the code block data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param tab: The tab level for the code block.
        :type tab: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Create the results list.
        results = []

        # Add the comments if they are present.
        if self.comments:
            results.extend([TAB*tab + comment for comment in self.comments])

        # Add the lines if they are present.
        if self.lines:
            results.extend([TAB*tab + line for line in self.lines])

        # Return the results.
        return results
    

class ImportData(ModelData, Import):
    '''
    A data representation of an import.
    '''

    class Options():
        '''
        The options for the import data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the import data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }

    def map(self, role: str = 'to_object', **kwargs) -> Import:
        '''
        Maps the import data to an import object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new import object.
        :rtype: ImportData
        '''

        # Map the import data to an import object.
        return super().map(Import, role, **kwargs)

    def to_primitive(self, role=None, app_data=None, **kwargs) -> List[str]:
        '''
        Converts the import data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: List[str]
        '''

        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Start the result as a string import statement.
        result = f'import {self.import_module}'

        # If the import has a from module, add it to the result.
        if self.from_module:
            result = f'from {self.from_module} {result}'

        # If the import has an alias, add it to the result.
        if self.alias:
            result = f'{result} as {self.alias}'

        # Return the result.
        return result
    

class CodeComponentData(ModelData, CodeComponent):
    '''
    A data representation of a code component.
    '''

    class Options():
        '''
        The options for the code component data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the code component data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }

    def map(self, role: str = 'to_object', **kwargs) -> CodeComponent:

        # Map the code component data to a code component object.
        return super().map(CodeComponent, role, **kwargs)
    

class VariableData(CodeComponentData, Variable):
    '''
    A data representation of a variable.
    '''

    class Options():
        '''
        The options for the variable data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the variable data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }
    
    @staticmethod
    def new(**kwargs) -> 'VariableData':
        '''
        Initializes a new VariableData object from a Variable object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new VariableData object.
        :rtype: VariableData
        '''

        # Create the variable data.
        _variable = VariableData(
            dict(**kwargs), 
            strict=False
        )

        # Validate and return the variable data.
        _variable.validate()
        return

    def map(self, role: str = 'to_object', **kwargs) -> Variable:
        '''
        Maps the variable data to a variable object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new variable object.
        :rtype: VariableData
        '''

        # Map the variable data to a variable object.
        return super().map(Variable, role, **kwargs)

    def to_primitive(self, role=None, app_data=None, **kwargs):
        '''
        Converts the variable data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Set the result as the name.
        result = self.name

        # Add the type to the result if it exists.
        if self.type:
            result = f'{result} = {self.type}'
        
        # Add the value to the result.
        f'{result} = {self.value}'

        # Return the result as a list.
        return [result]


class ParameterData(ModelData, Parameter):
    '''
    A data representation of a parameter.
    '''

    class Options():
        '''
        The options for the parameter data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the parameter data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }

    def map(self, role: str = 'to_object', **kwargs) -> Parameter:
        '''
        Maps the parameter data to a parameter object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new parameter object.
        :rtype: ParameterData
        '''

        # Map the parameter data to a parameter object.
        return super().map(Parameter, role, **kwargs)
    
    def to_primitive(self, role=None, app_data=None, **kwargs):
        '''
        Converts the parameter data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Set the result as the name.
        result = self.name

        # Add the type to the result if it exists.
        if self.type:
            result = f'{result}: {self.type}'
        
        # Add the value to the result and return it.
        f'{result} = {self.value}'
        return result


class FunctionData(CodeComponentData, Function):
    '''
    A data representation of a function.
    '''

    class Options():
        '''
        The options for the function data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the function data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }
    
    parameters = t.ListType(
        t.ModelType(ParameterData),
        default=[],
        metadata=dict(
            description='The function parameters.'
        ),
    )

    @staticmethod
    def new(**kwargs) -> 'FunctionData':
        '''
        Initializes a new FunctionData object from a Function object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new FunctionData object.
        :rtype: FunctionData
        '''

        # Create the function data.
        _function = FunctionData(
            dict(**kwargs), 
            strict=False
        )

        # Validate and return the function data.
        _function.validate()
        return _function
    
    def map(self, role: str = 'to_object', **kwargs) -> Function:
        '''
        Maps the function data to a function object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new function object.
        :rtype: FunctionData
        '''

        # Map the function data to a function object.
        return super().map(Function, role, **kwargs)
    
    def to_primitive(self, role=None, app_data=None, **kwargs):
        '''
        Converts the function data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        '''

        # If the role is not to_data.python, return the default primitive.
        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)
        
        # Initialize the result as the function name.
        result = f'def {self.name}('

        # Add the parameters to the result.
        result = f'{result}{", ".join([parameter.to_primitive(role, app_data, **kwargs) for parameter in self.parameters])})'

        # Add the return type to the result if it exists.
        if self.return_type:
            result = f'{result} -> {self.return_type}:'
        else:
            result = f'{result}:'

        # Set the result as a list.
        result = [result]

        # Add the code block to the result.
        result.extend([code.to_primitive(role, tab=1) for code in self.code_block])


class ClassData(CodeComponentData, Class):
    '''
    A data representation of a class.
    '''

    class Options():
        '''
        The options for the class data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the class data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }

    attributes = t.ListType(
        t.ModelType(VariableData),
        default=[],
        metadata=dict(
            description='The class attributes.'
        ),
    )

    methods = t.ListType(
        t.ModelType(FunctionData),
        default=[],
        metadata=dict(
            description='The class methods.'
        ),
    )

    @staticmethod
    def new(**kwargs) -> 'ClassData':
        '''
        Initializes a new ClassData object from a Class object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ClassData object.
        :rtype: ClassData
        '''

        # Create the class data.
        _class = ClassData(
            dict(**kwargs), 
            strict=False
        )

        # Validate and return the class data.
        _class.validate()
        return _class

    def map(self, role: str = 'to_object', **kwargs) -> Class:
        '''
        Maps the class data to a class object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new class object.
        :rtype: ClassData
        '''

        # Map the class data to a class object.
        return super().map(Class, role, **kwargs)
    
    def to_primitive(self, role=None, app_data=None, **kwargs):
        '''
        Converts the class data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Initialize the result as the class name.
        result = f'class {self.name}'

        # Add the base classes to the result if they exist.
        if self.base_classes:
            result = f'{result}({", ".join(self.base_classes)}):'
        else:
            result = f'{result}(object):'

        # Set the result as a list.
        result = [result]
        result.append(f'{TAB}\'\'\'')
        result.append(f'{TAB}{self.description}')
        result.append(f'{TAB}\'\'\'')
        

        # Return the result if there are no attributes or methods.
        if not self.attributes and not self.methods:
            result.append('')
            result.append(f'{TAB}pass')
            return result

        # Add the attributes to the result.
        if self.attributes:
            result.append('')
        for attribute in self.attributes:
            result.extend([f'{TAB}{line}' for line in attribute.to_primitive(role, app_data, **kwargs)])
            

        # Add the methods to the result.
        if self.methods:
            result.append('')
        for method in self.methods:
            result.extend([f'{TAB}{line}' for line in method.to_primitive(role, app_data, **kwargs)])

        # Return the result.
        return result


class ModuleData(ModelData, Module):
    '''
    A data representation of a module.
    '''

    class Options():
        '''
        The options for the module data.
        '''

        # Set the serialize when none flag to false.
        serialize_when_none = False

        # Define the roles for the module data.
        roles = {
            'to_object': wholelist(),
            'to_data.python': wholelist()
        }

    id = t.StringType(
        metadata=dict(
            description='The module file name placeholder.'
        ),
    )

    type = t.StringType(
        metadata=dict(
            description='The module type placeholder.'
        ),
    )

    imports = t.ListType(
        t.ModelType(ImportData),
        default=[],
        metadata=dict(
            description='The imports for the module.'
        ),
    )

    components = t.ListType(
        t.ModelType(CodeComponentData),
        default=[],
        metadata=dict(
            description='The components of the module.'
        ),
    )

    @staticmethod
    def new(components: List[CodeComponent], **kwargs) -> 'ModuleData':
        '''
        Initializes a new ModuleData object from a Module object.

        :param components: The components for the module.
        :type components: List[CodeComponent]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ModuleData object.
        :rtype: ModuleData
        '''

        # Create the Data object for each component.
        _components = []
        for component in components:
            if isinstance(component, Variable):
                _components.append(VariableData.new(**component.to_primitive()))
            elif isinstance(component, Function):
                _components.append(FunctionData.new(**component.to_primitive()))
            elif isinstance(component, Class):
                _components.append(ClassData.new(**component.to_primitive()))

        # Create the module.
        _module = ModuleData(
            dict(**kwargs,
                components=_components
            ), 
            strict=False
        )

        # Validate and return the module.
        _module.validate()
        return _module

    @staticmethod
    def from_python_file(lines: List[str], **kwargs) -> 'ModuleData':
        '''
        Creates a module data from a Python file.
        '''

        pass

    def map(self, role: str = 'to_object', **kwargs) -> Module:
        '''
        Maps the module data to a module data.

        :param role: The role for the mapping.
        :type role: str
        :param kwargs: Additional keyword arguments for mapping.
        :type kwargs: dict
        :return: A new module data.
        :rtype: ModuleData
        '''

        # Map the module data to a module data.
        return super().map(Module, role, **kwargs)

    def to_primitive(self, role=None, app_data=None, **kwargs):
        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Initialize and add the imports and components to the result.
        result = []
        
        # Create lookup of core, infra, and app imports.
        core_imports = []
        infra_imports = []
        app_imports = []

        # Add the imports to the result.
        for _import in self.imports:
            if _import.type == 'core':
                core_imports.append(_import.to_primitive(role=role))
            elif _import.type == 'infra':
                infra_imports.append(_import.to_primitive(role=role))
            else:
                app_imports.append(_import.to_primitive(role=role))

        # Add the imports to the result.
        if core_imports:
            result.extend(core_imports)
            result.append('')
        if infra_imports:    
            result.extend(infra_imports)
            result.append('')
        if app_imports:
            result.extend(app_imports)
            result.append('')
        result.append('')

        for component in self.components:
            result.extend([line for line in component.to_primitive(role, app_data, **kwargs)])
            result.append('')

        # Return the result.
        return result
