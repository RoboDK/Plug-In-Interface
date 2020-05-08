#ifndef CHIP8CORE_H
#define CHIP8CORE_H
#include <irobodk.h>

void chip8Init(RoboDK*);
void chip8EmulateCycle();
void chip8EmulationLoop();
void chip8EndEmulationLoop();
void chip8UpdateButtons(bool *input);
void chip8Render(RoboDK *RDK,Item);
void chip8LoadFile(QByteArray);

#endif // CHIP8CORE_H
