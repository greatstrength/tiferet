import re

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

    @staticmethod
    def from_python_file(line: str, type: str, **kwargs) -> 'ImportData':

        # Pull out alias statement if any.
        alias = None
        line = line.split(' as ')
        if len(line) == 2:
            alias = line[1].strip()

        # Pull out import statement.
        line = line[0].split('import ')
        import_module = line[1].strip()

        # Pull out from statement if any.
        from_module = None
        line = line[0].split('from ')
        if len(line) == 2:
            from_module = line[1].strip()

        # Create the import data.
        _data = ImportData(
            dict(**kwargs,
                 import_module=import_module,
                 from_module=from_module,
                 alias=alias,
                 type=type
                 ),
            strict=False
        )

        # Validate and return the import data.
        _data.validate()
        return _data

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

    @staticmethod
    def from_python_file(lines: List[str], var_type: str = None, **kwargs) -> 'VariableData':
        '''
        Creates a variable data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new variable data.
        :rtype: VariableData
        '''

        # Get the first line of the variable.
        line = lines[0]

        # Split on the equals sign.
        line = line.split('=')

        # Set the value to None if there is no equals sign.
        if len(line) == 1:
            value = None

        # Set the value to the right side of the equals sign if the type is None.
        elif not var_type:
            value = line[1].strip()

        # Split the name and the type
        line = line[0].split(':')

        # Set the name and type.
        name = line[0].strip()
        type = line[1].strip() if len(line) == 2 else None

        # Create the variable data.
        _variable = VariableData(
            dict(**kwargs,
                 name=name,
                 type=type,
                 value=value
                 ),
            strict=False
        )

        # Validate and return the variable data.
        _variable.validate()
        return _variable

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
            result = f'{result}: {self.type}'

        # Split the value on the newline character.
        value = self.value.split('\n')

        # If the value is not a list, add it to the result and convert the result to a list.
        if len(value) == 1:
            result = f'{result} = {value[0]}'
            return [result]
        
        # Add the first line of the value to the result.
        result = f'{result} = {value[0]}'

        # Add the rest of the value to the result and return it.
        return [result, *[f'{value}' for value in value[1:]]]


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
        result.extend([code.to_primitive(role, tab=1)
                      for code in self.code_block])


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

    @staticmethod
    def from_python_file(lines: List[str], **kwargs) -> 'ClassData':
        '''
        Creates a class data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new class data.
        :rtype: ClassData
        '''

        # Get the first line of the class.
        line = lines[0]

        # Split on the open parenthesis.
        line = line.split('(')

        # Set the name and base classes.
        name = line[0].split('class ')[1].strip()
        base_classes = line[1].split(')')[0].split(
            ',') if len(line) == 2 else []

        # Set the description.
        if lines[1].startswith(f'{TAB}\'\'\''):
            description = lines[2].strip()

        # Create the class data.
        _class = ClassData(
            dict(**kwargs,
                 name=name,
                 base_classes=base_classes,
                 description=description
                 ),
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
        return Class.new(**self.to_primitive(role, **kwargs))

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

        # Initialize the result as a list.
        result = []

        # Add the class to the result.
        first_line = f'class {self.name}'
        if self.base_classes:
            first_line = f'{first_line}({", ".join(self.base_classes)}):'
        else:
            first_line = f'{first_line}(object):'
        result.append(first_line)

        # Set the description.
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
            result.append(f'{TAB}#** attribute - {attribute.name}')
            result.extend(
                [f'{TAB}{line}' for line in attribute.to_primitive(role, app_data, **kwargs)])

        # Add the methods to the result.
        if self.methods:
            result.append('')
        for method in self.methods:
            result.append(f'{TAB}#** method - {method.name}')
            result.extend(
                [f'{TAB}{line}' for line in method.to_primitive(role, app_data, **kwargs)])

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
                _components.append(VariableData.new(
                    **component.to_primitive()))
            elif isinstance(component, Function):
                _components.append(FunctionData.new(
                    **component.to_primitive()))
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

        # Create a lookup of module code.
        module_code = {}

        # Current code marker.
        code_marker = None

        # Iterate over the lines.
        for i, line in enumerate(lines):

            # Skip the first line if it is empty.
            if i == 0 and not line:
                continue

            # If the line is a comment, add it to the module code.
            if line.startswith('#**'):

                # Set the code marker.
                code_marker = line[3:].strip()
                module_code[code_marker] = []

            # If the line is not a comment, add it to the module code.
            else:
                module_code[code_marker].append(line)

        # Create imports and components list.
        imports = []
        components = []

        for key, value in module_code.items():

            # Create the imports if present.
            if 'imports' in key:
                type = key.split(' - ')[1]
                imports.extend([ImportData.from_python_file(line, type)
                               for line in value if line])

            # Create the variable components if present.
            elif 'variable' in key:
                components.append(VariableData.from_python_file(value, type))

            # Create the function components if present.
            elif 'function' in key:
                components.append(FunctionData.from_python_file(value))

            # Create the class components if present.
            elif 'class' in key:
                components.append(ClassData.from_python_file(value))

        # Create the module data.
        _data = ModuleData(
            dict(**kwargs,
                 imports=imports,
                 components=components
                 ),
            strict=False
        )

        # Validate and return the module data.
        _data.validate()
        return _data

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
        _object = super().map(Module, role, **kwargs)

        # Set the components as the mapped components.
        _object.components = [component.map(role, **kwargs) for component in self.components]

        # Return the mapped module data.
        return _object

    def to_primitive(self, role=None, app_data=None, **kwargs):
        '''
        Converts the module data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param app_data: The application data.
        :type app_data: dict
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        # If the role is not to_data.python, return the default primitive.
        if role != 'to_data.python':
            return super().to_primitive(role, app_data, **kwargs)

        # Initialize and add the imports and components to the result.
        result = []

        # Create lookup of core, infra, and app imports.
        lookup = dict(
            core=[],
            infra=[],
            app=[]
        )

        # Add the imports to the result.
        for _import in self.imports:
            lookup[_import.type].append(_import.to_primitive(role=role))

        # Add the imports to the result.
        for type in ['core', 'infra', 'app']:
            imports = lookup[type]
            if imports:
                result.append(f'#** imports - {type}')
                result.extend(imports)
                result.append('')
        result.append('')

        # Add the components to the result.
        for component in self.components:
            if isinstance(component, Variable):
                result.append(f'#** variable - {component.name}')
            elif isinstance(component, Function):
                result.append(f'#** function - {component.name}')
            elif isinstance(component, Class):
                result.append(f'#** class - {component.name}')
            result.extend(
                [line for line in component.to_primitive(role, app_data, **kwargs)])
            result.append('')

        # Return the result.
        return result
