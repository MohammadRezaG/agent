# agent
agent is a service that can be used to run periodic tasks .

Agent runs on a separate thread and when the Agent is shutdown, it waits till all job currently is Running complete.

Inspired by this project https://github.com/sankalpjonn/timeloop

## Installation
```
copy all files and import agent
```

##creating options
```python
import  datetime
options = {
        'calculator': 'interval',
        'start_time': datetime.datetime.now(),
        'interval': 1
    }
```

## Using Agent

```python
import time

from agent import Agent

agent = Agent()


@agent.create_job_decorator(options=options, args=('i am massage',), name='dec1')
def sample_job_every_2s(massage, job):
    print(f'I am running whit massage {massage} and my Name is {job.name}')


@agent.create_job_decorator(options=options)
def sample_job_every_5s():
    print('I am running whiteout massage and name')


def sample_job_every_10s(massage, job):
    print(f'I am running whit massage {massage} and my Name is {job.name}')
agent.create_job(func = sample_job_every_10s, name='job2', options=options, args=('i am massage',))

#run agent whit :
agent.start()
```





## Author
* **Mohammad Reza Golesorkhi**
* **Ramin Jolfaei**

Email me with any queries: [mgol2077@outlook.com](mgol2013@gmail.com).
