"""
This module runs Scratch blocks on demand.
Basically it emulates Scratch in Pygame, hence the name.
"""
import sys
import os
import random
import pygame.time
import cairosvg
import io
import config


if not config.enableDebugMessages:
    sys.stderr = open(os.devnull, "w")
if not config.enableTerminalOutput:
    sys.stdout = open(os.devnull, "w")


HEIGHT = config.projectScreenHeight
WIDTH = config.projectScreenWidth

# Key maps to convert the key option in blocks to Pygame constants
KEY_MAPPING = {
    "up arrow"   : pygame.K_UP,
    "down arrow" : pygame.K_DOWN,
    "left arrow" : pygame.K_LEFT,
    "right arrow": pygame.K_RIGHT,
    "space"      : pygame.K_SPACE,
    "a"          : pygame.K_a,
    "b"          : pygame.K_b,
    "c"          : pygame.K_c,
    "d"          : pygame.K_d,
    "e"          : pygame.K_e,
    "f"          : pygame.K_f,
    "g"          : pygame.K_g,
    "h"          : pygame.K_h,
    "i"          : pygame.K_i,
    "j"          : pygame.K_j,
    "k"          : pygame.K_k,
    "l"          : pygame.K_l,
    "m"          : pygame.K_m,
    "n"          : pygame.K_n,
    "o"          : pygame.K_o,
    "p"          : pygame.K_p,
    "q"          : pygame.K_q,
    "r"          : pygame.K_r,
    "s"          : pygame.K_s,
    "t"          : pygame.K_t,
    "u"          : pygame.K_u,
    "v"          : pygame.K_v,
    "w"          : pygame.K_w,
    "x"          : pygame.K_x,
    "y"          : pygame.K_y,
    "z"          : pygame.K_z,
    "0"          : pygame.K_0,
    "1"          : pygame.K_1,
    "2"          : pygame.K_2,
    "3"          : pygame.K_3,
    "4"          : pygame.K_4,
    "5"          : pygame.K_5,
    "6"          : pygame.K_6,
    "7"          : pygame.K_7,
    "8"          : pygame.K_8,
    "9"          : pygame.K_9,

    # Scratch supports these keys internally
    "enter"      : pygame.K_RETURN,
    "<"          : pygame.K_LESS,
    ">"          : pygame.K_GREATER,
    "+"          : pygame.K_PLUS,
    "-"          : pygame.K_MINUS,
    "="          : pygame.K_EQUALS,
    "."          : pygame.K_PERIOD,
    ","          : pygame.K_COMMA,
    "%"          : pygame.K_PERCENT,
    "$"          : pygame.K_DOLLAR,
    "#"          : pygame.K_HASH,
    "@"          : pygame.K_AT,
    "!"          : pygame.K_EXCLAIM,
    "^"          : pygame.K_CARET,
    "&"          : pygame.K_AMPERSAND,
    "*"          : pygame.K_ASTERISK,
    "("          : pygame.K_LEFTPAREN,
    ")"          : pygame.K_RIGHTPAREN,
    "["          : pygame.K_LEFTBRACKET,
    "]"          : pygame.K_RIGHTBRACKET,
    "?"          : pygame.K_QUESTION,
    "\\"         : pygame.K_BACKSLASH,
    "/"          : pygame.K_SLASH,
    "'"          : pygame.K_QUOTE,
    "\""         : pygame.K_QUOTEDBL,
    "`"          : pygame.K_BACKQUOTE,

    # Scratch2Python only
    "backspace"  : pygame.K_BACKSPACE,
    "f1"         : pygame.K_F1,
    "f2"         : pygame.K_F2,
    "f3"         : pygame.K_F3,
    "f4"         : pygame.K_F4,
    "f5"         : pygame.K_F5,
    "f6"         : pygame.K_F6,
    "f7"         : pygame.K_F7,
    "f8"         : pygame.K_F8,
    "f9"         : pygame.K_F9,
    "f10"        : pygame.K_F10,
    "f11"        : pygame.K_F11,
    "f12"        : pygame.K_F12
}


# Load SVG
def loadSvg(svgBytes):
    newBytes = cairosvg.svg2png(bytestring=svgBytes)
    byteIo = io.BytesIO(newBytes)
    return pygame.image.load(byteIo)


# Refresh screen resolution
def refreshScreenResolution():
    global HEIGHT
    global WIDTH
    HEIGHT = config.projectScreenHeight
    WIDTH = config.projectScreenWidth


