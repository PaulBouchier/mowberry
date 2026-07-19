import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'mowberry'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bouchier',
    maintainer_email='paul.bouchier@gmail.com',
    description='Support for the Mowberry mower',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mowberry_bringup = mowberry.mowberry_bringup:main',
            'print_zedf9p_pos = mowberry.print_zedf9p_pos:main',
            'gps_to_local_map_pose = mowberry.gps_to_local_map_pose:main',
            'print_map_pose = mowberry.print_map_pose:main',
            'rx_udp_corrections = mowberry.rx_udp_corrections:main'
        ],
    },
)
