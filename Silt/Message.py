          
def messageWithSrc(src, msg):
    return "{}: {}".format(
        src,
        msg
     )


def messageWithPos(pos, msg):
    return "{}: [{}:{}] {}".format(
        pos.source, 
        pos.lineNum,
        pos.offset,
        msg
     )
