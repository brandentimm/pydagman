"""
pydagman.dagfile
Provides the dagfile class to represent a DAGman file
Classes:
Dagfile: Represents a DAGman file
InvalidJobObjectError: Thrown when add_job is called with an invalid pydagman.job.Job object
CircularDependencyError: Thrown when add_job would result in a circular dependency because
the new_job already has the existing job as a parent
"""
import job


class Dagfile:
    """
    Class to represent a DAGman file
    Attributes:
    jobs (list[pydagman.job.Job]): A list of Job objects
    """
    def __init__(self):
        """
        Initialize a new Dagman object
        :rtype : object
        """
        self.jobs = []

    def add_job(self, new_job):
        """
        Add a job to the Dagfile object
        Args:
        new_job (pydagman.job.Job): The Job object to add
        Raises:
        InvalidJobObjectError: if new_job is not a valid Job object
        """
        if isinstance(new_job, job.Job) is not True:
            raise InvalidJobObjectError("Error in Dagman.add_job", new_job)
        try:
            self.__dependency_check(new_job)
        except Exception as e:
            raise(e)
        self.jobs.append(new_job)

    def save(self, filename):
        """Save the dagfile to a provided path
        Args:
        filename (string): Path to save the dagfile to
        """
        with open(filename, 'w') as dagfile:
            # First write out all of the job descriptions, including variables and pre/post scripts
            for job in self.jobs:
                dagfile.write('JOB %s %s\n' % (job.name, job.submit_file))
                if job.pre:
                    dagfile.write('SCRIPT PRE %s %s\n' % (job.name, ' '.join(job.pre)))
                if job.post:
                    dagfile.write('SCRIPT POST %s %s\n' % (job.name, ' '.join(job.post)))
                for key in job.vars:
                    dagfile.write('VARS %s %s="%s"\n' % (job.name, key, job.vars[key]))
                if job.num_retries:
                    dagfile.write('RETRY %s %d\n' % (job.name, job.num_retries))
                dagfile.write('\n')
            # Next print out the parent/child relationships - these must come after all jobs are defined
            for job in self.jobs:
                for parent in job.parents:
                    dagfile.write('PARENT %s CHILD %s\n' % (parent, job.name))

    def __dependency_check(self, new_job):
        """Check for circular dependencies
         Args:
         new_job (pydagman.job.Job): Job to add to the Dagfile object
         Raises:
         CircularDependencyError: if adding the job would create a circular dependency
        """
        for job in self.jobs:
                if new_job.name in job.parents and job.name in new_job.parents:
                    raise CircularDependencyError("CircularDependencyError in \
dagman.__dependency_check: Jobs %s and %s have a circular dependency." \
                        % (job.name, new_job.name))


class InvalidJobObjectError(Exception):
    """Error if trying to add a job that is not a valid pydagman.job.Job object"""
    def __init__(self, msg, obj):
        self.msg = msg
        self.obj = obj

    def __str__(self):
        return "%s\nExpected Job object, instead got %s" % (self.msg, repr(self.obj))


class CircularDependencyError(Exception):
    """Error if addition of job would create circular dependency """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg