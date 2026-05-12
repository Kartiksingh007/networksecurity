'''
The setup.py file is an essential part of packaging and 
distributing python Projects. It is used by setupools
(or distutil in older python versions) to define the configuration
of your project ,such as it metadatas, dependencies and more 
'''

from setuptools import find_packages,setup
from typing import List

def get_requirements() -> List[str]:
    """

    This function will return list of requirements
    
    """

    requirement_list:List[str]=[]

    try:
        with open('requirements.txt','r') as file:
            # read lines from the file 
            lines=file.readlines()
            #Process each line
            for line in lines:
                requirement=line.strip()
                ## ignore the empty lines and -e.   
                if requirement and requirement !='-e .':
                    requirement_list.append(requirement)

    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_list

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Kartik",
    another_email="kr5291766@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)

