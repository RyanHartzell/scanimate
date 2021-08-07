import setuptools
import os

current_dir = os.path.dirname(__file__)

# load __version__, __author__, __email__, etc variables
with open(os.path.join(current_dir,'scanimate/version_info.py')) as f:
    exec(f.read())

# load in list of requirements
requirements_path = os.path.join(current_dir,'requirements.txt')
with open(requirements_path,'r') as f:
    requirements = f.read().splitlines()

# load in list of dev requirements
dev_requirements_path = os.path.join(current_dir,'requirements-dev.txt')
with open(dev_requirements_path,'r') as f:
    requirements_dev = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name='scanimate',
      version=__version__,
      description=__description__,
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=__author__,
      author_email=__email__,
      license=__license__,
      url=__url__,
      download_url=__download_url__,
      maintainer=__maintainer__,
      maintainer_email=__maintainer_email__,
      keywords=__keywords__,
      python_requires=__python_requires__,
      platforms=__platforms__,
      classifiers=__classifiers__,
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=requirements, # these are always installed
      extras_require = {
                    'dev' : requirements_dev,
                    },
      entry_points={
          "console_scripts": [
              "scanimate=scanimate.scanimate:main",
          ]
      }
)