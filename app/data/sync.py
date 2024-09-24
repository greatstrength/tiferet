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

    @staticmethod
    def new(**kwargs) -> 'CodeBlockData':
        '''
        Initializes a new CodeBlockData object from a CodeBlock object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new CodeBlockData object.
        :rtype: CodeBlockData
        '''

        # Create the code block data.
        return CodeBlockData(
            super(CodeBlockData, CodeBlockData).new(**kwargs),
        )

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

    def to_primitive(self, role=None, app_data=None, **kwargs):
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

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive(**kwargs)

        # Return the default primitive.
        return super().to_primitive(role, app_data, **kwargs)

    def to_python_primitive(self, tabs: int = 0, **kwargs):
        '''
        Converts the code block data to a python source code-based primitive.
        '''

        # Initialize the result a list.
        result = ''.join([
            '\n'.join(
                f'# {comment}' for comment in self.comments) if self.comments else '',
            '\n' if self.comments and self.lines else '',
            '\n'.join(self.lines) if self.lines else '',
        ])

        # Add tabs and return the formatted result.
        if tabs:
            result = '\n'.join(
                [f'{TAB*tabs}{line}' if line else '' for line in result.split('\n')])
        return result


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
    def new(**kwargs) -> 'ImportData':
        '''
        Initializes a new ImportData object from an Import object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ImportData object.
        :rtype: ImportData
        '''

        # Create the import data.
        return ImportData(
            super(ImportData, ImportData).new(**kwargs),
        )

    @staticmethod
    def from_python_file(line: str) -> 'ImportData':
        '''
        Creates an import data from a Python file.

        :param line: The line of the Python file.
        :type line: str
        :return: A new import data.
        :rtype: ImportData
        '''

        # Split the line on the import keywords.
        from_module, import_module = line.strip('\n').split('import ')
        from_module = from_module.replace('from ', '').strip() if 'from' in from_module else None
        import_module, alias = import_module.split(' as ') if ' as ' in import_module else (import_module, None)

        # Determine import type.
        if 'import' in line:
            if 'from' not in line:
                type = IMPORT_TYPE_CORE
            elif from_module.startswith('.'):
                type = IMPORT_TYPE_APP
            else:
                type = IMPORT_TYPE_INFRA

        # Create the import data.
        return ImportData(
            super(ImportData, ImportData).new(
                from_module=from_module,
                import_module=import_module,
                alias=alias,
                type=type
            ),
        )

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

    def to_primitive(self, role=None, **kwargs) -> str:
        '''
        Converts the import data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: List[str]
        '''

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive()

        # Return the default primitive.
        return super().to_primitive(role, **kwargs)

    def to_python_primitive(self) -> str:
        '''
        Converts the import data to a python source code-based primitive.
        
        :return: The source code-based primitive.
        :rtype: str
        '''

        # Initialize the result as a string and return it.
        result = ''.join([
            f'from {self.from_module} ' if self.from_module else '',
            f'import {self.import_module}' if self.import_module else '',
            f' as {self.alias}' if self.alias else '',
            '\n',
        ])
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
        return VariableData(
            super(VariableData, VariableData).new(**kwargs),
        )

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

    def to_primitive(self, role=None, **kwargs):
        '''
        Converts the variable data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive(**kwargs)

        # Return the default primitive.
        return super().to_primitive(role, **kwargs)

    def to_python_primitive(self, tabs: int = 0, **kwargs):
        '''
        Converts the variable data to a python source code-based primitive.
        '''

        # Set the result as a list.
        result = ''.join([
            f'{self.name}',
            f': {self.type}' if self.type else '',
            f' = {self.value}' if self.value else '',
            '\n',
        ])

        # Add tabs and return the formatted result.
        if tabs:
            result = '\n'.join(
                [f'{TAB*tabs}{line}' if line else '' for line in result.split('\n')])
        return result


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

    @staticmethod
    def new(**kwargs) -> 'ParameterData':
        '''
        Initializes a new ParameterData object from a Parameter object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ParameterData object.
        :rtype: ParameterData
        '''

        # Create the parameter data.
        return ParameterData(
            super(ParameterData, ParameterData).new(**kwargs),
        )
    
    @staticmethod
    def from_python_file(lines: List[str], **kwargs) -> 'ParameterData':
        '''
        Creates a parameter data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new parameter data.
        :rtype: ParameterData
        '''

        # Convert the lines to a string.
        lines = '/n'.join(lines).strip()

        # Split the lines on the colon.
        line = lines.split(':')

        # Set the name, type, and default.
        name = line[0].strip()
        type = line[1].strip() if len(line) == 2 else None
        default = None
        if '=' in type:
            type = type.split('=')
            default = type[1].strip()
            type = type[0].strip()

        # Check if the parameter is kwargs.
        is_kwargs = False
        if '**' in name:
            name = name.replace('**', '')
            is_kwargs = True

        # Create the parameter data.
        _parameter = ParameterData(
            dict(**kwargs,
                name=name,
                type=type,
                default=default,
                is_kwargs=is_kwargs
            ),
            strict=False
        )

        # Validate and return the parameter data.
        _parameter.validate()
        return _parameter

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

    def to_primitive(self, role=None, **kwargs):
        '''
        Converts the parameter data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive()

        # Return the default primitive.
        return super().to_primitive(role, **kwargs)

    def to_python_primitive(self):
        '''
        Converts the parameter data to a python source code-based primitive.
        
        :return: The source code-based primitive.
        :rtype: str
        '''

        # Set the result as a string and return it.
        result = ''.join([
            '**' if self.is_kwargs else '',
            f'{self.name}',
            f': {self.type}' if self.type and not self.is_kwargs else '',
            f' = \'{self.default}\'' if self.default and self.type == 'str' else '',
            f' = {self.default}' if self.default and not self.type == 'str' else '',
        ])
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
        return FunctionData(
            super(FunctionData, FunctionData).new(**kwargs),
        )
    
    @staticmethod
    def from_python_file(lines: List[str], **kwargs) -> 'FunctionData':
        '''
        Creates a function data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new function data.
        :rtype: FunctionData
        '''

        # Get the first line of the function.
        line = lines[0]

        # Split on the open parenthesis.
        line = line.split('(')

        # Set the name, parameters, and code block.
        name = line[0].split('def ')[1].strip()
        parameters = line[1].split(')')[0].split(',') if len(line) == 2 else []
        description_block = []
        code_block = []

        # Set the current region to parameters.
        current_region = 'parameters'

        # Iterate over the lines of the Python file.
        for line in lines[1:]:

            # Remove the leading whitespace.
            line = line.strip()

            # If the line starts with ''', set the current region to description and add the remaining parameters.
            if line.startswith("'''") and current_region == 'parameters':
                current_region = 'description'

            # If the line starts with ''' and the current region is description, set the current region to code block.
            elif line.startswith("'''") and current_region == 'description':
                current_region = 'code_block'
                
            # If the current region is parameter, add the line to the parameters block.
            if current_region == 'parameters':
                parameters.append(line)
            
            # If the current region is description, add the line to the description block.
            if current_region == 'description':
                description_block.append(line)

            # If the current region is code block, add the line to the code block.
            if current_region == 'code_block':
                code_block.append(line)

        # Initialize the parameter descriptions and types.
        param_descriptions = {}
        param_types = {}
        return_type = None
        return_description = None
        for line in description_block:
            if ':param' in line:
                param = line.split(':param ')[1].split(': ')[0]
                description = line.split(': ')[1]
                param_descriptions[param] = description
            if ':type' in line:
                param = line.split(':type ')[1].split(': ')[0]
                type = line.split(': ')[1]
                param_types[param] = type
            if ':return' in line:
                return_description = line.split(': ')[1]
            if ':rtype' in line:
                return_type = line.split(': ')[1]

        # Create the function data.
        _function = FunctionData(
            dict(**kwargs,
                name=name,
                parameters=[],
                return_type=return_type,
                return_description=return_description,
                description=description_block[1]
            ),
            strict=False
        )

        # Validate and return the function data.
        _function.validate()
        return

    def map(self, role: str = 'to_object', **kwargs) -> Function:
        '''
        Maps the function data to a function object.

        :param role: The role for the mapping.
        :type role: str
        :return: A new function object.
        :rtype: FunctionData
        '''

        # Map the function data to a function object.
        return Function.new(**self.to_primitive(role, **kwargs))

    def to_primitive(self, role=None, **kwargs):
        '''
        Converts the function data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        '''

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive(role, **kwargs)

        # Return the default primitive.
        return super().to_primitive(role, **kwargs)

    def to_python_primitive(self, role: str, tabs: int = 0, **kwargs):
        '''
        Converts the function data to a python source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param tabs: The number of tabs for the code block.
        :type tabs: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        # Create the parameters segment.
        delimiter = ', ' if len(self.parameters) < 3 else f',\n{TAB}'
        parameters = (
            parameter.to_primitive(role, **kwargs) for parameter in self.parameters
        ) if self.parameters else []

        # Initialize the result as the function name.
        result = ''.join([
            f'def {self.name}(',
            'self' if self.is_class_method else '',
            ',' if self.parameters else '',
            f'\n{TAB}' if len(self.parameters) > 2 else '',
            ' ' if self.parameters and len(self.parameters) <= 2 else '',
            delimiter.join(parameters) if self.parameters else '',
            '\n' if len(self.parameters) > 2 else '',
            f') -> {self.return_type}:\n' if self.return_type else '):\n',
            f'{TAB}\'\'\'\n',
            f'{TAB}{self.description}\n',
            '\n' if self.parameters or self.return_type else '',
            '\n'.join(
                [f'{TAB}:param {param.name}: {param.description}\n{TAB}:type {param.name}: {param.type}' for param in self.parameters]),
            '\n' if self.parameters and self.return_type else '',
            f'{TAB}:return: {self.return_description}\n' if self.return_description else '',
            f'{TAB}:rtype: {self.return_type}\n' if self.return_type else '\n',
            f'{TAB}\'\'\'\n',
            f'\n{TAB}pass\n' if not self.code_block else '',
            '\n' if self.code_block else '',
            '\n\n'.join(
                [f'{block.to_primitive(role, tabs=1)}' for block in self.code_block]) if self.code_block else '',
            '\n' if self.code_block else '',
        ])

        # Format the tabs and return the result.
        if tabs:
            result = '\n'.join(
                [f'{TAB*tabs}{line}' if line else '' for line in result.split('\n')])
        return result


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

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new ClassData object.
        :rtype: ClassData
        '''

        # Set the attributes and methods as VariableData and FunctionData objects.
        kwargs['attributes'] = [VariableData.new(
            **attribute) for attribute in kwargs.get('attributes', [])]
        kwargs['methods'] = [FunctionData.new(
            **method) for method in kwargs.get('methods', [])]

        # Create the class data.
        return ClassData(
            super(ClassData, ClassData).new(**kwargs),
        )

    @staticmethod
    def from_python_file(lines: List[str], type: str, **kwargs) -> 'ClassData':
        '''
        Creates a class data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: List[str]
        :param type: The type of the class.
        :type type: str
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

        # Initialize the attributes and methods.
        attributes = []
        methods = []
        current_region = None

        # Iterate over the lines of the Python file.
        for line in lines[3:]:

            # Set the current region.
            if line.__contains__('#**'):
                current_region = line.strip()

            # Add the line to the attributes if the current region is attributes.
            elif type == 'model' and current_region == '#** moa':
                attributes.append(line.strip())
                

            # Add the line to the methods if the current region is methods.
            elif type == 'model' and current_region == '#** mom':
                methods.append(line)

            



            

        # Create the class data.
        _class = ClassData(
            dict(**kwargs,
                name=name,
                attributes=[VariableData.from_python_file(lines) for lines in '/n'.join(attributes).split('\n\n')],
                methods=[FunctionData.from_python_file(lines) for lines in '/n'.join(methods).split('\n\n')],
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

    def to_primitive(self, role=None, **kwargs):
        '''
        Converts the class data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive(role, **kwargs)

        # Return the default primitive.
        return super().to_primitive(role, **kwargs)

    def to_python_primitive(self, role: str, tabs: int = 0, **kwargs):
        '''
        Converts the class data to a python source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :param tabs: The number of tabs for the code block.
        :type tabs: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The source code-based primitive.
        :rtype: str
        '''

        # Initialize the result as a list.
        result = ''.join([
            f'class {self.name}(',
            ', '.join(self.base_classes) if self.base_classes else 'object',
            '):\n',
            f'{TAB}\'\'\'\n',
            f'{TAB}{self.description}\n',
            f'{TAB}\'\'\'\n',
            f'\n{TAB}pass\n' if not self.attributes and not self.methods else '',
            '\n' if self.attributes or self.methods else '',
            f'{TAB}#** moa\n\n' if self.attributes and self.type == 'model' else '',
            '\n'.join([f'{attribute.to_primitive(role, tabs=1)}'
                      for attribute in self.attributes]) if self.attributes else '',
            '\n' if self.methods else '',
            f'{TAB}#** mom\n\n' if self.methods and self.type == 'model' else '',
            '\n'.join([method.to_primitive(role, tabs=1)
                      for method in self.methods]) if self.methods else '',
        ])

        # Format the tabs and return the result.
        if tabs:
            result = '\n'.join(
                [f'{TAB*tabs}{line}' if line else '' for line in result.split('\n')])
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

    constants = t.ListType(
        t.ModelType(VariableData),
        default=[],
        metadata=dict(
            description='The constants for the module.'
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
    def from_python_file(lines: List[str], type: str, **kwargs) -> 'ModuleData':
        '''
        Creates a module data from a Python file.
        '''

        # Convert to a string.
        lines = '\n'.join(lines)

        # Split the lines on the component type.
        lines = lines.split('#** com\n\n')

        # Split on the imports and package them.
        imports = lines[0].split('#** imp\n\n')
        imports = [ImportData.from_python_file(import_line) for import_line in imports if import_line]

        # Split the classes on the three new lines.
        classes = lines[1].split('\n\n\n')

        # Initialize the module data.
        imports = []
        components = []
        current_region = None
        component_type = None
        component_lines = []

        # Iterate over the lines of the Python file.
        for line in lines:

            # Set the current region if the line is a comment.
            if line.startswith('#**'):
                current_region = line
                continue

            # Add the line to the module code if the current region is imports.
            if current_region == '#** imp':
                if line.startswith('import'):
                    imports.append(ImportData.from_python_file(line, 'core'))
                elif line.startswith('from .'):
                    imports.append(ImportData.from_python_file(line, 'app'))
                elif line.startswith('from'):
                    imports.append(ImportData.from_python_file(line, 'infra'))
                elif not line:
                    continue

            # Add the line to the module code if the current region is components.
            elif current_region == '#** com':
                if line.startswith('class'):
                    if component_lines and component_type == 'class': 
                        type = 'model' if type == 'objects' else type 
                        components.append(ClassData.from_python_file(
                            lines=component_lines, 
                            type=type
                        ))
                    component_type = 'class'
                    component_lines = [line]
                elif not line and not component_type:
                    continue
                else:
                    component_lines.append(line)

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
        _object.components = [component.map(
            role, **kwargs) for component in self.components]

        # Return the mapped module data.
        return _object

    def to_primitive(self, role=None):
        '''
        Converts the module data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
        :return: The source code-based primitive.
        :rtype: str
        '''

        # If the role is to_data.python, return the python primitive.
        if role == 'to_data.python':
            return self.to_python_primitive(role)

        # Return the default primitive.
        return super().to_primitive(role)

    def to_python_primitive(self, role: str = 'to_data.python'):
        '''
        Converts the module data to a python source code-based primitive.
        
        :return: The source code-based primitive.
        :rtype: str
        '''

        # Prepare imports for the python primitive.
        has_imports = {type: any(_import.type == type for _import in self.imports) for type in IMPORT_TYPES}
    
        # Create the python primitive.
        result = ''.join([
            '#** imp\n\n' if self.imports else '',
            '\n'.join((_import.to_primitive(role=role) for _import in self.imports if _import.type == 'core')) if has_imports[IMPORT_TYPE_CORE] else '',
            '\n\n' if has_imports[IMPORT_TYPE_CORE] else '',
            '\n'.join((_import.to_primitive(role=role) for _import in self.imports if _import.type == 'infra')) if has_imports[IMPORT_TYPE_INFRA] else '',
            '\n\n' if has_imports[IMPORT_TYPE_INFRA] else '',
            '\n'.join((_import.to_primitive(role=role) for _import in self.imports if _import.type == 'app')) if has_imports[IMPORT_TYPE_APP] else '',
            '\n\n' if has_imports[IMPORT_TYPE_APP] else '',
            '\n' if self.imports else '',
            '#** com\n\n' if self.components else '',
            '\n\n'.join(
                (f'{component.to_primitive(role=role)}' for component in self.components)),
        ])
        return result
