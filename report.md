# Experiment To Convert XGB models to branchless C++ code

Here are the results - running Google Test on isolated cpus on a bare metal server - 

![Branchless Code](/images/isolcpu_branchless.jpg)
The above is branchless code that takes roughly 2.9 us per inference on average

![Naive Code](/images/isolcpu_naive.jpg)
This is naive code tha takes roughly 1.8 us per inference on average.

We can see that the branchless code has a lot less branch misses as opposed to the naive code. 

----

## My own experiments to measure the number of cycles each inference takes - 

These are the results - 

![My experiments](/images/my_benchmark.jpg)

The average performance does decrease, but there is an increase in tail-end performance with a 15% speedup in p99.9 and the standard deviation, which is a proxy for jitter decreases by 4.9%

## Further Optimizations 

There's only really one issue with the branchless code that's causing it to perform worse than the naive code, it's that the number of instructions has increased (so has the IPC but not enough to make up for the increase).   
So, the focus, in my opinion, should be entirely on how we make the number of instructions smaller, maybe by clever grouping of terms or something, I don't really know at the moment.

## CI/CD pipeline - 
Added two yml scripts for automated testing 