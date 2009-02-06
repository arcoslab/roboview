from distutils.core import setup

setup(name='roboview',
      version='0.1',
      author='Jonathan Kleinehellefort',
      author_email='jk@molb.org',
      url='http://www9.in.tum.de/~kleinehe/roboview.html',
      description='Kinematic chain viewer based on KDL',
      license='GPL',
      package_dir={'roboview': ''},
      packages=['roboview'],
      scripts=['roboview']
    )
