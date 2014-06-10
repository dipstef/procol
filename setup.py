from distutils.core import setup

VERSION = '0.1'

desc = """A library for concurrent processing:
Includes producer-consumer for intra/inter process communication, as well remote implementations based on zero-mq
and multiprocessing remote manager.
Other features include scheduling and a pool worker"""

name = 'procol'


setup(name=name,
      version=VERSION,
      author='Stefano Dipierro',
      author_email='dipstef@github.com',
      url='http://github.com/dipstef/{}/'.format(name),
      description='A library for concurrent processing',
      license='http://www.apache.org/licenses/LICENSE-2.0',
      packages=['procol', 'procol.queue', 'procol.pool'],
      platforms=['Any'],
      long_description=desc,
      requires=['pyzmq', 'funlib']
)

