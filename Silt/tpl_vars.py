import architecture
from tpl_locationRoot import LocationRoot, NoLoc
from tpl_types import Type, NoType
from ci_symbol import Symbol


#from tpl_either import Either

# What's this for?
# Most computer langauages have a consistent interface for cinstants
# and variables. A functional language does not care, a constant is
# a function that returns itself. I'm beginning to think this is a key
# mark of a mid---high level language.
#
# You see, Assembly languages do care. Some machine code ops can take
# a constant (an immediate) some can take a location that is abstactedly
# a variable (e/g/ a register). Some ops only work with one or the 
# other, or only work with them in certain parameter positions.
#
# But it seems Rubble will be close enough to an assembly code to need
# to capture these distinctions. It needs to be able to say, function X
# can take VarOrConstant of a type e.g.
class Var(Symbol):
    def __init__(self, name, loc, tpe):
        assert isinstance(loc, LocationRoot), "Parameter not a LocRoot. loc: '{}'".format(loc)
        assert isinstance(tpe, Type), "Parameter not a Type. tpe: '{}'".format(tpe)
        # None is for loc. it's a big refactorr.
        super().__init__(name, tpe)
        self.loc = loc
        #self.tpe = tpe
        
        # Variables can be given a priority, for retaining on registers.
        # Priority is always the baseline of zero. It is 
        # updated from outside. See AutoStores for details.
        self.priority = 0
            
    # def value(self):
        # return self.loc.value()

    # def toStackIndex(self, b, index):
        # self.loc = self.loc.toStackIndex(b, index)

    # def toRegister(self, b, targetRegisterName):
        # self.loc = self.loc.toRegister(b, targetRegisterName)
                     
    def __repr__(self):
        return f"Var(name:{self.name}, loc:'{self.loc}', tpe:{self.tpe})"

    def __str__(self):
        return f"Var('{self.name}', {self.tpe})"

NoVar = Var("NoVar", NoLoc, NoType)


#? from this import, probably not the right place. Where is?
import tpl_locationRoot as Loc

class UpdateLocationBuilder():
    def __init__(self, arch):
        self.arch = arch
        
    def toLabel(self, var):
        assert (var.labelLoc), 'toLabel: This var was not a label? var:{}'.format(
            var
        )
        # No need to build anything, this is a compiler only scenario
        var.loc = var.loc.labelLoc
        
    def toRegister(self, b, var, dstRegisterName):
        loc = var.loc
        assert (dstRegisterName in self.arch['registers']), 'toRegister: Not a register? dstRegisterName:{}'.format(
            dstRegisterName
        )
        assert (not(isinstance(loc, Loc.LocationRegister)) or (var.loc.lid != dstRegisterName)), 'toRegister: Move to same register? var:{}, dstRegisterName:{}'.format(
            var,
            dstRegisterName
        )

        # build the move
        if (isinstance(loc, Loc.LocationLabel) or isinstance(loc, Loc.LocationRegister)):
            #? Should work for registers
            #? works for labels? If not....
            #b += 'lea {}, [{}]'.format(dstRegisterName, self.value())              
            b += "mov {} {}, {}".format(
                self.arch['ASMName'],
                dstRegisterName, 
                loc.lid
            )
        elif (isinstance(loc, Loc.LocationStack)):
            #? Should work for stack
            b += "mov {}, {} [rbp - {}]".format(
                dstRegisterName, 
                self.arch['ASMName'],
                loc.lid * self.arch['bytesize'],
            )
            
        # Now adapt the location
        if (loc.isAddressLoc):
            newLoc = Loc.RegisteredAddressX64(dstRegisterName) 
        else:
            newLoc = Loc.RegisterX64(dstRegisterName) 
        var.loc = newLoc
                    
    def toStack(self, b, var, slot):
        loc = var.loc
        assert(not(isinstance(loc, Loc.LocationStack))), 'toStack: Variable already on stack. var:{}'.format(
            var
        )

        # build the move
        #? Should work for labels and registers
        b += "mov {}[rbp - {}], {}".format(
            self.arch['ASMName'],
            slot * self.arch['bytesize'], 
            loc.lid
        )
        
        # Now adapt the location
        if (loc.isAddressLoc):
            newLoc = Loc.StackedAddressX64(slot) 
        else:
            newLoc = Loc.StackX64(slot) 
        var.loc = newLoc
