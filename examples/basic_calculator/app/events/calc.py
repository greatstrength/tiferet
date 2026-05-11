# *** imports

# ** core
from typing import Any

# ** infra
from tiferet.events import *

# ** app
from .settings import BasicCalcEvent

# *** events

# ** event: add_number
class AddNumber(BasicCalcEvent):
    '''
    A domain event to perform addition of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the addition event.

        :param a: A number representing the first operand.
        :type a: Any
        :param b: A number representing the second operand.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The sum of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Add verified values of a and b.
        result = a_verified + b_verified

        # Return the result.
        return result


# ** event: subtract_number
class SubtractNumber(BasicCalcEvent):
    '''
    A domain event to perform subtraction of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the subtraction event.

        :param a: A number representing the first operand.
        :type a: Any
        :param b: A number representing the second operand.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The difference of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Subtract verified values of b from a.
        result = a_verified - b_verified

        # Return the result.
        return result


# ** event: multiply_number
class MultiplyNumber(BasicCalcEvent):
    '''
    A domain event to perform multiplication of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the multiplication event.

        :param a: A number representing the first operand.
        :type a: Any
        :param b: A number representing the second operand.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The product of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Multiply the verified values of a and b.
        result = a_verified * b_verified

        # Return the result.
        return result


# ** event: divide_number
class DivideNumber(BasicCalcEvent):
    '''
    A domain event to perform division of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the division event.

        :param a: A number representing the numerator.
        :type a: Any
        :param b: A number representing the denominator, must be non-zero.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The quotient of a and b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Check if b is zero to avoid division by zero.
        self.verify(b_verified != 0, 'DIVISION_BY_ZERO')

        # Divide the verified values of a by b.
        result = a_verified / b_verified

        # Return the result.
        return result


# ** event: exponentiate_number
class ExponentiateNumber(BasicCalcEvent):
    '''
    A domain event to perform exponentiation of two numbers.
    '''

    # * method: execute
    def execute(self, a: Any, b: Any, **kwargs) -> int | float:
        '''
        Execute the exponentiation event.

        :param a: A number representing the base.
        :type a: Any
        :param b: A number representing the exponent.
        :type b: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The result of a raised to the power of b.
        :rtype: int | float
        '''

        # Verify numeric inputs.
        a_verified = self.verify_number(str(a))
        b_verified = self.verify_number(str(b))

        # Exponentiate the verified value of a by b.
        result = a_verified ** b_verified

        # Return the result.
        return result
