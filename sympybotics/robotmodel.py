# -*- coding: utf-8 -*-

###############################################################################
#  SymPyBotics: Symbolic Robotics Toolbox using Python and SymPy
#
#      Copyright (C) 2012, 2013 Cristóvão Sousa <crisjss@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL),
#  version 2 or any later version.  The full text of the GPL is available at:
#                  http://www.gnu.org/licenses/
###############################################################################

import sys
import sympy

from . import geometry
from . import kinematics
from . import dynamics
from . import symcode

def _fprint(x):
  print(x)
  sys.stdout.flush()

class RobotAllSymb(object):
  """Robot geometric, kinematic, and dynamic models in single symbolic expressions."""

  def __init__(self, rbtdef, usefricdyn=False):
    
    self.rbtdef = rbtdef
    self.dof = rbtdef.dof
    self.usefricdyn = usefricdyn
    
    self.geom = geometry.Geometry(self.rbtdef)
    self.kin = geometry.Geometry(self.rbtdef, self.geom)
    
    self.dyn = dynamics.Dynamics(self.rbtdef, self.geom, self.usefricdyn)
    self.dyn.gen_all()

  
class RobotDynCode(object):
  """Robot dynamic model in code form."""
  
  def __init__(self, rbtdef, usefricdyn=False):
    
    self.rbtdef = rbtdef
    self.dof = rbtdef.dof
    self.usefricdyn = usefricdyn
    
    self.geom = geometry.Geometry(self.rbtdef)
    self.kin = kinematics.Kinematics(self.rbtdef, self.geom)
    
    self.dyn = dynamics.Dynamics(self.rbtdef, self.geom, self.usefricdyn)
    
    subexprsmode = 'simple'
    
    _fprint('generating tau code')
    tau_se = symcode.subexprs.Subexprs(subexprsmode)
    self.dyn.gen_tau(tau_se.collect)
    self.tau_code  = (tau_se.subexprs, self.dyn.tau)
    
    _fprint('generating gravity term code')
    g_se = symcode.subexprs.Subexprs(subexprsmode)
    self.dyn.gen_gravterm(g_se.collect)
    self.g_code  = (g_se.subexprs, self.dyn.g)
    
    _fprint('generating Coriolisterm code')
    c_se = symcode.subexprs.Subexprs(subexprsmode)
    self.dyn.gen_ccfterm(c_se.collect)
    self.c_code  = (c_se.subexprs, self.dyn.c)
    
    _fprint('generating mass matrix code')
    M_se = symcode.subexprs.Subexprs(subexprsmode)
    self.dyn.gen_massmatrix(M_se.collect)
    self.M_code  = (M_se.subexprs, self.dyn.M)
    
    _fprint('generating regressor matrix code')
    H_se = symcode.subexprs.Subexprs(subexprsmode)
    self.dyn.gen_regressor(H_se.collect)
    self.H_code  = (H_se.subexprs, self.dyn.H)
    
    self._codes = ['tau_code', 'g_code', 'c_code', 'M_code', 'H_code']
    
    
  def gen_base_parms(self):
    
    _fprint('generating base parameters and regressor code')
    self.dyn.gen_base_parms()
    self.Hb_code  = (self.H_code[0], self.dyn.Hb)
    
    self._codes.append('Hb_code')


  def optimize_code(self):
    
    def optimize( code ):
      code = symcode.optimization.optim_dce_sup(code)
      code = symcode.optimization.optim_cp(code)
      return code
      
    for codename in self._codes:
      _fprint('optimizing %s'%codename)
      oldcode = getattr(self,codename)
      newcode = optimize(oldcode)
      setattr(self,codename,newcode)
    