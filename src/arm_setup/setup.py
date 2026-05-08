from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'arm_setup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', 'arm_setup', 'launch'),
            glob('launch/*.launch.py')),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chelsie-wei',
    maintainer_email='ywei05@tufts.edu',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "camera_publisher = arm_setup.camera_publisher:main",
            #"move_arm = arm_setup.move_arm:main",
            #"move_arm_sub = arm_setup.move_arm_sub:main",
            # "fake_publisher = arm_setup.fake_publisher:main",
            "color_detector_node = arm_setup.color_detector_node:main",
            "pixel_to_pose = arm_setup.pixel_to_pose:main",
            "move_arm_node = arm_setup.move_arm_node:main",
            #"state_machine = arm_setup.state_machine:main",
        ],
    },
)
