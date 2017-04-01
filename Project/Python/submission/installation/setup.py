#####################################################
# Install script for Windows 64-bit
# 1. Right-click on cmd.exe and run as administrator
# 2. Navigate to the folder containing this file
# 3. run `python setup.py`
#####################################################
import pip

# copies directories over
def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        print(exc)
        else: raise

# installs a pip package
def install(package):
    pip.main(['install', package])


if __name__ == '__main__':

    # pip install   
    dependencies = ['numpy', 'pandas', \
                    'tensorflow', 'keras', 'flask', \
                    'matplotlib', 'scipy', 'pyparsing']

    for pkg in dependencies:
        install(pkg)

    import glob
    import shutil, errno

    # Copy NetLogo extensions to directory
    extensions = glob.glob(r'.\*')

    nl_path = r'C:\Program Files\NetLogo*'
    nl_path = glob.glob(nl_path)[0]
    nl_extensions_dir = nl_path + r'\app\extensions'

    print(extensions)
    print(nl_extensions_dir) 

    for extension in extensions:
        # print(extension.replace(r'.\', ''))
        print(extension)
        copy_dir(extension, nl_extensions_dir + extension)