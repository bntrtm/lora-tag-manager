from graphics import TrainLoraWin
import os
import shutil

# save root, content, static, & docs directories for use in function definitions
root_dir = os.getcwd()
content_path = os.path.join(root_dir, 'content')
static_dir = os.path.join(root_dir, 'static')
docs_dir = os.path.join(root_dir, 'docs')
# save path to default template, located in the root directory
template_path = os.path.join(root_dir, 'template.html')

def prompt_dir(directory, as_copy=True):
    '''Takes in a directory and sets it for the program to use.

    If optional parameter 'as_copy' is set to True, the program will COPY the aforementioned files to a separate
    directory to keep the original directory untouched.
        This directory copy will be titled as '{directory_given}_LoRA'.
    '''

def copy_dir(from_dir, to_dir, b_clean=False):
    '''Copies the contents of one directory to another, deleting any existing destination directory, if desired.
    '''
    # check that the from_dir is valid and has files to work with
    if not os.path.exists(from_dir):
        raise ValueError(f'Copy-From directory "{from_dir}" does not exist.')
    # a list of paths within the "from_dir" directory that could be files, or directories themselves
    from_paths = os.listdir(from_dir)
    if len(from_paths) == 0:
        if b_clean:
            raise Exception(f'{from_dir} contains no files to copy!')
        print(f'{omit_cd(from_dir)} contains no files to copy. Skipping directory.')
        return
    # delete any existing to_dir if b_clean is true
    if b_clean:
        if os.path.exists(to_dir):
            shutil.rmtree(to_dir)
    # remake to_dir
    if not os.path.exists(to_dir):
        os.mkdir(to_dir)
    # here, we acknowledge that shutil.copytree exists, but use shutil.copy anyway, for recursion practice
    print(f'Copying contents of {omit_cd(from_dir)} to {omit_cd(to_dir)}...')
    for p in from_paths:
        new_from_path = os.path.join(from_dir, p)
        new_to_path = os.path.join(to_dir, p)
        if os.path.isfile(new_from_path):
            shutil.copy(new_from_path, new_to_path)
        else:
            # recursively copy over any subdirectories
            copy_dir(new_from_path, new_to_path)

def main():
    win = TrainLoraWin(900, 600)
    win.redraw()

    win.wait_for_close()

main()