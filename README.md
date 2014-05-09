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

The Job.noop attribute controls whether the job is actually run or not.  Job.noop is False by default
```python
job1 = Job('job1.submit')
job1.noop = True
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
job4.add_parent(job3) # We now have a circular dependency between job3 and job4, but they are not checked until the jobs are added to the dagfile
mydag.add_job(job3) # No error here, since we've only added job3 to the dagfile so far
mydag.add_job(job4) # Now CircularDependencyError is thrown, because job3 already specified job4 as it's parent
```
You can use job.Job.add_category and dagfile.Dagfile.set_maxjobs to control the number of concurrent jobs in any category
```python
job3 = Job('job3.submit')
job3.add_category("BigCPU")
mydag.add_job(job3)
mydag.set_maxjobs("BigCPU", 24)
```

The state of a job is saved to the dagfile object when add_job is called.  Therefore, adding further attributes to a job (vars, pre/post, parent) after a job has already been added to a dagfile object will have no affect:
```python
job5 = Job('job5.submit')
mydag.add_job(job5)
job5.add_var('mem', '20G') # This has no effect since the job was already added to the dagfile object
```

Example with output
-------------------
```python
# my_workflow.py
from pydagman.dagfile import Dagfile
from pydagman.job import Job

mydag = Dagfile()

job1 = Job('job1.submit', 'JOB1')
job1.add_var('mem', '20G')
job1.add_var('cpus', '12')
job1.retry(4)
mydag.add_job(job1)

job2 = Job('job2.submit', 'JOB2')
job2.add_var('mem', '4G')
job2.add_var('cpus', '2')
job2.retry(2)
job2.add_parent(job1)
mydag.add_job(job2)

job3 = Job('job3.submit', 'JOB3')
job3.add_pre('job3_pre.sh', '/tmp/JOB2', '/tmp/JOB3')
job3.add_var('mem', '4G')
job3.add_var('cpus', '2')
job3.retry(2)
job3.add_parent(job2)
mydag.add_job(job3)

job4 = Job('job4.submit', 'JOB4')
job4.add_pre('job4_pre.sh', '/tmp/JOB2', '/tmp/JOB4')
job4.add_var('mem', '4G')
job4.add_var('cpus', '2')
job4.retry(2)
job4.add_parent(job2)
mydag.add_job(job4)

mydag.save('my_workflow.dag')
```

```
# my_workflow.dag
JOB JOB1 job1.submit
VARS JOB1 mem="20G"
VARS JOB1 cpus="12"
RETRY JOB1 4

JOB JOB2 job2.submit
VARS JOB2 mem="4G"
VARS JOB2 cpus="2"
RETRY JOB2 2

JOB JOB3 job3.submit
SCRIPT PRE JOB3 job3_pre.sh /tmp/JOB2 /tmp/JOB3
VARS JOB3 mem="4G"
VARS JOB3 cpus="2"
RETRY JOB3 2

JOB JOB4 job4.submit
SCRIPT PRE JOB4 job4_pre.sh /tmp/JOB2 /tmp/JOB4
VARS JOB4 mem="4G"
VARS JOB4 cpus="2"
RETRY JOB4 2

PARENT JOB1 CHILD JOB2
PARENT JOB2 CHILD JOB3
PARENT JOB2 CHILD JOB4
```


TODO
----
Support the following advanced dagman directives:
* PRE-SKIP
* ABORT-DAG-ON
* PRIORITY
* CONFIG
