import architecture
from tpl_locationRoot import LocationRoot, NoLoc
from tpl_types import Type, NoType

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
#
# Value(Bit64)
#
# Or not,
#
# Constant(StrASCII)
#
# or
#
# Var(Bit64)
#
# No hang on, the input type is irrelevant. int, float, str will do
# But the varOrConstant
# So we need something like 
# StrConstant() or
# We could even do with it being based on location
# RegVar or String
# And we need Arrays... lists?
# How are we going to do that?

# At first I was reluctant to type further than using the  
# types from the language the parser--builder is written in. It means
# a wrap, and I don't like wraps. But without that, we can't do the
# type checking of args. Further, with that the parserBuilder can then
# use a consistent interface for code building. So here it it is, the 
# Value class. 

        
#! this tangle of Base and Var needs fixing.
# will affect syn_arg_tests also
# class Base():

    # def value(self):
        # return self.loc.value()

    # def toStackIndex(self, b, index):
        # self.loc = self.loc.toStackIndex(b, index)

    # def toRegister(self, b, targetRegisterName):
        # self.loc = self.loc.toRegister(b, targetRegisterName)
                     
    # def __repr__(self):
        # return "Var(loc:'{}', tpe:{})".format(
            # self.loc,
            # self.tpe
        # )

    # def __str__(self):
        # return "Var({}, {})".format(
            # self.loc.lid,
            # self.tpe
        # )



class Var():
    def __init__(self, loc, tpe):
        assert isinstance(loc, LocationRoot), "Parameter not a LocRoot. loc: '{}'".format(loc)
        assert isinstance(tpe, Type), "Parameter not a Type. tpe: '{}'".format(tpe)
        self.loc = loc
        self.tpe = tpe
        
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
        return "Var(loc:'{}', tpe:{})".format(
            self.loc,
            self.tpe
        )

    def __str__(self):
        return "Var('{}', {})".format(
            self.loc.lid,
            self.tpe
        )

NoVar = Var(NoLoc, NoType)


#? from this import, probably not the right place. Where is?
import tpl_locationRoot as Loc

class UpdateLocationBuilder():
    def __init__(self, arch):
        self.arch = arch
        
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
        elif (isinstance(loc, LocationStack)):
            #? Should work for stack
            b += "mov {}, {} [rbp - {}]".format(
                dstRegisterName, 
                self.arch['ASMName'],
                self.lid * self.arch['bytesize'],
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
