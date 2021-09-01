# Create custom interval function

```python  
  def custom_interval(interval, job):

        if job.next_run_time is None:
            try:
                r = job.options['start_time']
            except KeyError:
                raise KeyError('start_time not fond')
        else:
            r = job.next_run_time + datetime.timedelta(seconds=interval)
        print('this is custom interval returning {}'.format(str(r)))
        return r

```