# *** imports

# ** app
from ..events import *

# *** classes

# ** class: TestAddNumber
class TestAddNumber(Command):
    '''
    A command to add two numbers.
    '''

    # * method: execute
    def execute(self, a: int, b: int, **kwargs) -> int:
        '''
        Execute the command to add two numbers.

        :param a: The first number.
        :type a: int
        :param b: The second number.
        :type b: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The sum of the two numbers.
        :rtype: int
        '''
        
        # Return the sum of the two numbers.
        return int(a) + int(b)
    

# ** class: TestSubtractNumber
class TestSubtractNumber(Command):
    '''
    A command to subtract two numbers.
    '''

    # * method: execute
    def execute(self, a: int, b: int, **kwargs) -> int:
        '''
        Execute the command to subtract two numbers.

        :param a: The first number.
        :type a: int
        :param b: The second number.
        :type b: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The difference of the two numbers.
        :rtype: int
        '''
        
        # Return the difference of the two numbers.
        return int(a) - int(b)
    

# ** class: TestMultiplyNumber
class TestMultiplyNumber(Command):
    '''
    A command to multiply two numbers.
    '''

    # * method: execute
    def execute(self, a: int, b: int, **kwargs) -> int:
        '''
        Execute the command to multiply two numbers.

        :param a: The first number.
        :type a: int
        :param b: The second number.
        :type b: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The product of the two numbers.
        :rtype: int
        '''
        
        # Return the product of the two numbers.
        return int(a) * int(b)
    

# ** class: TestDivideNumber
class TestDivideNumber(Command):
    '''
    A command to divide two numbers.
    '''

    # * method: execute
    def execute(self, a: int, b: int, **kwargs) -> float:
        '''
        Execute the command to divide two numbers.

        :param a: The numerator.
        :type a: int
        :param b: The denominator.
        :type b: int
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The quotient of the two numbers.
        :rtype: float
        '''
        
        # Raise an error if the denominator is zero.
        if int(b) == 0:
            self.raise_error(
                'DIVISION_BY_ZERO',
                'Cannot divide by zero.',
            )

        # Return the quotient of the two numbers.
        return int(a) / int(b)
    