# Run the given block object
def execute(block, s, keys=[]):
    # Get block values
    opcode = block.opcode
    id = block.blockID
    blockRan = block.blockRan
    inputs = block.inputs
    fields = block.fields
    shadow = block.shadow
    nextBlock = None

    if opcode == "motion_gotoxy":  # go to x: () y: ()
        s.setXy(int(block.getInputValue("x")), int(block.getInputValue("y")))

    elif opcode == "motion_goto":
        nextBlock = block.getBlockInputValue("to")
        return s.target.blocks[nextBlock]

    elif opcode == "motion_goto_menu":
        if block.getFieldValue("to") == "_mouse_":  # go to [mouse pointer v]
            newX, newY = pygame.mouse.get_pos()
            newX = newX - WIDTH // 2
            newY = HEIGHT // 2 - newY
            s.setXy(newX, newY)
            return s.target.blocks[s.target.blocks[block.parent].next]

        elif block.getFieldValue("to") == "_random_":  # go to [random position v]
            minX = 0 - WIDTH // 2
            maxX = WIDTH // 2
            minY = 0 - HEIGHT // 2
            maxY = HEIGHT // 2
            newX, newY = (random.randint(minX, maxX), random.randint(minY, maxY))
            s.setXy(newX, newY)
            return s.target.blocks[s.target.blocks[block.parent].next]

    elif opcode == "motion_setx":  # set x to ()
        s.setXy(int(block.getInputValue("x")), s.y)

    elif opcode == "motion_changexby":  # change x by ( )
        s.setXyDelta(int(block.getInputValue("dx")), 0)

    elif opcode == "motion_sety":  # set y to ()
        s.setXy(s.x, int(block.getInputValue("y")))

    elif opcode == "motion_changeyby":  # change y by ()
        s.setXyDelta(0, int(block.getInputValue("dy")))

    elif opcode == "control_wait":  # wait () seconds
        block.screenRefresh = True
        if not block.waiting:
            # Get time delay and convert it to milliseconds
            block.timeDelay = int(round(float(float(block.getInputValue("duration"))) * 1000))
            block.waiting = True
            block.executionTime = 0
            print("DEBUG: Waiting for", block.timeDelay, "ms", file=sys.stderr)
        return block

    elif opcode == "event_whenflagclicked":  # when green flag clicked
        pass

    elif opcode == "event_whenkeypressed":
        # if not block.waiting:
        #     # Get time delay and convert it to milliseconds
        #     block.timeDelay = 500
        #     block.waiting = True
        #     block.executionTime = 0
        #     print("DEBUG: Waiting for", block.timeDelay, "ms")
        key = block.getFieldValue("key_option", lookIn=0)

        if key == "any":  # when key [any v] pressed
            print("DEBUG: Handling key", key, file=sys.stderr)
            if keys:
                print("DEBUG: Handling key", key, file=sys.stderr)
                for b in block.script:
                    s.target.blocks[b].blockRan = False
                nb = block  # s.target.blocks[block.next]
                nb.blockRan = False
                block.script.add(nb.blockID)
                while nb.next and nb.next != block.blockID:
                    nb.blockRan = False
                    nb.timeDelay = 0
                    nb.executionTime = 0
                    nb = s.target.blocks[nb.next]
                    block.script.add(nb.blockID)
                    if not nb.next:
                        nb.next = block.blockID
                nb.blockRan = False
                nextBlock = s.target.blocks[block.next]
                return nextBlock

        elif KEY_MAPPING[key] in keys and block.next:  # when key [. . . v] pressed
            print("DEBUG: Handling key", key, file=sys.stderr)
            for b in block.script:
                s.target.blocks[b].blockRan = False
            nb = block  # s.target.blocks[block.next]
            nb.blockRan = False
            block.script.add(nb.blockID)
            while nb.next and nb.next != block.blockID:
                nb.blockRan = False
                nb.timeDelay = 0
                nb.executionTime = 0
                nb = s.target.blocks[nb.next]
                block.script.add(nb.blockID)
                if not nb.next:
                    nb.next = block.blockID
            nb.blockRan = False
            nextBlock = s.target.blocks[block.next]
            return nextBlock

    elif opcode == "control_forever":  # forever {..}
        # Don't mark the loop as ran, and do a screen refresh
        block.blockRan = False
        block.screenRefresh = True

        # If there are blocks, get them
        if inputs["SUBSTACK"][1]:
            # No blocks will be flagged as ran inside a forever loop
            for b in block.substack:
                s.target.blocks[b].blockRan = False
            nextBlock = s.target.blocks[inputs["SUBSTACK"][1]]
            nb = s.target.blocks[inputs["SUBSTACK"][1]]
            block.substack.add(nb.blockID)
            while nb.next and nb.next != block.blockID:
                # TODO: Caution: Don't loop the program
                nb.blockRan = False
                nb.waiting = False
                nb.timeDelay = 0
                nb.executionTime = 0
                nb = s.target.blocks[nb.next]
                block.substack.add(nb.blockID)
            nb.next = block.blockID
            return nextBlock
    elif opcode == "procedures_call":
        if config.showSALogs:
            if block.proccode == "​​log​​ %s":  # Scratch Addons log ()
                print("PROJECT LOG:", block.getCustomInputValue(0), file=sys.stderr)
            elif block.proccode == "​​warn​​ %s":  # Scratch Addons warn ()
                print("PROJECT WARN:", block.getCustomInputValue(0), file=sys.stderr)
            elif block.proccode == "​​error​​ %s":  # Scratch Addons error ()
                print("PROJECT ERROR:", block.getCustomInputValue(0), file=sys.stderr)
    else:
        print("Unknown opcode:", opcode)

    # If there is a block below, return it
    if block.next:
        nextBlock = s.target.blocks[block.next]
    block.blockRan = True

    return nextBlock
