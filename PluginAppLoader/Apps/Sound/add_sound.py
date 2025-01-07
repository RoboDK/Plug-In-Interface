import os
import zlib

from pathlib import Path
from robodk import robolink, robomath, roboapps

robolink.import_install("PySide2")
from PySide2 import QtCore, QtGui, QtWidgets


class SoundApplication:
    RDK = None
    tools = None

    app = None
    window = None

    combo_instruction = None
    combo_program = None
    combo_sound = None
    combo_object = None
    check_loop = None
    edit_repeat = None
    slider_volume_left = None
    edit_volume_left = None
    slider_volume_right = None
    edit_volume_right = None

    programs = []
    bindings = []

    def __init__(self):
        self.RDK = robolink.Robolink()

        self.app = roboapps.get_qt_app()

        self.window = QtWidgets.QDialog()
        self.window.setWindowTitle("Add Sound Instruction")
        self.window.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        content = QtWidgets.QWidget()
        self.ui_create_form(content)

        button_add = QtWidgets.QPushButton()
        button_add.setText("Add")
        button_add.clicked.connect(self.add_clicked)

        button_cancel = QtWidgets.QPushButton()
        button_cancel.setText("Cancel")
        button_cancel.setDefault(True)
        button_cancel.clicked.connect(self.window.close)

        layout_footer = QtWidgets.QHBoxLayout()
        layout_footer.setContentsMargins(0, 0, 0, 0)
        layout_footer.addStretch()
        layout_footer.addWidget(button_add)
        layout_footer.addWidget(button_cancel)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(content)
        layout.addLayout(layout_footer)

        self.window.setLayout(layout)
        self.window.update()

        self.update_internal_data()

        content.adjustSize()
        self.window.adjustSize()

    def ui_create_form(self, parent):
        self.combo_instruction = QtWidgets.QComboBox()
        self.combo_instruction.addItem("Play Sound (Blocking)")
        self.combo_instruction.addItem("Start Playing a Sound")
        self.combo_instruction.addItem("Wait for the End of Playback")
        self.combo_instruction.addItem("Stop Playing a Sound")
        self.combo_instruction.addItem("Stop Playing All Sounds")
        self.combo_instruction.currentIndexChanged.connect(self.instruction_changed)

        self.combo_program = QtWidgets.QComboBox()
        self.combo_sound = QtWidgets.QComboBox()
        self.combo_object = QtWidgets.QComboBox()
        self.combo_object.currentIndexChanged.connect(self.object_changed)

        self.edit_repeat = QtWidgets.QSpinBox()
        self.edit_repeat.setRange(0, 1000)

        self.check_loop = QtWidgets.QCheckBox()
        self.check_loop.setText("Loop")
        self.check_loop.stateChanged.connect(self.edit_repeat.setDisabled)

        self.slider_volume_left = QtWidgets.QSlider()
        self.slider_volume_left.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.slider_volume_left.setRange(0, 100)
        self.edit_volume_left = QtWidgets.QSpinBox()
        self.edit_volume_left.setRange(0, 100)
        self.edit_volume_left.setSuffix("%")
        self.slider_volume_left.valueChanged.connect(self.edit_volume_left.setValue)
        self.edit_volume_left.valueChanged.connect(self.slider_volume_left.setValue)

        self.slider_volume_right = QtWidgets.QSlider()
        self.slider_volume_right.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.slider_volume_right.setRange(0, 100)
        self.edit_volume_right = QtWidgets.QSpinBox()
        self.edit_volume_right.setRange(0, 100)
        self.edit_volume_right.setSuffix("%")
        self.slider_volume_right.valueChanged.connect(self.edit_volume_right.setValue)
        self.edit_volume_right.valueChanged.connect(self.slider_volume_right.setValue)

        layout_form = QtWidgets.QFormLayout(parent)
        layout_form.setHorizontalSpacing(15)
        layout_form.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)

        layout_form.addRow("Instruction", self.combo_instruction)
        layout_form.addRow("Robot Program", self.combo_program)
        layout_form.addRow("Sound File", self.combo_sound)
        layout_form.addRow("Bind to", self.combo_object)

        layout_form.addRow("Repeats", self.edit_repeat)
        layout_form.addRow("", self.check_loop)

        layout_form.addRow("Volume Left", self.slider_volume_left)
        layout_form.addRow("", self.edit_volume_left)

        layout_form.addRow("Volume Right", self.slider_volume_right)
        layout_form.addRow("", self.edit_volume_right)


    def update_internal_data(self):
        self.programs = self.RDK.ItemList(robolink.ITEM_TYPE_PROGRAM)
        if len(self.programs) > 0:
            for program in self.programs:
                self.combo_program.addItem(program.Name())
        else:
            self.combo_program.addItem("New Program")
            self.combo_program.setDisabled(True)

        current_folder = Path(__file__).absolute().parent
        sound_folder = current_folder / "sounds"
        if not sound_folder.exists() or not sound_folder.is_dir():
            sound_folder = current_folder.parent / "sounds"
        
        if sound_folder.exists() and sound_folder.is_dir():
            self.combo_sound.addItems([f.name for f in sound_folder.glob("*.*")])

        robots = self.RDK.ItemList(robolink.ITEM_TYPE_ROBOT)
        frames = self.RDK.ItemList(robolink.ITEM_TYPE_FRAME)
        tools = self.RDK.ItemList(robolink.ITEM_TYPE_TOOL)
        objects = self.RDK.ItemList(robolink.ITEM_TYPE_OBJECT)

        self.bindings = [None] + robots + frames + tools + objects
        self.combo_object.addItem("Nothing")
        self.combo_object.addItems(["[robot] " + i.Name() for i in robots])
        self.combo_object.addItems(["[frame] " + i.Name() for i in frames])
        self.combo_object.addItems(["[tool] " + i.Name() for i in tools])
        self.combo_object.addItems(["[object] " + i.Name() for i in objects])

        for binding in self.bindings:
            if not binding:
                continue
            suid = binding.getParam("SUID")
            if not suid:
                suid = binding.Name() + str(binding.item)
                suid = zlib.crc32(suid.encode('utf-8')).to_bytes(4, 'little')
                binding.setParam("SUID", suid)

        self.edit_volume_left.setValue(100)
        self.edit_volume_right.setValue(100)
        self.instruction_changed()
        self.object_changed()


    def instruction_changed(self):
        if self.combo_instruction.currentIndex() == 0:
            self.check_loop.setDisabled(True)
            self.edit_repeat.setEnabled(True)
        else:
            self.check_loop.setEnabled(True)
            self.edit_repeat.setDisabled(self.check_loop.isChecked())

    def object_changed(self):
        if self.combo_object.currentIndex() == 0:
            self.slider_volume_left.setEnabled(True)
            self.slider_volume_right.setEnabled(True)
            self.edit_volume_left.setEnabled(True)
            self.edit_volume_right.setEnabled(True)
        else:
            self.slider_volume_left.setDisabled(True)
            self.slider_volume_right.setDisabled(True)
            self.edit_volume_left.setDisabled(True)
            self.edit_volume_right.setDisabled(True)
    
    def add_clicked(self):
        filename = "play_sound"
        scripts = self.RDK.ItemList(robolink.ITEM_TYPE_PROGRAM_PYTHON, True)
        if filename not in scripts:
            current_folder = Path(__file__).absolute().parent
            file_path = current_folder / f"{filename}.py"
            if not file_path.exists():
                file_path = current_folder.parent / f"{filename}.py"
            self.RDK.AddFile(str(file_path))

        index = 0
        binding = self.bindings[self.combo_object.currentIndex()]
        if binding:
            suid = binding.getParam("SUID")
            if suid:
                index = int.from_bytes(suid, 'little')

        filename = self.combo_sound.currentText()

        command = "PlayBlocking"
        if self.combo_instruction.currentIndex() == 1:
            command = "Play"
        elif self.combo_instruction.currentIndex() == 2:
            command = "Status"
        elif self.combo_instruction.currentIndex() == 3:
            command = "Stop"
        elif self.combo_instruction.currentIndex() == 4:
            command = "StopAll"

        repeat = self.edit_repeat.value()
        if self.combo_instruction.currentIndex() > 0 and self.check_loop.isChecked():
            repeat = -1

        left_volume = float(self.edit_volume_left.value()) / 100;
        right_volume = float(self.edit_volume_right.value()) / 100;

        if len(self.programs) > 0:
            program = self.programs[self.combo_program.currentIndex()]
        else:
            program = self.RDK.AddProgram("Prog1")
            if program:
                self.programs.append(program)
                self.combo_program.setItemText(0, program.Name())
                self.combo_program.setEnabled(True)
        
        program.RunInstruction(f"play_sound({index},{filename},{command},{repeat},{left_volume},{right_volume})")


    def run(self):
        self.window.show()
        self.app.exec_()


def runmain():
    app = SoundApplication()
    app.run()


if __name__ == "__main__":
    runmain()