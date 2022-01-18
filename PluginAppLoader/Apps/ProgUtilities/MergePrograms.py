# Merge selected program(s) into a new common program.
#
# Type help("robodk.robolink") or help("robodk.robomath") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html

from robodk import robolink as rlk

PROG_MERGE_NAME = "%s Merged"  # ex: MyProg Merged


def getMergedProg(progs, RDK):
    """Creates a new program from the specified programs."""

    # Delete previously generated programs of the same name
    new_prog_name = ''
    for prog in progs:
        new_prog_name += prog.Name() + " "
    new_prog_name = PROG_MERGE_NAME % new_prog_name.strip()

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


def mergeProgs(progs, prog_to):
    """
    Merge instructions from a list of progams to another program.
    """
    for prog_from in progs:
        print('Merging program: "' + prog_from.Name() + '" to "' + prog_to.Name() + '"')

        inst_count = prog_from.InstructionCount()
        for i in range(inst_count):
            instruction_dict = prog_from.setParam(i)
            print(' - Instruction: ' + str(instruction_dict))

            prog_to.setParam("Add", instruction_dict)


def runmain():
    RDK = rlk.Robolink()

    # Get the programs to merge
    programs = list(filter(lambda item: item.Type() == rlk.ITEM_TYPE_PROGRAM, RDK.Selection()))
    if len(programs) < 2:
        RDK.ShowMessage('Please select at least two programs.')
        return

    # Create a new empty program
    merged_prog = getMergedProg(programs, RDK)

    # Merge programs into the new program
    mergeProgs(programs, merged_prog)


# Important: leave the main function as runmain if you want to compile this app
if __name__ == "__main__":
    runmain()