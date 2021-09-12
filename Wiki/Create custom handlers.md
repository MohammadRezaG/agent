# Create custom time scheduler

if you want job execute in a custom way you mast create a custom time scheduler

in this example we create a custom interval function that behave like builtin

## Create custom interval function

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
#### note : job must be at the end

now how we use this ?

## using our custom_interval function
first or option must be like this

```python
    options = {
    'scheduler': 'custom',
    'custom_time_scheduler': custom_interval,
    'start_time': datetime.datetime.now(),
    'args': (1,),
}
```
first detriment scheduler 
`'scheduler': 'custom',`

in **`custom_time_scheduler`** we add the name of or function in this case **`custom_interval`**
#### note : do not use `()` in Front of function name
after that we must add **start_time** and **args**

# Create custom FunctinoJob Fail Handler
this handler calls after job has failed or raise an error

in this example we crate a custom FunctinoJob Fail Handler

```python

```