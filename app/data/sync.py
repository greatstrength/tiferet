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

    @staticmethod
    def from_python_file(lines: str) -> 'CodeBlockData':
        '''
        Creates a code block data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: List[str]
        :return: A new code block data.
        :rtype: CodeBlockData
        '''

        # Split the lines on the comments.
        comments = []
        code_lines = []
        for line in lines.split('\n'):
            if line.startswith('# '):
                comments.append(line.strip().strip('# '))
            else:
                code_lines.append(line[4:] if line.startswith(TAB) else line)

        # Create the code block data.
        return CodeBlockData(
            super(CodeBlockData, CodeBlockData).new(
                comments=comments,
                lines=code_lines
            ),
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

    def to_primitive(self, role=None, **kwargs):
        '''
        Converts the code block data to a source code-based primitive.
        
        :param role: The role for the conversion.
        :type role: str
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
        return super().to_primitive(role, **kwargs)

    def to_python_primitive(self, tabs: int = 0) -> str:
        '''
        Converts the code block data to a python source code-based primitive.

        :param tabs: The number of tabs for the code block.
        :type tabs: int
        :return: The source code-based primitive.
        :rtype: str
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
        from_module = from_module.replace(
            'from ', '').strip() if 'from' in from_module else None
        import_module, alias = import_module.split(
            ' as ') if ' as ' in import_module else (import_module, None)

        # Determine import type.
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


class VariableData(ModelData, Variable):
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
    def from_python_file(lines: str) -> 'VariableData':
        '''
        Creates a variable data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: str
        :return: A new variable data.
        :rtype: VariableData
        '''

        # Split the lines on the equals sign.
        name_and_type, value = lines.split(' = ' if ' = ' in lines else '=')
        name, type = name_and_type.split(
            ': ') if ':' in name_and_type else (name_and_type.strip(), None)
        if type == 'str':
            value = value.strip().strip('\'')

        # Create the variable data.
        return VariableData(
            super(VariableData, VariableData).new(
                name=name,
                type=type,
                value=value.strip(),
            ),
        )

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
    def from_python_file(line: str, **kwargs) -> 'ParameterData':
        '''
        Creates a parameter data from a Python file.

        :param lines: The line of the Python file.
        :type line: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new parameter data.
        :rtype: ParameterData
        '''

        # Remove the leading and trailing whitespace.
        line = line.strip('\n')
        name_and_type, default = line.split(
            ' = ' if ' = ' in line else '=') if '=' in line else (line, None)
        name, type = name_and_type.split(
            ': ') if ':' in name_and_type else (name_and_type.strip(), None)
        if type == 'str' and default:
            default = default.strip().strip('\'')

        # Check if the parameter is kwargs.
        is_kwargs = False
        if '**' in name:
            name = name.replace('**', '')
            is_kwargs = True
            type = 'dict'

        # Create the parameter data.
        return ParameterData.new(
            **kwargs,
            name=name,
            type=type,
            default=default.strip() if default else None,
            is_kwargs=is_kwargs
        )

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


class FunctionData(ModelData, Function):
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

    code_block = t.ListType(
        t.ModelType(CodeBlockData),
        default=[],
        metadata=dict(
            description='The code blocks for the function.'
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

        # Set the parameters as ParameterData objects.
        kwargs['parameters'] = [ParameterData.new(
            **parameter) for parameter in kwargs.get('parameters', [])]
        kwargs['code_block'] = [CodeBlockData.new(
            **block) for block in kwargs.get('code_block', [])]

        # Create the function data.
        return FunctionData(
            super(FunctionData, FunctionData).new(**kwargs),
        )

    @staticmethod
    def from_python_file(lines: str, **kwargs) -> 'FunctionData':
        '''
        Creates a function data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new function data.
        :rtype: FunctionData
        '''

        # Convert the lines to a string.
        lines = lines.strip('\n')
        name, parameters = lines.split('(')[0].replace(
            'def ', '').strip(), '('.join(lines.split('(')[1:])
        name = name.split('\n')[1] if name.startswith('@staticmethod') else name
        parameters, description = [param.strip() for param in parameters.split(
            ')')[0].split(',')], ')'.join(parameters.split(')')[1:])
        description = ':\n'.join(description.split(':\n')[1:])
        _, description, code_block = description.split('\'\'\'')
        description_block = description.split(f'\n{TAB}')[1:]
        description = description_block[0].strip('\n')

        # Set the parameter descriptions.
        param_descriptions = {}
        return_description = None
        return_type = None
        for line in description_block[1:]:
            if ':param' in line:
                param = line.split(':param ')[1].split(': ')[0]
                param_desc = line.split(': ')[1]
                param_descriptions[next(
                    (p.strip() for p in parameters if param in p.strip()), None)] = param_desc
            if ':return' in line:
                return_description = line.split(': ')[1]
            if ':rtype' in line and not return_type:
                return_type = line.split(': ')[1]

        # Set the code block.
        code_block = code_block.strip('\n').split('\n\n')
        if len(code_block) > 1 or 'pass' not in code_block[0]:
            code_block = [CodeBlockData.from_python_file(
                block[4:]) for block in code_block]
        else:
            code_block = []

        # If the lines start with @staticmethod, set the is_static_method and is_class_method flags.
        is_class_method = False
        is_static_method = False
        if lines.startswith('@staticmethod'):
            is_class_method = True
            is_static_method = True

        # If the return type is an object type, set the has_object_return flag.
        # If there is no return type, set the has_object_return flag to false.
        # If the return type is a list, dict, or any, set the has_object_return flag to false.
        # If the return type is a str, int, float, bool, date, or datetime, set the has_object_return flag to false.
        has_object_return = True
        if not return_type:
            has_object_return = False
        else:
            for prefix in ['List[', 'Dict[', 'Any']:
                if return_type.startswith(prefix):
                    has_object_return = False
                    break
            if return_type in ['str', 'int', 'float', 'bool', 'date', 'datetime']:
                has_object_return = False
        
        # Remove the first parameter if it is self and the function is not a class method.
        # Then sent the function as a class method.
        if not is_class_method and parameters[0] == 'self':
            parameters = parameters[1:]
            is_class_method = True

        # Create the function data.
        return FunctionData.new(**kwargs,
                                name=name,
                                parameters=[ParameterData.from_python_file(
                                    param, description=param_descriptions[param]) for param in parameters if param != 'self'],
                                return_type=return_type,
                                return_description=return_description,
                                description=description,
                                is_class_method=is_class_method,
                                is_static_method=is_static_method,
                                has_object_return=has_object_return,
                                code_block=code_block
                                )

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
            parameter.to_python_primitive(**kwargs) for parameter in self.parameters
        ) if self.parameters else []

        # Define has_self_parameter flag.
        has_self_parameter = self.is_class_method and not self.is_static_method

        # Define function to format paramter type description.
        def _format_parameter_type_description(param_type):
            if not param_type:
                return ''
            for type in ['List', 'Dict', 'Any']:
                if type in param_type and param_type.startswith('typin'):
                    return param_type[7:]
            return param_type

        # Initialize the result as the function name.
        result = ''.join([
            '@staticmethod\n' if self.is_static_method else '',
            f'def {self.name}(',
            'self' if has_self_parameter else '',
            ',' if has_self_parameter and self.parameters else '',
            f'\n{TAB}' if len(self.parameters) > 2 else '',
            ' ' if has_self_parameter and self.parameters and len(self.parameters) <= 2 else '',
            delimiter.join(parameters) if self.parameters else '',
            '\n' if len(self.parameters) > 2 else '',
            f') -> ' if self.return_type else '):\n',
            f'\'{self.return_type}\':\n' if self.has_object_return else '',
            'typing.' if self.return_type and self.return_type in ['List', 'Dict', 'Any'] else '',
            f'{self.return_type}:\n' if self.return_type and not self.has_object_return else '',
            f'{TAB}\'\'\'\n',
            f'{TAB}{self.description}\n',
            '\n' if self.parameters or self.return_type else '',
            '\n'.join(
                [f'{TAB}:param {param.name}: {param.description}\n{TAB}:type {param.name}: {_format_parameter_type_description(param.type)}' for param in self.parameters]),
            '\n' if self.parameters and self.return_type else '',
            f'{TAB}:return: {self.return_description}\n' if self.return_description else '',
            f'{TAB}:rtype: {self.return_type}\n' if self.return_type else '\n',
            f'{TAB}\'\'\'\n',
            f'\n{TAB}pass\n' if not self.code_block else '',
            '\n' if self.code_block else '',
            '\n\n'.join(
                [f'{block.to_python_primitive(tabs)}' for block in self.code_block]) if self.code_block else '',
            '\n' if self.code_block else '',
        ])

        # Format the tabs and return the result.
        if tabs:
            result = '\n'.join(
                [f'{TAB*tabs}{line}' if line else '' for line in result.split('\n')])
        return result


class ClassData(ModelData, Class):
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
    def from_python_file(lines: str, **kwargs) -> 'ClassData':
        '''
        Creates a class data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new class data.
        :rtype: ClassData
        '''

        # Get the first line of the class.
        name, lines = lines.split('(')[0].replace(
            'class ', '').strip(), '('.join(lines.split('(')[1:])
        base_classes, description = lines.split('):\n')[0].split(
            ','), '):\n'.join(lines.split('):\n')[1:])
        description, lines = description.split('\'\'\'')[1].strip(
            f'{TAB}\n'), '\'\'\''.join(description.split('\'\'\'')[2:])

        # Strip a tab from the beginning of each line.
        lines = '\n'.join([line[4:] if line.startswith(
            f'{TAB}') else line for line in lines.split('\n')])
        lines = lines.strip('\n\n').split('\n\n')

        # Initialize the attributes and methods.
        attributes = []
        methods = []
        method_lines = []
        current_region = None

        # Iterate over the lines.
        for line in lines:

            # Set the current region.
            if line.startswith('#**'):
                current_region = line.strip()

            # Add the line to the attributes if the current region is attributes.
            elif current_region == '#** atr':
                attributes.append(VariableData.from_python_file(line.strip()))

            # Add the line to the methods if the current region is methods.
            elif current_region == '#** met':
                if 'def ' in line:
                    if method_lines:
                        methods.append(FunctionData.from_python_file(
                            '\n'.join(method_lines)))
                        method_lines = []
                    method_lines.append(line)
                if line.startswith(TAB):
                    method_lines.append(line)

        # Add the last method.
        if method_lines:
            methods.append(FunctionData.from_python_file(
                '\n\n'.join(method_lines)))

        # Create the class data.
        return ClassData.new(
            **kwargs,
            name=name,
            attributes=attributes,
            methods=methods,
            base_classes=base_classes,
            description=description,
        )

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
            f'{TAB}\'\'\'\n{TAB}{self.description}\n{TAB}\'\'\'\n',
            f'\n{TAB}pass\n' if not self.attributes and not self.methods else '',
            '\n' if self.attributes or self.methods else '',
            f'{TAB}#** atr\n\n' if self.attributes else '',
            '\n'.join([f'{attribute.to_primitive(role, tabs=1)}'
                      for attribute in self.attributes]) if self.attributes else '',
            '\n' if self.attributes and self.methods else '',
            f'{TAB}#** met\n\n' if self.methods else '',
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

    functions = t.ListType(
        t.ModelType(FunctionData),
        default=[],
        metadata=dict(
            description='The functions for the module.'
        ),
    )

    classes = t.ListType(
        t.ModelType(ClassData),
        default=[],
        metadata=dict(
            description='The classes for the module.'
        ),
    )

    @staticmethod
    def new(
        imports: typing.List[Import] = [], 
        constants: typing.List[Variable] = [],          
            functions: typing.List[Function] = [], 
            classes: typing.List[Class] = [],
            **kwargs
        ) -> 'ModuleData':
        '''
        Initializes a new ModuleData object from a Module object.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A new ModuleData object.
        :rtype: ModuleData
        '''

        # Set the imports, constants, functions, and classes as ImportData, VariableData, FunctionData, and ClassData objects.
        imports = [ImportData.new(**_import) for _import in imports]
        constants = [VariableData.new(**constant) for constant in constants]
        functions = [FunctionData.new(**function) for function in functions]
        classes = [ClassData.new(**cls) for cls in classes]

        # Create the module data.
        return ModuleData(
            super(ModuleData, ModuleData).new(
                **kwargs,
                imports=imports,
                constants=constants,
                functions=functions,
                classes=classes
            ),
        )

    @staticmethod
    def from_python_file(lines: str, **kwargs) -> 'ModuleData':
        '''
        Creates a module data from a Python file.

        :param lines: The lines of the Python file.
        :type lines: str
        :param type: The type of the module.
        :type type: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new module data.
        :rtype: ModuleData
        '''

        # Split the lines on the code marker comments.
        lines, classes = lines.split(
            '#** cls\n\n') if '#** cls' in lines else (lines, None)
        lines, functions = lines.split(
            '#** fun\n\n') if '#** fun' in lines else (lines, None)
        lines, constants = lines.split(
            '#** con\n\n') if '#** con' in lines else (lines, None)
        imports = lines.split('#** imp\n\n')[1] if '#** imp' in lines else None
        imports = [ImportData.from_python_file(
            line) for line in imports.split('\n') if line] if imports else []
        constants = [VariableData.from_python_file(
            constant) for constant in constants.strip('\n').split(' #/\n') if constant] if constants else []
        functions = [FunctionData.from_python_file(
            function) for function in functions.split('\n\n\n') if function] if functions else []
        classes = [ClassData.from_python_file(class_lines) for class_lines in classes.strip(
            '\n').split('\n\n\n')] if classes else []

        # Create and return the module data.
        return ModuleData(super(ModuleData, ModuleData).new(
            imports=imports,
            constants=constants,
            functions=functions,
            classes=classes,
            **kwargs
        ))

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

        # Prepare the imports, constants, functions, and classes.
        imports = [import_.map(role, **kwargs)
                   for import_ in self.imports] if self.imports else []
        constants = [constant.map(role, **kwargs)
                     for constant in self.constants] if self.constants else []
        functions = [function.map(role, **kwargs)
                     for function in self.functions] if self.functions else []
        classes = [cls.map(role, **kwargs)
                   for cls in self.classes] if self.classes else []

        # Map the module data to a module data.
        _object = super().map(Module, role,
                              imports=imports, constants=constants,
                              functions=functions, classes=classes,
                              **kwargs)

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
        has_imports = {type: any(
            _import.type == type for _import in self.imports) for type in IMPORT_TYPES}

        # Create the python primitive.
        result = ''.join([
            '#** imp\n\n' if self.imports else '',
            ''.join((_import.to_primitive(role=role) for _import in self.imports if _import.type ==
                    'core')) if has_imports[IMPORT_TYPE_CORE] else '',
            '\n' if has_imports[IMPORT_TYPE_CORE] else '',
            ''.join((_import.to_primitive(role=role) for _import in self.imports if _import.type ==
                    'infra')) if has_imports[IMPORT_TYPE_INFRA] else '',
            '\n' if has_imports[IMPORT_TYPE_INFRA] else '',
            ''.join((_import.to_primitive(role=role) for _import in self.imports if _import.type ==
                    'app')) if has_imports[IMPORT_TYPE_APP] else '',
            '\n' if has_imports[IMPORT_TYPE_APP] else '',
            '\n' if self.imports else '',
            '#** con\n\n' if self.constants else '',
            ' #/\n'.join(
                (f'{constant.to_primitive(role=role)}'.strip('\n') for constant in self.constants)) if self.constants else '',
            '\n\n\n' if self.constants else '',
            '#** fun\n\n' if self.functions else '',
            '\n\n'.join(
                (f'{function.to_primitive(role=role)}' for function in self.functions)) if self.functions else '',
            '\n' if self.functions else '',
            '#** cls\n\n' if self.classes else '',
            '\n\n'.join(
                (f'{cls.to_primitive(role=role)}' for cls in self.classes)) if self.classes else ''
        ])
        return result
