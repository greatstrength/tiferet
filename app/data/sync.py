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

        # Return the result as a list.
        return [result]
    

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
            result = f'{result}({", ".join(self.base_classes)})'
        else:
            result = f'{result}(object):'

        # Set the result as a list.
        result = [result]
        result.append("'''")
        result.append(self.description)
        result.append("'''")
        result.append('')

        # Add the attributes to the result.
        for attribute in self.attributes:
            result.extend([line for line in attribute.to_primitive(role, app_data, **kwargs)])
            result.append('')

        # Add the methods to the result.
        for method in self.methods:
            result.extend([line for line in method.to_primitive(role, app_data, **kwargs)])
            result.append('')

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

    @staticmethod
    def from_python_file(**kwargs) -> 'ModuleData':
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
        result.extend([_import.to_primitive(role, app_data, **kwargs)
                      for _import in self.imports])
        result.extend([component.to_primitive(role, app_data, **kwargs)
                      for component in self.components])

        # Return the result.
        return result
