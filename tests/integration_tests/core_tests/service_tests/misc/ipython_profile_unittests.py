# IPython log file

# the unittests were run with a '-m cProfile -o profile.out TEST_SCRIPT' interpreter options
import pstats
p = pstats.Stats('profile.out')
p.strip_dirs().sort_stats(-1).print_stats()
#[Out]# <pstats.Stats instance at 0x108b96e60>
p.sort_stats('cumulative').print_stats(50)
#[Out]# <pstats.Stats instance at 0x108b96e60>
p.sort_stats('time').print_stats(50)
#[Out]# <pstats.Stats instance at 0x108b96e60>

