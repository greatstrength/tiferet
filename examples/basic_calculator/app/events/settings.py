# *** imports

# ** infra
from tiferet.events import *

# *** events

# ** event: basic_calc_event
class BasicCalcEvent(DomainEvent):
    '''
    A domain event to validate that a value can be a Number object.
    '''

    # * method: verify_number
    def verify_number(self, value: str) -> int | float:
        '''
        Verify that the value can be converted to an integer or float.

        :param value: The value to verify.
        :type value: str
        :return: The numeric value as an integer or float.
        :rtype: int | float
        '''

        # Check if the value is a valid number.
        is_valid = isinstance(value, str) and (
            value.isdigit()
            or (value.replace('.', '', 1).isdigit() and value.count('.') < 2)
        )

        # Verify the value.
        self.verify(
            is_valid,
            'INVALID_INPUT',
            f"Invalid number: {value}",
            value=value,
        )

        # If valid, return the value as a float or int.
        if '.' in value:
            return float(value)
        return int(value)
