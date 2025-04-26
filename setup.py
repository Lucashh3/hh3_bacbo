from setuptools import setup, find_packages

setup(
    name="bacbo_bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pyautogui',
        'opencv-python',
        'numpy',
        'pytest'
    ],
    python_requires='>=3.8',
)