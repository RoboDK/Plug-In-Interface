# Expand program calls of the selected program(s) into new program(s).
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink

PROG_EXPAND_NAME = "%s Expanded"  # ex: MyProg Expanded


def getExpandedProg(prog, RDK):
    """Creates a new program from the specified program."""

    # Delete previously generated programs of the same name
    new_prog_name = PROG_EXPAND_NAME % prog.Name()
    new_prog = RDK.Item(new_prog_name, rlk.ITEM_TYPE_PROGRAM)
    if new_prog.Valid() and new_prog.Name() == new_prog_name:
        new_prog.Delete()

    # Create a new program
    new_prog = RDK.AddProgram(new_prog_name)
    if not new_prog.Valid():
        new_prog.Delete()
        raise
    new_prog.setParent(prog.Parent())
    new_prog.ShowInstructions()
    return new_prog


def expandProg(prog_from, prog_to, RDK, recurse=True, root=None):
    """
    Inline all instructions from a program to another program.
    For recursive calls only, the initial root program must be provided to avoid loopholes.
    """

    print('Expanding program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"')

    if recurse and root == prog_from:
        raise Exception("Attempting to expand %s, which recursively calls itself in %s" % (root.Name(), prog_to.Name()))

    inst_count = prog_from.InstructionCount()
    for i in range(inst_count):
        instruction_dict = prog_from.setParam(i)
        print(' - Instruction: ' + str(instruction_dict))

        if instruction_dict['Type'] == robolink.INS_TYPE_CODE and recurse:
            sub_prog = RDK.Item(instruction_dict['Code'], robolink.ITEM_TYPE_PROGRAM)
            if sub_prog.Valid():
                expandProg(sub_prog, prog_to, RDK, True, prog_from if root is None else root)
                continue  # continue, as program calls to non-program are valid

        prog_to.setParam("Add", instruction_dict)


def runmain():
    RDK = robolink.Robolink()

    # Get the programs to expand
    programs = list(filter(lambda item: item.Type() == robolink.ITEM_TYPE_PROGRAM, RDK.Selection()))
    if len(programs) < 1:
        RDK.ShowMessage('Please select at least one program.')
        return

    for program in programs:
        # Create a new empty program
        exp_prog = getExpandedProg(program, RDK)

        # Inline any sub programs into the new program
        expandProg(program, exp_prog, RDK, True)


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()