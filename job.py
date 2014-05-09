"""
pydagman.job
Provides the Job class to represent a Condor job to be submitted via DAGman
Classes:
Job: Represent a DAGman Condor job
DuplicateParentError: Exception thrown when trying to add a parent already in
the parents list
"""
from shortuuid import uuid

class Job:
    """
    Class to represent a DAGman Condor Job
    Attributes:
    submit_file (string): Path to the Condor submit file
    name (string): The name to assign to the Condor job
    vars (dict): A dictionary of key/value pairs representing DAGman VARS for a job
    parents (list[string]): A list of job names that are parents of this job
    pre (list[string]): Command and arguments to run as SCRIPT PRE for this job
    post (list[string]): Command and arguments to run as SCRIPT POST for this job
    retry (int): Number of times to retry the job
    """
    def __init__(self, submit_file, name=''):
        """
        Create a new pydagman.Job object

        Arguments:
        submit_file (string): The full path to the Condor submit file for this job
        name (string): The name to assign to the job.  Optional parameter, if name is
        not provided a uuid is automatically generated

        Yields:
        Job object
        """
        self.name = name if name else uuid()
        self.submit_file = submit_file
        self.vars = {}
        self.parents = []
        self.pre = []
        self.post = []
        self.num_retries = 0
        self.noop = False

    def add_var(self, name, value):
        """Add a VARS directive for this job
        Args:
        name (string): name of the variable
        value (string): value to assign
        """
        self.vars[name] = value

    def add_parent(self, parent_job):
        """Add a parent to this job
        Args:
        parent_job (string): Job name of the parent job to add

        Raises:
        DuplicateParentError: if parent_job is already in the parents list
        """
        if parent_job.name not in self.parents:
            self.parents.append(parent_job.name)
        else:
            raise DuplicateParentError("DuplicateParentError in \
                  dagman.Job.add_parent: Parent job %s is already a parent of %s."
            % (parent_job.name, self.name))

    def add_pre(self, path, *args):
        """Add a SCRIPT PRE directive to the job
        Args:
        path (string): Path to the script
        *args (optional): Additional arguments to the script
        """
        self.pre.append(path)
        for index, arg in enumerate(args):
            self.pre.append(arg)

    def add_post(self, path, *args):
        """Add a SCRIPT POST directive to the job
        Args:
        path (string): Path to the script
        *args (optional): Additional arguments to the script
        """
        self.post.append(path)
        for index, arg in enumerate(args):
            self.post.append(arg)

    def retry(self, num_retries):
        """Set the number of retries for this job
        Args:
        num_retries (int): Number of times to retry the job

        """
        self.num_retries = num_retries

class DuplicateParentError(Exception):
    """Thrown if attempting to add a parent that is already in the parents list"""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg