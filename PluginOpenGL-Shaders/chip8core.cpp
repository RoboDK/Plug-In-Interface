/// This module emulates the Chip 8 virtual machine
/// See http://devernay.free.fr/hacks/chip8/C8TECH10.HTM for the technical documentation of the virtual sytem
/// The core logic is contained within chip8EmulationLoop

#include <stdint.h>
#include <stdlib.h>
#include <irobodk.h>
#include <iitem.h>
#include <QThread> // only for uSleep
#include <QElapsedTimer> //Used for timing control


RoboDK *RDK; ////To trigger updates in robodk

/// Chip8 binary font 5 * 4 pixel
uint8_t chip8Fontset[80] =
{
  0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
  0x20, 0x60, 0x20, 0x20, 0x70, // 1
  0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
  0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
  0x90, 0x90, 0xF0, 0x10, 0x10, // 4
  0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
  0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
  0xF0, 0x10, 0x20, 0x40, 0x40, // 7
  0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
  0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
  0xF0, 0x90, 0xF0, 0x90, 0x90, // A
  0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
  0xF0, 0x80, 0x80, 0x80, 0xF0, // C
  0xE0, 0x90, 0x90, 0x90, 0xE0, // D
  0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
  0xF0, 0x80, 0xF0, 0x80, 0x80  // F
};

//64*32
#define PIXEL_COUNT 2048

void chip8LoadFile(QByteArray inputData);

//Chip 8 virtual machine variables
uint8_t  ram[4096];              //The virtual systems main memory
bool     chip8VRAM[PIXEL_COUNT]; //64*32, each bool represents if a pixel is on or off

uint16_t regPC;
uint16_t regI;
uint8_t  regDelayTimer;
uint8_t  regSoundTimer;
uint8_t  regSP;
uint16_t callStack[16];
uint8_t  regs[16];
bool     regButtons[16];

//Flags to indicate that the screen or buttons have changed
bool     fRender;
bool     fPressed;

///Initialise all the chip8 registers and memory
void chip8Init(RoboDK *inRDK) {
  RDK = inRDK;
  regPC = 0x0200;
  regI = 0;
  regSP = 0;
  regDelayTimer = 0;
  regSoundTimer = 0;
  fRender = false;

  for (int i = 0; i < sizeof(ram); i++) {
    ram[i] = 0;
  }

  for (int i = 0; i < sizeof(chip8VRAM); i++) {
    chip8VRAM[i] = false;
  }

  /*
  for (int i = 0; i < 2048; i++) {
    chip8VRAM[i] = (rand() & 1) == 1;
  }*/

  for (int i = 0; i < sizeof(regs); i++) {
    regs[i] = 0;
    regButtons[i] = false;
    callStack[i] = 0;
  }

  for (int i = 0; i < sizeof(chip8Fontset); i++) {
    ram[i] = chip8Fontset[i];
  }
}

