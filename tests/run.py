"""
run.py [arg [...]]
"""

if __name__ == "__main__":
    import _setup_path_env
    _setup_path_env.run()
   
import poe_exp_after_dot as _poe_exp_after_dot

if __name__ == "__main__":
    import sys as _sys 
 
    _sys.exit(_poe_exp_after_dot.main(_sys.argv))