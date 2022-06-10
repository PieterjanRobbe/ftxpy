import numpy as np

# class that represents an FTX parameter
class FTXParameter():
    """
    A class to represent an FTX parameter

    Methods
    -------
    check_bounds(value):
        Checks if the given parameter falls between the lower and upper bound
    get_name()
        Returns the name of this parameter
    get_value()
        Returns the current value of this parameter
    set_value(value)
        Sets the value of this parameter to the given value
    set_random_value(value)
        Sets the value of this parameter to a random value sampled according to a uniform law between the lower and upper bound
    """

    def __init__(self, name, description, nominal, lower=None, upper=None, log10_transform=False):
        """
        Constructs all the necessary attributes for the FTXParameter object

        Parameters
        ----------
            name : str
                The name of the parameter
            description : str
                A description of the parameter
            nominal : float
                The nominal value of the parameter
            lower : float (keyword argument)
                The lower bound of this parameter
            upper : float (keyword argument)
                The upper bound of this parameter
            log10_transform : bool (keyword argument)
                A flag to indicate if the log of this parameter must be sampled
        """
        self.name = name
        self.description = description
        self.nominal = nominal
        self.value = self.nominal
        self.lower = lower if not lower is None else nominal
        self.upper = upper if not upper is None else nominal
        self.log10_transform = log10_transform
        self.check_bounds(nominal)

    def check_bounds(self, value:float)->None:
        """Checks if the given parameter falls between the lower and upper bound"""
        if self.lower > self.upper:
            print(f"Invalid bounds specified for parameter {self.name}: lower bound ({self.lower}) > upper bound ({self.upper})")
            raise ValueError("FTXPy -> FTXParameter -> check_bounds() : Invalid bounds specified")
        else:
            if not (value >= self.lower and value <= self.upper):
                print(f"Invalid value specified for parameter {self.name}: expected value between {self.lower} (lower bound) and {self.upper} (upper bound), got {value}")
                raise ValueError("FTXPy -> FTXParameter -> check_bounds() : Invalid value specified")

    def get_name(self)->str:
        """Returns the name of this parameter"""
        return self.name

    def get_value(self)->float:
        """Returns the current value of this parameter"""
        return self.value

    def set_value(self, value:float)->None:
        """
        Sets the value of this parameter to the given value
        
            Parameters:
                value (float): The new vaue for this parameter
        """
        self.value = value
        if self.upper == self.lower: # also change lower and upper bound if parameter is deterministic
            self.upper = value
            self.lower = value
        self.check_bounds(value)

    def set_random_value(self)->None:
        """Sets the value of this parameter to a random value sampled according to a uniform law between the lower and upper bound"""
        a = self.lower
        b = self.upper
        if self.log10_transform:
            a = np.log10(a)
            b = np.log10(b)
        value = np.random.rand() * (b - a) + a
        if self.log10_transform:
            value = 10**value
        self.value = value