///Emulates a chip8 instruction cycle
void chip8EmulateCycle() {
  uint16_t curOpcode;
  uint8_t curNibble0;
  uint8_t curNibble1;
  uint8_t curNibble2;
  uint8_t curNibble3;
  uint8_t curLowByte;
  uint8_t spriteX;
  uint8_t spriteY;

  curOpcode = (ram[regPC] << 8) | (ram[regPC+1]);
  curNibble0 = (curOpcode & 0x000F);
  curNibble1 = (curOpcode & 0x00F0) >> 4;
  curNibble2 = (curOpcode & 0x0F00) >> 8;
  curNibble3 = (curOpcode & 0xF000) >> 12;
  curLowByte = curOpcode & 0x00FF;
  //qDebug() << "RegPC";
  //QString valueInHex  = QString("%1").arg(curOpcode , 0, 16);
  //QString valueInHex2 = QString("%1").arg(regPC , 0, 16);

  //qDebug() << valueInHex2;
  //qDebug() << valueInHex;

  if (curOpcode == 0x0000) {
    return;
  }


  switch (curNibble3) {
    case 0x0:
      if (curNibble0 == 0x0) {
          for (int i = 0; i < sizeof(chip8VRAM); i++) {
            chip8VRAM[i] = 0;
          }
          fRender = true;
      }
      else if (curNibble1 == 0xE) {
        regSP--;
        regPC = callStack[regSP];
      }
      break;
    case 0x1:
      regPC = curOpcode & 0x0FFF;
      return;
      break;
    case 0x2:
      callStack[regSP] = regPC;
      regSP++;
      regPC = curOpcode & 0x0FFF;
      return;
      break;
    case 0x3:
      if (regs[curNibble2] == curLowByte) {
        regPC++;
        regPC++;
      }
      break;
    case 0x4:
      if (regs[curNibble2] != curLowByte) {
        regPC++;
        regPC++;
      }
      break;
    case 0x5:
      if (regs[curNibble2] == regs[curNibble1]) {
        regPC++;
        regPC++;
      }
      break;
    case 0x6:
      regs[curNibble2] = curLowByte;
      break;
    case 0x7:
      regs[curNibble2] += curLowByte;
      break;
    case 0x8:
     switch(curNibble0) {
       case 0x0:
         regs[curNibble2] = regs[curNibble1];
         break;
       case 0x1:
         regs[curNibble2] |= regs[curNibble1];
         break;
       case 0x2:
         regs[curNibble2] &= regs[curNibble1];
         break;
       case 0x3:
         regs[curNibble2] ^= regs[curNibble1];
         break;
       case 0x4:
         regs[curNibble2] += regs[curNibble1];
         regs[0xF] = ((regs[curNibble2] + regs[curNibble1]) & 0x100) >> 8;
         break;
       case 0x5:
         regs[curNibble2] -= regs[curNibble1];
         regs[0xF] = ((regs[curNibble2] - regs[curNibble1]) & 0x100) >> 8;
         break;
       case 0x6:
         regs[0xF] = regs[curNibble2] & 0x1;
         regs[curNibble2] >>= 1;
         break;
       case 0x7:
         regs[curNibble2] = regs[curNibble1] - regs[curNibble2];
         regs[0xF] = ((regs[curNibble1] - regs[curNibble2]) & 0x100) >> 8;
         break;
       case 0xE:
         regs[0xF] = regs[curNibble2] >> 7;
         regs[curNibble2] <<= 1;
         break;
     }
     break;
    case 0x9:
      if (regs[curNibble2] != regs[curNibble1]) {
        regPC++;
        regPC++;
      }
     break;
    case 0xA:
      regI = curOpcode & 0x0FFF;
      break;
    case 0xB:
      regPC = (curOpcode & 0x0FFF) + regs[0x0];
      return;
      break;
    case 0xC:
      regs[curNibble2] = (rand() % 0xFF) & curLowByte;
      break;
    case 0xD:
      uint8_t    curByteInRAM;
      regs[0xF] = 0;
      spriteX = regs[curNibble2];
      spriteY = regs[curNibble1];
      for (int i = 0; i < curNibble0; i++) {
        curByteInRAM = ram[regI+i];
        for (int j = 0; j < 8; j++) {
          if ((curByteInRAM & (0x80 >> j)) != 0) {
              regs[0xF] |= chip8VRAM[spriteX+j+(i+spriteY)*64] & 0x01;
              chip8VRAM[spriteX+j+((i+spriteY)*64)] ^= 1;
          }
        }
      }
      fRender = true;
      break;
    case 0xE:
      if (curLowByte == 0x9E) {
          if (regButtons[regs[curNibble2]] == true) {
              regPC++;
              regPC++;
          }
      } else if (curLowByte == 0xA1) {
          if (regButtons[regs[curNibble2]] == false) {
              regPC++;
              regPC++;
          }
      }
      break;
    case 0xF:
      switch (curLowByte) {
        case 0x07:
          regs[curNibble2] = regDelayTimer;
          break;
        case 0x0A:
          fPressed = false;
          for (uint8_t i = 0; i < sizeof(regButtons); i++) {
            if(regButtons[i] == true) {
                regs[curNibble2] = i;
                fPressed = true;
            }
          }
          if (fPressed == false) {
            regPC--;
            regPC--;
          }
          break;
        case 0x15:
          regDelayTimer = regs[curNibble2];
          break;
        case 0x18:
          regSoundTimer = regs[curNibble2];
          break;
        case 0x1E:
          regs[0xF] = ((regI+regs[curNibble2])>>8) & 0x001;
          regI += regs[curNibble2];
          break;
        case 0x29:
          regI = regs[curNibble2]*5;
          break;
        case 0x33:
          ram[regI + 0] = (regs[curNibble2] / 100);
          ram[regI + 1] = (regs[curNibble2] / 10 ) % 10;
          ram[regI + 2] = (regs[curNibble2] % 100) % 10;
          break;
        case 0x55:
          for (int i = 0; i < curNibble2+1; i++) {
              ram[regI + i] = regs[i];
          }
          regI += curNibble2+ 1;
          break;
        case 0x65:
          for (int i = 0; i < curNibble2+1; i++) {
              regs[i] = ram[regI + i];
          }
          regI += curNibble2 + 1;
          break;
      }
      break;
    default:
       regPC--;
       regPC--;
       break;
  }
  regPC++;
  regPC++;
  return;
}

///Function to set a flag to end the emulation thread
static bool chip8ThreadRunning = false;
void chip8EndEmulationLoop() {
    chip8ThreadRunning = false;
}

///Loop to emulate the chip8, run's in it's own thread
void chip8EmulationLoop() {
    chip8ThreadRunning = true;
    bool updateTimers = false;
    QElapsedTimer timer;
    timer.start();


    //QThread::msleep(1000); //Wait for robodk to finish starting up

    while(chip8ThreadRunning) {
        updateTimers = !updateTimers;

        chip8EmulateCycle();
        QThread::usleep((1/1000)*1000); //500Hz


        //60 Hz
        if (timer.elapsed() > ((1.0/60.0)*1000)) {
            timer.start();
            if ((regDelayTimer > 0)) {
                regDelayTimer--;
            }
            if ((regSoundTimer > 0)) {
                regSoundTimer--;
            }
        }


        if (fRender == true) {
            RDK->Render();
            fRender = false;
        }
    }
}

///Function to update the state of the 16 buttons
void chip8UpdateButtons(bool *inputStates) {
    for (int i = 0; i < 16; i++) {
        regButtons[i] = inputStates[i];
    }
}

///Function to load a rom file
void chip8LoadFile(QByteArray inputData) {
    if (inputData != nullptr) {
        for (int i = 0; i < inputData.size(); i++) {
            uint8_t curByte = (uint8_t)inputData.at(i);
            ram[i+0x0200] = curByte;
        }
    }
}

/// Copy 2 triangles representing the square xyPixel in to the ptr buffer (triangles and normals)
void CopyPixel2Buffer(int xPixel, int yPixel, double *ptr_vtx, double *ptr_normals) {

    // size per pixel in mm
    double xSize = 5;
    double ySize = 5;


    double xPos = +xSize*xPixel;
    double yPos = ySize*32 - ySize*yPixel;
    double zPos = 0;


    double bottomHalf[] = {xPos,     yPos,zPos,
                          xPos+xSize,yPos,zPos,
                          xPos,yPos-ySize,zPos,
                          };
    double topHalf[] = {xPos+xSize,yPos-ySize,zPos,
                          xPos+xSize,yPos,zPos,
                          xPos,yPos-ySize,zPos,
                          };

    // copy vertex
    COPY3(ptr_vtx, bottomHalf);
    COPY3(ptr_vtx+3, bottomHalf+3);
    COPY3(ptr_vtx+6, bottomHalf+6);
    COPY3(ptr_vtx+9, topHalf);
    COPY3(ptr_vtx+12, topHalf+3);
    COPY3(ptr_vtx+15, topHalf+6);

    // copy normals
    double normals[] = {0.0,0.0,1.0};
    for (int i=0; i<6; i++) {
        COPY3(ptr_normals+i*3, normals);
    }
}


