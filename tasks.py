from contextlib import contextmanager
import io
import os
import re
from datetime import datetime
from invoke import run, task
from textwrap import dedent

from tox._config import parseconfig

RELEASE_BRANCH = 'master'
VERSION_FILE = 'chronometer.py'
CHANGES_FILE = 'CHANGES.rst'


_version_re = re.compile(r'(?:v(\d+)(?:\.|_)(\d+))')


def _tool_run(*commands, env=None, **kwargs):
    kwargs.setdefault('hide', True)

    _env_backup, output = os.environb.copy(), []
    for command in commands:
        try:
            os.environb.update(env or {})
            output += run(command, **kwargs),
        finally:
            os.environb.clear()
            os.environb.update(_env_backup)

    return output[0] if len(output) == 1 else output


def _version_find_existing():
    """Returns set of existing versions in this repository.  This
    information is backed by previously used version tags in git.
    Available tags are pulled from origin repository before.

    :return:
        available versions
    :rtype:
        set
    """
    _tool_run('git fetch origin -t')
    git_tags = [x for x in (y.strip() for y in (_tool_run('git tag -l')
                                                .stdout.split('\n'))) if x]
    return {tuple(int(n) if n else 0 for n in m.groups())
            for m in (_version_re.match(t) for t in git_tags) if m}


def _version_get_latest():
    """Returns the most recent used version number.  This information is
    backed by previously used version tags in git.  Git tags are pulled from
    server before returning.

    :return:
        latest version
    :rtype:
        tuple
    """
    return max(_version_find_existing())


def _version_guess_next():
    """Guess next version by incrementing least significant version position
    in latest existing version.

    :return:
        next version
    :rtype:
        str
    """
    try:
        latest_version = list(_version_get_latest())
    except ValueError:
        latest_version = [1, 0]
    else:
        latest_version[-1] += 1
    return tuple(latest_version)


def _version_format(version):
    return '.'.join(str(x) for x in version)


def _git_get_current_branch():
    """Determine the current checked out git branch name.

    :return:
        git branch name
    :rtype:
        str
    """
    return (_tool_run('git rev-parse --abbrev-ref HEAD')
            .stdout.strip('\n'))


@contextmanager
def _git_enable_branch(desired_branch):
    """Enable desired branch name."""
    preserved_branch = _git_get_current_branch()
    try:
        if preserved_branch != desired_branch:
            _tool_run('git checkout ' + desired_branch)
        yield
    finally:
        if preserved_branch and preserved_branch != desired_branch:
            _tool_run('git checkout ' + preserved_branch)


@contextmanager
def _git_enable_release_branch():
    """Enable desired release branch."""
    with _git_enable_branch(RELEASE_BRANCH):
        yield


_project_assign_re = re.compile((r"""^(\s*([^\s]+)\s*=\s*(?:"|'))"""
                                 r"""(?:[^"]*)((?:"|')\s*)$"""))


def _project_get_metadata(*args):
    with _git_enable_release_branch():
        return [_tool_run('python setup.py --' + x).strip('\n')
                for x in args]


def _project_get_metadata_key(key):
    return _project_get_metadata(key)[0]


def _patch_file(file_path, line_callback):
    with io.open(file_path) as in_stream:
        new_file_content = [line_callback(l.strip('\n')) + '\n'
                            for l in in_stream.readlines()]
    new_file_name = file_path + '.new'
    with io.open(new_file_name, 'w') as out_stream:
        out_stream.writelines(new_file_content)
    os.rename(new_file_name, file_path)


def _project_patch_version(new_version):
    replacements = {'__version__': new_version, }

    def __line_callback(line):
        match = _project_assign_re.match(line)
        if not match:
            return line
        head, var_name, tail = match.groups()
        return (head + replacements[var_name] + tail
                if var_name in replacements else line)
    _patch_file(VERSION_FILE, __line_callback)


def _project_patch_changelog():
    pit = datetime.now().strftime('Released on %Y-%m-%d.')
    _patch_file(CHANGES_FILE,
                lambda l: l if l != 'Yet to be released.' else pit)


@task
def mk_travis_config():
    """Generate configuration for travis."""
    t = dedent("""\
        sudo: false
        language: python
        python: 3.4
        env:
        {jobs}
        install:
            - pip install -r requirements/ci.txt
        script:
            - invoke ci_run_job $TOX_JOB
        after_success:
            coveralls
    """)
    jobs = [env for env in parseconfig(None, 'tox').envlist
            if not env.startswith('cov-')]
    jobs += 'coverage',
    print(t.format(jobs=('\n'.join(('    - TOX_JOB=' + job)
                                   for job in jobs))))


@task
def ci_run_job(job_name):
    """Run given job name in tox environment.  This task is supposed to run
    within the CI environment.
    """
    run(('tox'
         + ((' -e ' + job_name) if job_name != 'coverage' else '')
         + ' -- --color=yes'),
        pty=True)


@task
def mkrelease(finish='yes', version=''):
    """Allocates the next version number and marks current develop branch
    state as a new release with the allocated version number.
    Syncs new state with origin repository.
    """
    if not version:
        version = _version_format(_version_guess_next())

    if _git_get_current_branch() != 'release/' + version:
        _tool_run('git checkout develop',
                  'git flow release start ' + version)

    _project_patch_version(version)
    _project_patch_changelog()
    patched_files = ' '.join([VERSION_FILE, CHANGES_FILE])

    run('git diff ' + patched_files, pty=True)
    _tool_run(('git commit -m "Bump Version to {0!s}" {1!s}'
               .format(version, patched_files)))

    if finish not in ('no', 'n', ):
        _tool_run("git flow release finish -m '{0}' {0}".format(version),
                  env={b'GIT_MERGE_AUTOEDIT': b'no', })
        _tool_run('git push origin --tags develop master')
