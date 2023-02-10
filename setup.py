from setuptools import setup

setup(
    name='gridphoto',
    version='0.1.0',    
    description='This makes tiles from a larger image.',
    long_description = 'This will take a larger image and slice it up into smaller tile images.  This script will also rebuild the original from the smaller tiles or randomly place the tiles back together creating an image with the same dimensions using all the tiles.',
    url='https://github.com/MotionDesignStudio/gridphoto',
    author='Motion Design Studio',
    author_email='thank@you.net',
    license='Creative Commons',
    packages=['gridphoto'],
    install_requires=['PIL',                     
                      ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
    ],
)