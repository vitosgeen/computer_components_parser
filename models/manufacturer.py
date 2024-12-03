
class Manufacturer():
    
    # consts of manufacturers
    ASUS = 'ASUS'
    ASROCK = 'ASROCK'
    GIGABYTE = 'GIGABYTE'
    MSI = 'MSI'
    BIOSTAR = 'BIOSTAR'
    COLORFUL = 'COLORFUL'
    EVGA = 'EVGA'
    GALAX = 'GALAX'

    def __init__(self):
        pass

    def list_manufacturers(self):
        return [self.ASUS, self.ASROCK, self.GIGABYTE, self.MSI, self.BIOSTAR, self.COLORFUL, self.EVGA, self.GALAX]
    
    def get_manufacturer(self, manufacture):
        if manufacture == self.ASUS:
            return 'asus'
        elif manufacture == self.ASROCK:
            return 'asrock'
        elif manufacture == self.GIGABYTE:
            return 'gigabyte'
        elif manufacture == self.MSI:
            return 'msi'
        elif manufacture == self.BIOSTAR:
            return 'biostar'
        elif manufacture == self.COLORFUL:
            return 'colorful'
        elif manufacture == self.EVGA:
            return 'evga'
        elif manufacture == self.GALAX:
            return 'galax'
        return None
    
    def validate_manufacture(self, manufacture):
        manufacture = manufacture.upper()
        if manufacture in self.list_manufacturers():
            return True
        return False