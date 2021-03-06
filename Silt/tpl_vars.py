import architecture
from tpl_locationRoot import LocationRootX64
from tpl_types import Type
from tpl_either import Either

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
class Base():

    def value(self):
        return self.loc.value()

    def toStackIndex(self, b, index):
        self.loc = self.loc.toStackIndex(b, index)

    def toRegister(self, b, targetRegisterName):
        self.loc = self.loc.toRegister(b, targetRegisterName)

    # def toCodeValue(self):
        # '''
        # Build a snippet of code to access the var.
        # This acesses to top-level type of any goven tpye tree. In the 
        # case of singular types, it will access the value directly. In
        # the case of a container, it returns the container. To access  
        # values in a container, a path is needed. 
        # This method should always succeed???
        # For access to containers see accessBPathuilder()
        # '''
        # return self.loc.value()

    # def toCodeAddress(self):
        # '''
        # Build a snippet of code to access the var.
        # This acesses to top-level tpye of any goven tpye tree. In the 
        # case of singular types, it will access the value directly. In
        # the case of a container, it returns the container. To access  
        # values in a container, a path is needed. 
        # This method should always succeed???
        # For access to containers see accessBPathuilder()
        # '''
        # return self.loc.address()
        
    # def accessPartialDeep(self):
        # '''
        # Build a snippet of code to access a value in a var.
        # This accesses a position in a type tree. To do this, it needs a 
        # path. The method may error, refusing direct access if the path
        # os too deep for the architecture to handle.
        # For simple acess to singular types, see accessBuilder()
        # '''
        # return NotImplementedError()
                
    def __repr__(self):
        return "Var(loc:'{}', tpe:{})".format(
            self.loc,
            self.tpe
        )

    def __str__(self):
        return "Var({})".format(
            self.loc.lid,
        )

class Var(Base):
    def __init__(self, loc, tpe):
        assert isinstance(loc, LocationRootX64), "Parameter not a LocRoot. loc: '{}'".format(loc)
        assert isinstance(tpe, Type), "Parameter not a Type. tpe: '{}'".format(tpe)
        self.loc = loc
        self.tpe = tpe
                        
            

    
    
#x        
# class RegX64(Base):
    # def __init__(self, register, tpe):
        # self.loc = LocRoot.RegisterX64(register)
        # self.tpe = tpe

    # # def accessMk(self):
        # # # registers represent assembler-driven addresses.
        # # # They do not need address syntax  
        # # return self.loc.lid
    
    # def accessDeepMk(self, path):
        # return '[' + self.loc.lid + '+' + str(self.tpe.offsetDeep(path)) + ']'   

# def RegX64Either(register, tpe):
    # locEither = LocRoot.RegisterX64Either(register)
    # varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    # return varEither
        
        
#x        
# class RegAddrX64(Base):
    # def __init__(self, register, tpe):
        # self.loc = LocRoot.RegisteredAddressX64(register)
        # self.tpe = tpe        
        
# def RegAddrX64Either(register, tpe):
    # locEither = LocRoot.RegisteredAddressX64Either(register)
    # varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    # return varEither
    
    
#x            
# class StackX64(Base):
    # def __init__(self, index, tpe):
        # self.loc = LocRoot.StackX64(index)
        # self.tpe = tpe

    # # def accessMk(self): 
        # # return '[rbp -' + str(self.loc.lid)  + ']' 
    
    # def accessDeepMk(self, path): 
        # return '[rbp -' + str(self.loc.lid + self.tpe.offsetDeep(path)) + ']' 

# def StackX64Either(index, tpe):
    # locEither = LocRoot.StackX64Either(index)
    # varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    # return varEither


        
# def StackAddrX64Either(index, tpe):
    # locEither = LocRoot.StackedAddressX64Either(index)
    # varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    # return varEither
