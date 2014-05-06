pydagman
========

Python library for programmatic creation of DAGman job files for Condor

Usage
-----
To work with the package, put it in an accessible location and import the Dagfile and Job classes
```python
from pydagman.dagfile import Dagfile
from pydagman.job import Job
```

Create a dagfile object
```python
mydag = Dagfile()
```

Create a job.  You must specify the path to your submit file.  Optionally, you can specify a name, otherwise the library will automatically generate a uuid to serve as the job name.
```python
job1 = Job('job1.submit', 'job1')
# OR
job1 = Job('job1.submit') # Job name will be automatically generated uuid
```

Jobs can have variables (VARS in the dagfile) that will be injected into the submit file.
```python
job1.add_var('mem', '20G')
job1.add_var('outdir', '/tmp/job1')
```

Jobs can also have pre and post scripts.  Job.add\_pre and Job.add\_post take the path to the script as the first parameter, and optionally as many additional parameters as you need for script arguments.
```python
job1.add_pre('pre_stage1.sh') # No additional arguments
job1.add_post('post_stage1.sh', '/tmp/job1', '/tmp/job2') # Expands to 'post-stage1.sh /tmp/job1 /tmp/job2'
```

Of course we can also specify an arbitrary number of parent/child relationships between jobs.  Job.add\_parent ensures that the parent isn't already in the child job's parent list.  If it is, Job will throw DuplicateParentError.  The library could choose to just ignore the duplicate Job.add\_parent, but since it almost certainly indicates a logic issue with the program using this library we choose to fail early.
```python
job2 = Job('job2.submit')
job2.add_parent(job1)
job2.add_parent(job1) # Adding the same parent a second time throws DuplicateParentError
```

Once you have configured your job's variables, pre/post scripts, and parent/child relationships you add them to the dagfile with Dagfile.add\_job.
```python
my_dag.add_job(job1)
my_dag.add_job(job2)
```

Dagfile.add\_job also checks for circular dependencies and throws CircularDependencyError if one is found.
```python
job3 = Job('job3.submit')
job4 = Job('job4.submit')
job3.add_parent(job4)
job4.add_parent(job3) # We now have a circular dependency between job3 and job4, but they are not checked until the jobs                        # are added to the dagfile
mydag.add_job(job3) # No error here, since we've only added job3 to the dagfile so far
mydag.add_job(job4) # Now CircularDependencyError is thrown, because job3 already specified job4 as it's parent
```

The state of a job is saved to the dagfile object when add_job is called.  Therefore, adding further attributes to a job (vars, pre/post, parent) after a job has already been added to a dagfile object will have no affect:
```python
job5 = Job('job5.submit')
mydag.add_job(job5)
job5.add_var('mem', '20G') # This has no affect since job5 was already added to the dagfile.
```

Finally, save the dagfile to the filesystem using Dagfile.save()
```python
mydag.save('myworkflow.dag')
```

TODO
----
Support the following advanced dagman directives:
* PRE-SKIP
* ABORT-DAG-ON
* PRIORITY
* CATEGORY
* MAXJOBS
* CONFIG
