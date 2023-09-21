import os
import re
from datetime import datetime
print('hello world')
# os.environ['GITHUB_WORKSPACE'] = '/Users/wphyo/Projects/unity/unity-data-services'
# os.environ['PR_TITLE'] = 'breaking: test1'
# os.environ['PR_NUMBER'] = '342'
# PR_NUMBER: ${{ github.event.number }}
# PR_TITLE: ${{ github.event.pull_request.title }}
print(os.environ)
pr_title = os.environ.get('PR_TITLE')
pr_number = os.environ.get('PR_NUMBER')
root_dir = os.environ.get('GITHUB_WORKSPACE')
pr_title = pr_title.strip().lower()

if pr_title.startswith('breaking'):
    major1, minor1, patch1 = 1, 0, 0
    change_log_line = '### Added'
elif pr_title.startswith('feat'):
    major1, minor1, patch1 = 1, 1, 0
    change_log_line = '### Changed'
elif pr_title.startswith('fix') or pr_title.startswith('chore'):  # TODO chore is bumping up version?
    major1, minor1, patch1 = 1, 0, 1
    change_log_line = '### Fixed'
else:
    raise RuntimeError(f'invalid PR Title: {pr_title}')

def update_version():
    # Specify the path to your setup.py file
    setup_py_path = os.path.join(root_dir, 'setup.py')
    # Define a regular expression pattern to match the version
    version_pattern = r"version\s*=\s*['\"](.*?)['\"]"

    # Read the contents of setup.py
    with open(setup_py_path, 'r') as setup_file:
        setup_contents = setup_file.read()

    # Find the current version using the regular expression pattern
    current_version = re.search(version_pattern, setup_contents).group(1)

    # Parse the current version and increment it
    major, minor, patch = map(int, current_version.split('.'))
    new_version = f"{major + major1}.{minor + minor1}.{patch + patch1}"

    # Replace the old version with the new version in setup.py
    updated_setup_contents = re.sub(version_pattern, f"version = '{new_version}'", setup_contents)

    # Write the updated contents back to setup.py
    with open(setup_py_path, 'w') as setup_file:
        setup_file.write(updated_setup_contents)

    print(f"Version bumped up from {current_version} to {new_version}")
    return new_version


new_version_from_setup = update_version()
def update_change_log():
    change_log_path = os.path.join(root_dir, 'CHANGELOG.md')
    change_log_blob = [
        f'## [{new_version_from_setup}] - {datetime.now().strftime("%Y-%m-%d")}',
        change_log_line,
        f'- [#${pr_number}](https://github.com/unity-sds/unity-data-services/pull/{pr_number}) {pr_title}'
    ]
    with open(change_log_path, 'r') as change_log_file:
        change_logs = change_log_file.read().splitlines()
    pattern = r"## \[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}"

    inserting_line = 0
    for i, each_line in enumerate(change_logs):
        if re.search(pattern, each_line):
            inserting_line = i
            break
    inserting_line = inserting_line - 1 if inserting_line > 0 else inserting_line
    for i, each_line in enumerate(change_log_blob):
        change_logs.insert(inserting_line, each_line)
        inserting_line += 1
    change_logs = '\n'.join(change_logs)

    with open(change_log_path, 'w') as change_log_file:
        change_log_file.write(change_logs)
    return
update_change_log()