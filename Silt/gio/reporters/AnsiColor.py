## Text styling for terminals. 
# To turn on reverse with bold style and
# then turn off styling embed,
#   println(s"${REVERSED}${BOLD}Hello 1979!${RESET}")

BLACK      = "\u001b[30m"

# Foreground color for ANSI red
# @group color-red
RED        = "\u001b[31m"

# Foreground color for ANSI green
# @group color-green
GREEN      = "\u001b[32m"

# Foreground color for ANSI yellow
# @group color-yellow
YELLOW     = "\u001b[33m"

# Foreground color for ANSI blue
# @group color-blue
BLUE       = "\u001b[34m"

# Foreground color for ANSI magenta
# @group color-magenta
MAGENTA    = "\u001b[35m"

# Foreground color for ANSI cyan
# @group color-cyan
CYAN       = "\u001b[36m"

# Foreground color for ANSI white
# @group color-white
WHITE      = "\u001b[37m"


# Background color for ANSI black
# @group color-black
BLACK_B    = "\u001b[40m"

# Background color for ANSI red
# @group color-red
RED_B      = "\u001b[41m"

# Background color for ANSI green
# @group color-green
GREEN_B    = "\u001b[42m"

# Background color for ANSI yellow
# @group color-yellow
YELLOW_B   = "\u001b[43m"

# Background color for ANSI blue
# @group color-blue
BLUE_B     = "\u001b[44m"

# Background color for ANSI magenta
# @group color-magenta
MAGENTA_B  = "\u001b[45m"

# Background color for ANSI cyan
# @group color-cyan
CYAN_B     = "\u001b[46m"

# Background color for ANSI white
# @group color-white
WHITE_B    = "\u001b[47m"


# Reset ANSI styles
# @group style-control
RESET      = "\u001b[0m"

# ANSI bold
# @group style-control
BOLD       = "\u001b[1m"

# ANSI underlines
# @group style-control
UNDERLINED = "\u001b[4m"

# ANSI blink
# @group style-control
BLINK      = "\u001b[5m"

# ANSI reversed
# @group style-control
REVERSED   = "\u001b[7m"

# ANSI invisible
# @group style-control
INVISIBLE  = "\u001b[8m"