///Function to Update the entire chip8 display in robodk
void chip8Render(RoboDK *RDK,Item ScreenRef) {
    // one vertex has 3 coordinates (xyz)
    #define CoordsPerVertex 3
    // one trinagle has 3 coordinates (p1,p2,p3)
    #define VertexPerTriangle 3

    // each triangle has 3*3 coordinates
    #define CoordsPerTriangle CoordsPerVertex*VertexPerTriangle

    // each pixel has 2 trinagles
    #define TrianglesPerPixel 2

    // 2 triangles per pixel
    #define CoordsPerPixel CoordsPerTriangle*TrianglesPerPixel

    fRender = true;
    int debug = 0;

    int count_triangles_On = 0;
    int count_triangles_Off = 0;


    // triangle count is 2*PIXEL_COUNT
    // each triangle has 3 points, each point has 3 coordinates
    static double buffer_vertex_On[PIXEL_COUNT*CoordsPerPixel];
    static double buffer_vertex_Off[PIXEL_COUNT*CoordsPerPixel];
    static double buffer_normals_On[PIXEL_COUNT*CoordsPerPixel];
    static double buffer_normals_Off[PIXEL_COUNT*CoordsPerPixel];

    float robodkColourOn[] = {1.0,0.0,0.0,1.0};
    float robodkColourOff[] = {0.0,0.0,1.0,1.0};


    // create an identity matrix:
    Mat pose_ref;// Same as: Mat::transl(0,0,0));

    if ( (ScreenRef != nullptr)) {
        //ScreenRef->PoseAbs().ToXYZRPW(WorldCoordPos);
        pose_ref = ScreenRef->PoseAbs();
    }
    const double *pose_ptr16 = pose_ref.Values();

    if (fRender == true) {
        for (int i = 0; i < 32; i++) {
            for (int j = 0; j < 64; j++) {
                if (chip8VRAM[i*64+j] == true) {
                    CopyPixel2Buffer(j,i, buffer_vertex_On + count_triangles_On*CoordsPerTriangle, buffer_normals_On+count_triangles_On*CoordsPerTriangle);
                    count_triangles_On = count_triangles_On + TrianglesPerPixel;
                } else {
                    CopyPixel2Buffer(j,i, buffer_vertex_Off + count_triangles_Off*CoordsPerTriangle, buffer_normals_Off+count_triangles_Off*CoordsPerTriangle);
                    count_triangles_Off = count_triangles_Off + TrianglesPerPixel;
                }
            }
        }
        debug++;
    }

    for (int i=0; i<count_triangles_On*CoordsPerTriangle; i=i+3){
        double ptcpy[3];
        double *pt = buffer_vertex_On + i;
        COPY3(ptcpy, pt);
        MULT_MAT_POINT(pt, pose_ptr16, ptcpy);

        double *nrml = buffer_normals_On + i;
        COPY3(ptcpy, nrml);
        MULT_MAT_VECTOR(nrml, pose_ptr16, ptcpy);
    }
    for (int i=0; i<count_triangles_Off*CoordsPerTriangle; i=i+3){
        double ptcpy[3];
        double *pt = buffer_vertex_Off + i;
        COPY3(ptcpy, pt);
        MULT_MAT_POINT(pt, pose_ptr16, ptcpy);

        double *nrml = buffer_normals_Off + i;
        COPY3(ptcpy, nrml);
        MULT_MAT_VECTOR(nrml, pose_ptr16, ptcpy);
    }

    // Display geometry using RoboDK shaders.
    // Note: here you could use plain OpenGL if you use the binary RoboDK-GL2
    // https://github.com/RoboDK/Plug-In-Interface/tree/master/PluginOpenGL

    // Display on pixels
    RDK->DrawGeometry(RoboDK::DrawTriangles, buffer_vertex_On, count_triangles_On, robodkColourOn,2,buffer_normals_On); //-2,buffer_normals_On);

    // Display off pixels (if desired)
    // this could be rendered as one plane behind the text (2 triangles)
    RDK->DrawGeometry(RoboDK::DrawTriangles, buffer_vertex_Off, count_triangles_Off, robodkColourOff,2,buffer_normals_Off); //-2,buffer_normals_On);
}

















