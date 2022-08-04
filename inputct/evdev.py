import os
from functools import cached_property, reduce, wraps
from enum import IntEnum
from ctypes import (
    Structure, Union, POINTER, create_string_buffer, sizeof,
    c_long, c_int, c_uint, c_uint8, c_int8, c_uint16, c_int16,
    c_uint32, c_int32, c_uint64, c_int64)
import typing
from dataclasses import dataclass
from datetime import datetime, timedelta
from fcntl import ioctl
from errno import errorcode
from contextlib import contextmanager
try:
    from inspect import get_annotations
except ImportError:
    def get_annotations(o):
        return o.__annotations__

class INPUT_PROP(IntEnum):
    POINTER        = 0x00
    DIRECT         = 0x01
    BUTTONPAD      = 0x02
    SEMI_MT        = 0x03
    TOPBUTTONPAD   = 0x04
    POINTING_STICK = 0x05
    ACCELEROMETER  = 0x06

class EV(IntEnum):
    SYN       = 0x00
    KEY       = 0x01
    REL       = 0x02
    ABS       = 0x03
    MSC       = 0x04
    SW        = 0x05
    LED       = 0x11
    SND       = 0x12
    REP       = 0x14
    FF        = 0x15
    PWR       = 0x16
    FF_STATUS = 0x17

class SYN(IntEnum):
    REPORT    = 0
    CONFIG    = 1
    MT_REPORT = 2
    DROPPED   = 3

class KEY(IntEnum):
    KEY_RESERVED                 = 0
    KEY_ESC                      = 1
    KEY_1                        = 2
    KEY_2                        = 3
    KEY_3                        = 4
    KEY_4                        = 5
    KEY_5                        = 6
    KEY_6                        = 7
    KEY_7                        = 8
    KEY_8                        = 9
    KEY_9                        = 10
    KEY_0                        = 11
    KEY_MINUS                    = 12
    KEY_EQUAL                    = 13
    KEY_BACKSPACE                = 14
    KEY_TAB                      = 15
    KEY_Q                        = 16
    KEY_W                        = 17
    KEY_E                        = 18
    KEY_R                        = 19
    KEY_T                        = 20
    KEY_Y                        = 21
    KEY_U                        = 22
    KEY_I                        = 23
    KEY_O                        = 24
    KEY_P                        = 25
    KEY_LEFTBRACE                = 26
    KEY_RIGHTBRACE               = 27
    KEY_ENTER                    = 28
    KEY_LEFTCTRL                 = 29
    KEY_A                        = 30
    KEY_S                        = 31
    KEY_D                        = 32
    KEY_F                        = 33
    KEY_G                        = 34
    KEY_H                        = 35
    KEY_J                        = 36
    KEY_K                        = 37
    KEY_L                        = 38
    KEY_SEMICOLON                = 39
    KEY_APOSTROPHE               = 40
    KEY_GRAVE                    = 41
    KEY_LEFTSHIFT                = 42
    KEY_BACKSLASH                = 43
    KEY_Z                        = 44
    KEY_X                        = 45
    KEY_C                        = 46
    KEY_V                        = 47
    KEY_B                        = 48
    KEY_N                        = 49
    KEY_M                        = 50
    KEY_COMMA                    = 51
    KEY_DOT                      = 52
    KEY_SLASH                    = 53
    KEY_RIGHTSHIFT               = 54
    KEY_KPASTERISK               = 55
    KEY_LEFTALT                  = 56
    KEY_SPACE                    = 57
    KEY_CAPSLOCK                 = 58
    KEY_F1                       = 59
    KEY_F2                       = 60
    KEY_F3                       = 61
    KEY_F4                       = 62
    KEY_F5                       = 63
    KEY_F6                       = 64
    KEY_F7                       = 65
    KEY_F8                       = 66
    KEY_F9                       = 67
    KEY_F10                      = 68
    KEY_NUMLOCK                  = 69
    KEY_SCROLLLOCK               = 70
    KEY_KP7                      = 71
    KEY_KP8                      = 72
    KEY_KP9                      = 73
    KEY_KPMINUS                  = 74
    KEY_KP4                      = 75
    KEY_KP5                      = 76
    KEY_KP6                      = 77
    KEY_KPPLUS                   = 78
    KEY_KP1                      = 79
    KEY_KP2                      = 80
    KEY_KP3                      = 81
    KEY_KP0                      = 82
    KEY_KPDOT                    = 83
    KEY_ZENKAKUHANKAKU           = 85
    KEY_102ND                    = 86
    KEY_F11                      = 87
    KEY_F12                      = 88
    KEY_RO                       = 89
    KEY_KATAKANA                 = 90
    KEY_HIRAGANA                 = 91
    KEY_HENKAN                   = 92
    KEY_KATAKANAHIRAGANA         = 93
    KEY_MUHENKAN                 = 94
    KEY_KPJPCOMMA                = 95
    KEY_KPENTER                  = 96
    KEY_RIGHTCTRL                = 97
    KEY_KPSLASH                  = 98
    KEY_SYSRQ                    = 99
    KEY_RIGHTALT                 = 100
    KEY_LINEFEED                 = 101
    KEY_HOME                     = 102
    KEY_UP                       = 103
    KEY_PAGEUP                   = 104
    KEY_LEFT                     = 105
    KEY_RIGHT                    = 106
    KEY_END                      = 107
    KEY_DOWN                     = 108
    KEY_PAGEDOWN                 = 109
    KEY_INSERT                   = 110
    KEY_DELETE                   = 111
    KEY_MACRO                    = 112
    KEY_MUTE                     = 113
    KEY_VOLUMEDOWN               = 114
    KEY_VOLUMEUP                 = 115
    KEY_POWER                    = 116
    KEY_KPEQUAL                  = 117
    KEY_KPPLUSMINUS              = 118
    KEY_PAUSE                    = 119
    KEY_SCALE                    = 120
    KEY_KPCOMMA                  = 121
    KEY_HANGEUL                  = 122
    KEY_HANJA                    = 123
    KEY_YEN                      = 124
    KEY_LEFTMETA                 = 125
    KEY_RIGHTMETA                = 126
    KEY_COMPOSE                  = 127
    KEY_STOP                     = 128
    KEY_AGAIN                    = 129
    KEY_PROPS                    = 130
    KEY_UNDO                     = 131
    KEY_FRONT                    = 132
    KEY_COPY                     = 133
    KEY_OPEN                     = 134
    KEY_PASTE                    = 135
    KEY_FIND                     = 136
    KEY_CUT                      = 137
    KEY_HELP                     = 138
    KEY_MENU                     = 139
    KEY_CALC                     = 140
    KEY_SETUP                    = 141
    KEY_SLEEP                    = 142
    KEY_WAKEUP                   = 143
    KEY_FILE                     = 144
    KEY_SENDFILE                 = 145
    KEY_DELETEFILE               = 146
    KEY_XFER                     = 147
    KEY_PROG1                    = 148
    KEY_PROG2                    = 149
    KEY_WWW                      = 150
    KEY_MSDOS                    = 151
    KEY_SCREENLOCK               = 152
    KEY_ROTATE_DISPLAY           = 153
    KEY_CYCLEWINDOWS             = 154
    KEY_MAIL                     = 155
    KEY_BOOKMARKS                = 156
    KEY_COMPUTER                 = 157
    KEY_BACK                     = 158
    KEY_FORWARD                  = 159
    KEY_CLOSECD                  = 160
    KEY_EJECTCD                  = 161
    KEY_EJECTCLOSECD             = 162
    KEY_NEXTSONG                 = 163
    KEY_PLAYPAUSE                = 164
    KEY_PREVIOUSSONG             = 165
    KEY_STOPCD                   = 166
    KEY_RECORD                   = 167
    KEY_REWIND                   = 168
    KEY_PHONE                    = 169
    KEY_ISO                      = 170
    KEY_CONFIG                   = 171
    KEY_HOMEPAGE                 = 172
    KEY_REFRESH                  = 173
    KEY_EXIT                     = 174
    KEY_MOVE                     = 175
    KEY_EDIT                     = 176
    KEY_SCROLLUP                 = 177
    KEY_SCROLLDOWN               = 178
    KEY_KPLEFTPAREN              = 179
    KEY_KPRIGHTPAREN             = 180
    KEY_NEW                      = 181
    KEY_REDO                     = 182
    KEY_F13                      = 183
    KEY_F14                      = 184
    KEY_F15                      = 185
    KEY_F16                      = 186
    KEY_F17                      = 187
    KEY_F18                      = 188
    KEY_F19                      = 189
    KEY_F20                      = 190
    KEY_F21                      = 191
    KEY_F22                      = 192
    KEY_F23                      = 193
    KEY_F24                      = 194
    KEY_PLAYCD                   = 200
    KEY_PAUSECD                  = 201
    KEY_PROG3                    = 202
    KEY_PROG4                    = 203
    KEY_DASHBOARD                = 204
    KEY_SUSPEND                  = 205
    KEY_CLOSE                    = 206
    KEY_PLAY                     = 207
    KEY_FASTFORWARD              = 208
    KEY_BASSBOOST                = 209
    KEY_PRINT                    = 210
    KEY_HP                       = 211
    KEY_CAMERA                   = 212
    KEY_SOUND                    = 213
    KEY_QUESTION                 = 214
    KEY_EMAIL                    = 215
    KEY_CHAT                     = 216
    KEY_SEARCH                   = 217
    KEY_CONNECT                  = 218
    KEY_FINANCE                  = 219
    KEY_SPORT                    = 220
    KEY_SHOP                     = 221
    KEY_ALTERASE                 = 222
    KEY_CANCEL                   = 223
    KEY_BRIGHTNESSDOWN           = 224
    KEY_BRIGHTNESSUP             = 225
    KEY_MEDIA                    = 226
    KEY_SWITCHVIDEOMODE          = 227
    KEY_KBDILLUMTOGGLE           = 228
    KEY_KBDILLUMDOWN             = 229
    KEY_KBDILLUMUP               = 230
    KEY_SEND                     = 231
    KEY_REPLY                    = 232
    KEY_FORWARDMAIL              = 233
    KEY_SAVE                     = 234
    KEY_DOCUMENTS                = 235
    KEY_BATTERY                  = 236
    KEY_BLUETOOTH                = 237
    KEY_WLAN                     = 238
    KEY_UWB                      = 239
    KEY_UNKNOWN                  = 240
    KEY_VIDEO_NEXT               = 241
    KEY_VIDEO_PREV               = 242
    KEY_BRIGHTNESS_CYCLE         = 243
    KEY_BRIGHTNESS_AUTO          = 244
    KEY_DISPLAY_OFF              = 245
    KEY_WWAN                     = 246
    KEY_RFKILL                   = 247
    KEY_MICMUTE                  = 248
    BTN_MISC                     = 0x100
    BTN_0                        = 0x100
    BTN_1                        = 0x101
    BTN_2                        = 0x102
    BTN_3                        = 0x103
    BTN_4                        = 0x104
    BTN_5                        = 0x105
    BTN_6                        = 0x106
    BTN_7                        = 0x107
    BTN_8                        = 0x108
    BTN_9                        = 0x109
    BTN_MOUSE                    = 0x110
    BTN_LEFT                     = 0x110
    BTN_RIGHT                    = 0x111
    BTN_MIDDLE                   = 0x112
    BTN_SIDE                     = 0x113
    BTN_EXTRA                    = 0x114
    BTN_FORWARD                  = 0x115
    BTN_BACK                     = 0x116
    BTN_TASK                     = 0x117
    BTN_JOYSTICK                 = 0x120
    BTN_TRIGGER                  = 0x120
    BTN_THUMB                    = 0x121
    BTN_THUMB2                   = 0x122
    BTN_TOP                      = 0x123
    BTN_TOP2                     = 0x124
    BTN_PINKIE                   = 0x125
    BTN_BASE                     = 0x126
    BTN_BASE2                    = 0x127
    BTN_BASE3                    = 0x128
    BTN_BASE4                    = 0x129
    BTN_BASE5                    = 0x12a
    BTN_BASE6                    = 0x12b
    BTN_DEAD                     = 0x12f
    BTN_GAMEPAD                  = 0x130
    BTN_A                        = 0x130
    BTN_B                        = 0x131
    BTN_C                        = 0x132
    BTN_X                        = 0x133
    BTN_Y                        = 0x134
    BTN_Z                        = 0x135
    BTN_TL                       = 0x136
    BTN_TR                       = 0x137
    BTN_TL2                      = 0x138
    BTN_TR2                      = 0x139
    BTN_SELECT                   = 0x13a
    BTN_START                    = 0x13b
    BTN_MODE                     = 0x13c
    BTN_THUMBL                   = 0x13d
    BTN_THUMBR                   = 0x13e
    BTN_DIGI                     = 0x140
    BTN_TOOL_PEN                 = 0x140
    BTN_TOOL_RUBBER              = 0x141
    BTN_TOOL_BRUSH               = 0x142
    BTN_TOOL_PENCIL              = 0x143
    BTN_TOOL_AIRBRUSH            = 0x144
    BTN_TOOL_FINGER              = 0x145
    BTN_TOOL_MOUSE               = 0x146
    BTN_TOOL_LENS                = 0x147
    BTN_TOOL_QUINTTAP            = 0x148
    BTN_STYLUS3                  = 0x149
    BTN_TOUCH                    = 0x14a
    BTN_STYLUS                   = 0x14b
    BTN_STYLUS2                  = 0x14c
    BTN_TOOL_DOUBLETAP           = 0x14d
    BTN_TOOL_TRIPLETAP           = 0x14e
    BTN_TOOL_QUADTAP             = 0x14f
    BTN_WHEEL                    = 0x150
    BTN_GEAR_DOWN                = 0x150
    BTN_GEAR_UP                  = 0x151
    KEY_OK                       = 0x160
    KEY_SELECT                   = 0x161
    KEY_GOTO                     = 0x162
    KEY_CLEAR                    = 0x163
    KEY_POWER2                   = 0x164
    KEY_OPTION                   = 0x165
    KEY_INFO                     = 0x166
    KEY_TIME                     = 0x167
    KEY_VENDOR                   = 0x168
    KEY_ARCHIVE                  = 0x169
    KEY_PROGRAM                  = 0x16a
    KEY_CHANNEL                  = 0x16b
    KEY_FAVORITES                = 0x16c
    KEY_EPG                      = 0x16d
    KEY_PVR                      = 0x16e
    KEY_MHP                      = 0x16f
    KEY_LANGUAGE                 = 0x170
    KEY_TITLE                    = 0x171
    KEY_SUBTITLE                 = 0x172
    KEY_ANGLE                    = 0x173
    KEY_FULL_SCREEN              = 0x174
    KEY_MODE                     = 0x175
    KEY_KEYBOARD                 = 0x176
    KEY_ASPECT_RATIO             = 0x177
    KEY_PC                       = 0x178
    KEY_TV                       = 0x179
    KEY_TV2                      = 0x17a
    KEY_VCR                      = 0x17b
    KEY_VCR2                     = 0x17c
    KEY_SAT                      = 0x17d
    KEY_SAT2                     = 0x17e
    KEY_CD                       = 0x17f
    KEY_TAPE                     = 0x180
    KEY_RADIO                    = 0x181
    KEY_TUNER                    = 0x182
    KEY_PLAYER                   = 0x183
    KEY_TEXT                     = 0x184
    KEY_DVD                      = 0x185
    KEY_AUX                      = 0x186
    KEY_MP3                      = 0x187
    KEY_AUDIO                    = 0x188
    KEY_VIDEO                    = 0x189
    KEY_DIRECTORY                = 0x18a
    KEY_LIST                     = 0x18b
    KEY_MEMO                     = 0x18c
    KEY_CALENDAR                 = 0x18d
    KEY_RED                      = 0x18e
    KEY_GREEN                    = 0x18f
    KEY_YELLOW                   = 0x190
    KEY_BLUE                     = 0x191
    KEY_CHANNELUP                = 0x192
    KEY_CHANNELDOWN              = 0x193
    KEY_FIRST                    = 0x194
    KEY_LAST                     = 0x195
    KEY_AB                       = 0x196
    KEY_NEXT                     = 0x197
    KEY_RESTART                  = 0x198
    KEY_SLOW                     = 0x199
    KEY_SHUFFLE                  = 0x19a
    KEY_BREAK                    = 0x19b
    KEY_PREVIOUS                 = 0x19c
    KEY_DIGITS                   = 0x19d
    KEY_TEEN                     = 0x19e
    KEY_TWEN                     = 0x19f
    KEY_VIDEOPHONE               = 0x1a0
    KEY_GAMES                    = 0x1a1
    KEY_ZOOMIN                   = 0x1a2
    KEY_ZOOMOUT                  = 0x1a3
    KEY_ZOOMRESET                = 0x1a4
    KEY_WORDPROCESSOR            = 0x1a5
    KEY_EDITOR                   = 0x1a6
    KEY_SPREADSHEET              = 0x1a7
    KEY_GRAPHICSEDITOR           = 0x1a8
    KEY_PRESENTATION             = 0x1a9
    KEY_DATABASE                 = 0x1aa
    KEY_NEWS                     = 0x1ab
    KEY_VOICEMAIL                = 0x1ac
    KEY_ADDRESSBOOK              = 0x1ad
    KEY_MESSENGER                = 0x1ae
    KEY_DISPLAYTOGGLE            = 0x1af
    KEY_SPELLCHECK               = 0x1b0
    KEY_LOGOFF                   = 0x1b1
    KEY_DOLLAR                   = 0x1b2
    KEY_EURO                     = 0x1b3
    KEY_FRAMEBACK                = 0x1b4
    KEY_FRAMEFORWARD             = 0x1b5
    KEY_CONTEXT_MENU             = 0x1b6
    KEY_MEDIA_REPEAT             = 0x1b7
    KEY_10CHANNELSUP             = 0x1b8
    KEY_10CHANNELSDOWN           = 0x1b9
    KEY_IMAGES                   = 0x1ba
    KEY_NOTIFICATION_CENTER      = 0x1bc
    KEY_PICKUP_PHONE             = 0x1bd
    KEY_HANGUP_PHONE             = 0x1be
    KEY_DEL_EOL                  = 0x1c0
    KEY_DEL_EOS                  = 0x1c1
    KEY_INS_LINE                 = 0x1c2
    KEY_DEL_LINE                 = 0x1c3
    KEY_FN                       = 0x1d0
    KEY_FN_ESC                   = 0x1d1
    KEY_FN_F1                    = 0x1d2
    KEY_FN_F2                    = 0x1d3
    KEY_FN_F3                    = 0x1d4
    KEY_FN_F4                    = 0x1d5
    KEY_FN_F5                    = 0x1d6
    KEY_FN_F6                    = 0x1d7
    KEY_FN_F7                    = 0x1d8
    KEY_FN_F8                    = 0x1d9
    KEY_FN_F9                    = 0x1da
    KEY_FN_F10                   = 0x1db
    KEY_FN_F11                   = 0x1dc
    KEY_FN_F12                   = 0x1dd
    KEY_FN_1                     = 0x1de
    KEY_FN_2                     = 0x1df
    KEY_FN_D                     = 0x1e0
    KEY_FN_E                     = 0x1e1
    KEY_FN_F                     = 0x1e2
    KEY_FN_S                     = 0x1e3
    KEY_FN_B                     = 0x1e4
    KEY_FN_RIGHT_SHIFT           = 0x1e5
    KEY_BRL_DOT1                 = 0x1f1
    KEY_BRL_DOT2                 = 0x1f2
    KEY_BRL_DOT3                 = 0x1f3
    KEY_BRL_DOT4                 = 0x1f4
    KEY_BRL_DOT5                 = 0x1f5
    KEY_BRL_DOT6                 = 0x1f6
    KEY_BRL_DOT7                 = 0x1f7
    KEY_BRL_DOT8                 = 0x1f8
    KEY_BRL_DOT9                 = 0x1f9
    KEY_BRL_DOT10                = 0x1fa
    KEY_NUMERIC_0                = 0x200
    KEY_NUMERIC_1                = 0x201
    KEY_NUMERIC_2                = 0x202
    KEY_NUMERIC_3                = 0x203
    KEY_NUMERIC_4                = 0x204
    KEY_NUMERIC_5                = 0x205
    KEY_NUMERIC_6                = 0x206
    KEY_NUMERIC_7                = 0x207
    KEY_NUMERIC_8                = 0x208
    KEY_NUMERIC_9                = 0x209
    KEY_NUMERIC_STAR             = 0x20a
    KEY_NUMERIC_POUND            = 0x20b
    KEY_NUMERIC_A                = 0x20c
    KEY_NUMERIC_B                = 0x20d
    KEY_NUMERIC_C                = 0x20e
    KEY_NUMERIC_D                = 0x20f
    KEY_CAMERA_FOCUS             = 0x210
    KEY_WPS_BUTTON               = 0x211
    KEY_TOUCHPAD_TOGGLE          = 0x212
    KEY_TOUCHPAD_ON              = 0x213
    KEY_TOUCHPAD_OFF             = 0x214
    KEY_CAMERA_ZOOMIN            = 0x215
    KEY_CAMERA_ZOOMOUT           = 0x216
    KEY_CAMERA_UP                = 0x217
    KEY_CAMERA_DOWN              = 0x218
    KEY_CAMERA_LEFT              = 0x219
    KEY_CAMERA_RIGHT             = 0x21a
    KEY_ATTENDANT_ON             = 0x21b
    KEY_ATTENDANT_OFF            = 0x21c
    KEY_ATTENDANT_TOGGLE         = 0x21d
    KEY_LIGHTS_TOGGLE            = 0x21e
    BTN_DPAD_UP                  = 0x220
    BTN_DPAD_DOWN                = 0x221
    BTN_DPAD_LEFT                = 0x222
    BTN_DPAD_RIGHT               = 0x223
    KEY_ALS_TOGGLE               = 0x230
    KEY_ROTATE_LOCK_TOGGLE       = 0x231
    KEY_BUTTONCONFIG             = 0x240
    KEY_TASKMANAGER              = 0x241
    KEY_JOURNAL                  = 0x242
    KEY_CONTROLPANEL             = 0x243
    KEY_APPSELECT                = 0x244
    KEY_SCREENSAVER              = 0x245
    KEY_VOICECOMMAND             = 0x246
    KEY_ASSISTANT                = 0x247
    KEY_KBD_LAYOUT_NEXT          = 0x248
    KEY_EMOJI_PICKER             = 0x249
    KEY_BRIGHTNESS_MIN           = 0x250
    KEY_BRIGHTNESS_MAX           = 0x251
    KEY_KBDINPUTASSIST_PREV      = 0x260
    KEY_KBDINPUTASSIST_NEXT      = 0x261
    KEY_KBDINPUTASSIST_PREVGROUP = 0x262
    KEY_KBDINPUTASSIST_NEXTGROUP = 0x263
    KEY_KBDINPUTASSIST_ACCEPT    = 0x264
    KEY_KBDINPUTASSIST_CANCEL    = 0x265
    KEY_RIGHT_UP                 = 0x266
    KEY_RIGHT_DOWN               = 0x267
    KEY_LEFT_UP                  = 0x268
    KEY_LEFT_DOWN                = 0x269
    KEY_ROOT_MENU                = 0x26a
    KEY_MEDIA_TOP_MENU           = 0x26b
    KEY_NUMERIC_11               = 0x26c
    KEY_NUMERIC_12               = 0x26d
    KEY_AUDIO_DESC               = 0x26e
    KEY_3D_MODE                  = 0x26f
    KEY_NEXT_FAVORITE            = 0x270
    KEY_STOP_RECORD              = 0x271
    KEY_PAUSE_RECORD             = 0x272
    KEY_VOD                      = 0x273
    KEY_UNMUTE                   = 0x274
    KEY_FASTREVERSE              = 0x275
    KEY_SLOWREVERSE              = 0x276
    KEY_DATA                     = 0x277
    KEY_ONSCREEN_KEYBOARD        = 0x278
    KEY_PRIVACY_SCREEN_TOGGLE    = 0x279
    KEY_SELECTIVE_SCREENSHOT     = 0x27a
    KEY_MACRO1                   = 0x290
    KEY_MACRO2                   = 0x291
    KEY_MACRO3                   = 0x292
    KEY_MACRO4                   = 0x293
    KEY_MACRO5                   = 0x294
    KEY_MACRO6                   = 0x295
    KEY_MACRO7                   = 0x296
    KEY_MACRO8                   = 0x297
    KEY_MACRO9                   = 0x298
    KEY_MACRO10                  = 0x299
    KEY_MACRO11                  = 0x29a
    KEY_MACRO12                  = 0x29b
    KEY_MACRO13                  = 0x29c
    KEY_MACRO14                  = 0x29d
    KEY_MACRO15                  = 0x29e
    KEY_MACRO16                  = 0x29f
    KEY_MACRO17                  = 0x2a0
    KEY_MACRO18                  = 0x2a1
    KEY_MACRO19                  = 0x2a2
    KEY_MACRO20                  = 0x2a3
    KEY_MACRO21                  = 0x2a4
    KEY_MACRO22                  = 0x2a5
    KEY_MACRO23                  = 0x2a6
    KEY_MACRO24                  = 0x2a7
    KEY_MACRO25                  = 0x2a8
    KEY_MACRO26                  = 0x2a9
    KEY_MACRO27                  = 0x2aa
    KEY_MACRO28                  = 0x2ab
    KEY_MACRO29                  = 0x2ac
    KEY_MACRO30                  = 0x2ad
    KEY_MACRO_RECORD_START       = 0x2b0
    KEY_MACRO_RECORD_STOP        = 0x2b1
    KEY_MACRO_PRESET_CYCLE       = 0x2b2
    KEY_MACRO_PRESET1            = 0x2b3
    KEY_MACRO_PRESET2            = 0x2b4
    KEY_MACRO_PRESET3            = 0x2b5
    KEY_KBD_LCD_MENU1            = 0x2b8
    KEY_KBD_LCD_MENU2            = 0x2b9
    KEY_KBD_LCD_MENU3            = 0x2ba
    KEY_KBD_LCD_MENU4            = 0x2bb
    KEY_KBD_LCD_MENU5            = 0x2bc
    BTN_TRIGGER_HAPPY            = 0x2c0
    BTN_TRIGGER_HAPPY1           = 0x2c0
    BTN_TRIGGER_HAPPY2           = 0x2c1
    BTN_TRIGGER_HAPPY3           = 0x2c2
    BTN_TRIGGER_HAPPY4           = 0x2c3
    BTN_TRIGGER_HAPPY5           = 0x2c4
    BTN_TRIGGER_HAPPY6           = 0x2c5
    BTN_TRIGGER_HAPPY7           = 0x2c6
    BTN_TRIGGER_HAPPY8           = 0x2c7
    BTN_TRIGGER_HAPPY9           = 0x2c8
    BTN_TRIGGER_HAPPY10          = 0x2c9
    BTN_TRIGGER_HAPPY11          = 0x2ca
    BTN_TRIGGER_HAPPY12          = 0x2cb
    BTN_TRIGGER_HAPPY13          = 0x2cc
    BTN_TRIGGER_HAPPY14          = 0x2cd
    BTN_TRIGGER_HAPPY15          = 0x2ce
    BTN_TRIGGER_HAPPY16          = 0x2cf
    BTN_TRIGGER_HAPPY17          = 0x2d0
    BTN_TRIGGER_HAPPY18          = 0x2d1
    BTN_TRIGGER_HAPPY19          = 0x2d2
    BTN_TRIGGER_HAPPY20          = 0x2d3
    BTN_TRIGGER_HAPPY21          = 0x2d4
    BTN_TRIGGER_HAPPY22          = 0x2d5
    BTN_TRIGGER_HAPPY23          = 0x2d6
    BTN_TRIGGER_HAPPY24          = 0x2d7
    BTN_TRIGGER_HAPPY25          = 0x2d8
    BTN_TRIGGER_HAPPY26          = 0x2d9
    BTN_TRIGGER_HAPPY27          = 0x2da
    BTN_TRIGGER_HAPPY28          = 0x2db
    BTN_TRIGGER_HAPPY29          = 0x2dc
    BTN_TRIGGER_HAPPY30          = 0x2dd
    BTN_TRIGGER_HAPPY31          = 0x2de
    BTN_TRIGGER_HAPPY32          = 0x2df
    BTN_TRIGGER_HAPPY33          = 0x2e0
    BTN_TRIGGER_HAPPY34          = 0x2e1
    BTN_TRIGGER_HAPPY35          = 0x2e2
    BTN_TRIGGER_HAPPY36          = 0x2e3
    BTN_TRIGGER_HAPPY37          = 0x2e4
    BTN_TRIGGER_HAPPY38          = 0x2e5
    BTN_TRIGGER_HAPPY39          = 0x2e6
    BTN_TRIGGER_HAPPY40          = 0x2e7

class REL(IntEnum):
    X             = 0x00
    Y             = 0x01
    Z             = 0x02
    RX            = 0x03
    RY            = 0x04
    RZ            = 0x05
    HWHEEL        = 0x06
    DIAL          = 0x07
    WHEEL         = 0x08
    MISC          = 0x09
    RESERVED      = 0x0a
    WHEEL_HI_RES  = 0x0b
    HWHEEL_HI_RES = 0x0c

class ABS(IntEnum):
    X              = 0x00
    Y              = 0x01
    Z              = 0x02
    RX             = 0x03
    RY             = 0x04
    RZ             = 0x05
    THROTTLE       = 0x06
    RUDDER         = 0x07
    WHEEL          = 0x08
    GAS            = 0x09
    BRAKE          = 0x0a
    HAT0X          = 0x10
    HAT0Y          = 0x11
    HAT1X          = 0x12
    HAT1Y          = 0x13
    HAT2X          = 0x14
    HAT2Y          = 0x15
    HAT3X          = 0x16
    HAT3Y          = 0x17
    PRESSURE       = 0x18
    DISTANCE       = 0x19
    TILT_X         = 0x1a
    TILT_Y         = 0x1b
    TOOL_WIDTH     = 0x1c
    VOLUME         = 0x20
    MISC           = 0x28
    RESERVED       = 0x2e
    MT_SLOT        = 0x2f
    MT_TOUCH_MAJOR = 0x30
    MT_TOUCH_MINOR = 0x31
    MT_WIDTH_MAJOR = 0x32
    MT_WIDTH_MINOR = 0x33
    MT_ORIENTATION = 0x34
    MT_POSITION_X  = 0x35
    MT_POSITION_Y  = 0x36
    MT_TOOL_TYPE   = 0x37
    MT_BLOB_ID     = 0x38
    MT_TRACKING_ID = 0x39
    MT_PRESSURE    = 0x3a
    MT_DISTANCE    = 0x3b
    MT_TOOL_X      = 0x3c
    MT_TOOL_Y      = 0x3d

class SW(IntEnum):
    LID                  = 0x00
    TABLET_MODE          = 0x01
    HEADPHONE_INSERT     = 0x02
    RFKILL_ALL           = 0x03
    MICROPHONE_INSERT    = 0x04
    DOCK                 = 0x05
    LINEOUT_INSERT       = 0x06
    JACK_PHYSICAL_INSERT = 0x07
    VIDEOOUT_INSERT      = 0x08
    CAMERA_LENS_COVER    = 0x09
    KEYPAD_SLIDE         = 0x0a
    FRONT_PROXIMITY      = 0x0b
    ROTATE_LOCK          = 0x0c
    LINEIN_INSERT        = 0x0d
    MUTE_DEVICE          = 0x0e
    PEN_INSERTED         = 0x0f
    MACHINE_COVER        = 0x10

class MSC(IntEnum):
    SERIAL    = 0x00
    PULSELED  = 0x01
    GESTURE   = 0x02
    RAW       = 0x03
    SCAN      = 0x04
    TIMESTAMP = 0x05

class LED(IntEnum):
    NUML     = 0x00
    CAPSL    = 0x01
    SCROLLL  = 0x02
    COMPOSE  = 0x03
    KANA     = 0x04
    SLEEP    = 0x05
    SUSPEND  = 0x06
    MUTE     = 0x07
    MISC     = 0x08
    MAIL     = 0x09
    CHARGING = 0x0a

class REP(IntEnum):
    DELAY  = 0x00
    PERIOD = 0x01

class SND(IntEnum):
    CLICK = 0x00
    BELL  = 0x01
    TONE  = 0x02

class ID(IntEnum):
    BUS     = 0
    VENDOR  = 1
    PRODUCT = 2
    VERSION = 3

class BUS(IntEnum):
    PCI         = 0x01
    ISAPNP      = 0x02
    USB         = 0x03
    HIL         = 0x04
    BLUETOOTH   = 0x05
    VIRTUAL     = 0x06
    ISA         = 0x10
    I8042       = 0x11
    XTKBD       = 0x12
    RS232       = 0x13
    GAMEPORT    = 0x14
    PARPORT     = 0x15
    AMIGA       = 0x16
    ADB         = 0x17
    I2C         = 0x18
    HOST        = 0x19
    GSC         = 0x1A
    ATARI       = 0x1B
    SPI         = 0x1C
    RMI         = 0x1D
    CEC         = 0x1E
    INTEL_ISHTP = 0x1F

class MT_TOOL(IntEnum):
    FINGER = 0x00
    PEN    = 0x01
    PALM   = 0x02
    DIAL   = 0x0a
    MAX    = 0x0f

class FF_STATUS(IntEnum):
    STOPPED = 0x00
    PLAYING = 0x01

class FF(IntEnum):
    RUMBLE   = 0x50
    PERIODIC = 0x51
    CONSTANT = 0x52
    SPRING   = 0x53
    FRICTION = 0x54
    DAMPER   = 0x55
    INERTIA  = 0x56
    RAMP     = 0x57
    SQUARE   = 0x58
    TRIANGLE = 0x59
    SINE     = 0x5a
    SAW_UP   = 0x5b
    SAW_DOWN = 0x5c
    CUSTOM   = 0x5d
    GAIN     = 0x60


class timeval(Structure):
    _fields_ = [
        ("sec", c_long),
        ("usec", c_long),
    ]

class input_event(Structure):
    _fields_ = [
        ("time", timeval),
        ("type", c_uint16),
        ("code", c_uint16),
        ("value", c_int32),
    ]

class input_id(Structure):
    _fields_ = [
        ("bustype", c_uint16),
        ("vendor", c_uint16),
        ("product", c_uint16),
        ("version", c_uint16),
    ]

class input_absinfo(Structure):
    _fields_ = [
        ("value", c_int32),
        ("minimum", c_int32),
        ("maximum", c_int32),
        ("fuzz", c_int32),
        ("flat", c_int32),
        ("resolution", c_int32),
    ]

class input_keymap_entry(Structure):
    _fields_ = [
        ("flags", c_uint8),
        ("len", c_uint8),
        ("index", c_uint16),
        ("keycode", c_uint32),
        ("scancode", c_uint8 * 32),
    ]

class input_mask(Structure):
    _fields_ = [
        ("type", c_uint32),
        ("codes_size", c_uint32),
        ("codes_ptr", c_uint64),
    ]


class ff_replay(Structure):
    _fields_ = [
        ("length", c_uint16),
        ("delay", c_uint16),
    ]

class ff_trigger(Structure):
    _fields_ = [
        ("button", c_uint16),
        ("interval", c_uint16),
    ]

class ff_envelope(Structure):
    _fields_ = [
        ("attack_length", c_uint16),
        ("attack_level", c_uint16),
        ("fade_length", c_uint16),
        ("fade_level", c_uint16),
    ]

class ff_constant_effect(Structure):
    _fields_ = [
        ("level", c_int16),
        ("envelope", ff_envelope),
    ]

class ff_ramp_effect(Structure):
    _fields_ = [
        ("start_level", c_int16),
        ("end_level", c_int16),
        ("envelope", ff_envelope),
    ]

class ff_condition_effect(Structure):
    _fields_ = [
        ("right_saturation", c_uint16),
        ("left_saturation", c_uint16),
        ("right_coef", c_int16),
        ("left_coef", c_int16),
        ("deadband", c_uint16),
        ("center", c_int16),
    ]

class ff_periodic_effect(Structure):
    _fields_ = [
        ("waveform", c_uint16),
        ("period", c_uint16),
        ("magnitude", c_int16),
        ("offset", c_int16),
        ("phase", c_uint16),
        ("envelope", ff_envelope),
        ("custom_len", c_uint32),
        ("center", POINTER(c_int16)),
    ]

class ff_rumble_effect(Structure):
    _fields_ = [
        ("strong_magnitude", c_uint16),
        ("weak_magnitude", c_uint16),
    ]

class _U(Union):
    _fields_ = [
        ("constant", ff_constant_effect),
        ("ramp", ff_ramp_effect),
        ("periodic", ff_periodic_effect),
        ("condition", ff_condition_effect * 2),
        ("rumble", ff_rumble_effect),
    ]

class ff_effect(Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("type", c_uint16),
        ("id", c_int16),
        ("direction", c_uint16),
        ("trigger", ff_trigger),
        ("replay", ff_replay),
        ("u", _U),
    ]


EV_VERSION = 0x010001


@dataclass(frozen=True)
class InputEvent:
    time: datetime
    type: EV
    code: typing.Union[SYN, KEY, REL, ABS, MSC, SW, LED, SND, REP]
    value: int

_code_map = {
    EV.SYN: SYN,
    EV.KEY: KEY,
    EV.REL: REL,
    EV.ABS: ABS,
    EV.MSC: MSC,
    EV.SW: SW,
    EV.LED: LED,
    EV.SND: SND,
    EV.REP: REP,
    EV.FF: FF,
    EV.FF_STATUS: FF_STATUS,
}

def _resolve(name, caps):
    caps = reduce(lambda acc, c: (acc<<64)|int(c,16), caps.split(" "), 0)

    if name == 'ev':
        m = EV
    else:
        m = _code_map[EV[name.upper()]]

    codes = set()
    offset = 0
    while caps:
        if caps & 1:
            codes.add(m(offset))
        offset += 1
        caps >>= 1
    if codes:
        return m, frozenset(codes)

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IO(nr, len=None):
    def decorator(func):
        a = get_annotations(func)
        dir = 0
        if 'arg' in a:
            dir |= _IOC_WRITE
            size = sizeof(a['arg'])

        if 'return' in a and a['return'] is not bytes:
            dir |= _IOC_READ
            size = sizeof(a['return'])

        if not dir:
            size = len

        request = ((dir or _IOC_READ) << 30) | (size << 16) | (0x45 << 8) | nr

        if dir & _IOC_WRITE:
            arg_type = a['arg']
            @wraps(func)
            def wrapper(self, arg):
                errno = ioctl(self.fd, request, arg)
                assert errno == 0, errorcode[errno]
        elif dir & _IOC_READ:
            arg_type = a['return']
            @wraps(func)
            def wrapper(self):
                arg = arg_type()
                errno = ioctl(self.fd, request, arg)
                assert errno == 0, errorcode[errno]
                return arg
        elif a.get('return', None) is bytes:
            @wraps(func)
            def wrapper(self):
                arg = create_string_buffer(size)
                ioctl(self.fd, request, arg)
                return arg.value
        else:
            @wraps(func)
            def wrapper(self):
                arg = create_string_buffer(size)
                len = ioctl(self.fd, request, arg)
                return arg[:len]
        return wrapper

    return decorator


class EventDevice:

    def __init__(self, dev, mode=0):
        self.dev = dev
        self.fd = None
        self.mode = 0

    def _readfile(self, name):
        with open(f"/sys/class/input/{self.dev}/device/{name}") as f:
            return f.read().strip()

    @cached_property
    def name(self):
        return self._readfile("name")

    @cached_property
    def phys(self):
        return self._readfile("phys")

    @cached_property
    def properties(self):
        props =  int(self._readfile("properties"))

        values = set()
        offset = 0
        while props:
            if props & 1:
                values.add(INPUT_PROP(offset))
            offset += 1
            props >>= 1

        return frozenset(values)

    @property
    def capabilities(self):
        return dict(
            filter(None,
                   (_resolve(name, self._readfile(f"capabilities/{name}"))
                   for name in os.listdir(f"/sys/class/input/{self.dev}/device/capabilities"))))

    def fileno(self):
        return self.fd

    def open(self):
        self.fd = os.open(os.fspath(f"/dev/input/{self.dev}"), os.O_RDWR | self.mode)

    def close(self):
        if self.fd is not None:
            fd = self.fd
            self.fd = None
            os.close(fd)

    def __del__(self):
        self.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, exc, tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        event = input_event.from_buffer_copy(os.read(self.fd, sizeof(input_event)))
        m = _code_map.get(event.type, None)
        return InputEvent(
            datetime.fromtimestamp(event.time.sec) + timedelta(microseconds=event.time.usec),
            EV(event.type), event.code if m is None else m(event.code), event.value)


    @_IO(0x01)
    def get_version(self) -> c_int:
        pass

    @_IO(0x02)
    def get_id(self) -> input_id:
        pass

    @_IO(0x03)
    def get_rep(self) -> c_uint*2:
        pass

    @_IO(0x03)
    def set_rep(self, arg: c_uint*2):
        pass

    @_IO(0x04)
    def get_keycode(self) -> c_uint*2:
        return

    @_IO(0x04)
    def set_keycode(self, arg: c_uint*2):
        return

    @_IO(0x04)
    def get_keycode_v2(self) -> input_keymap_entry:
        return

    @_IO(0x04)
    def set_keycode_v2(self, arg: input_keymap_entry):
        return

    @_IO(0x06, 80)
    def get_name(self) -> bytes:
        pass

    @_IO(0x07, 80)
    def get_phys(self) -> bytes:
        pass

    @_IO(0x08, 80)
    def get_uniq(self) -> bytes:
        pass

    @_IO(0x09, 1)
    def get_prop(self):
        pass

    def get_mt_slots(self, num):
        class input_mt_request_layout(Structure):
            _fields_ = [
                ("code", c_uint32),
                ("values", c_int32 * num),
            ]

        arg = input_mt_request_layout()
        assert ioctl(self.fd, 0x8000450a | (num<<16), arg) == 0
        return arg.values

    @_IO(0x18, 93)
    def get_key(self):
        return

    @_IO(0x19, 2)
    def get_led(self):
        return

    @_IO(0x1a, 1)
    def get_snd(self):
        pass

    @_IO(0x1b, 3)
    def get_sw(self):
        pass

    def get_bit(self, ev, len):
        arg = create_string_buffer(len)
        assert ioctl(self.fd, (0x80004520 | ev) | (len << 16), arg) == 0
        return arg

    def get_abs(self, abs):
        arg = input_absinfo()
        assert ioctl(self.fd, 0x80184540 | abs, arg) == 0
        return arg

    def set_abs(self, abs, arg):
        assert ioctl(self.fd, 0x801845C0 | abs, arg) == 0

    @_IO(0x80)
    def set_ff(self, arg: ff_effect):
        pass

    @_IO(0x81)
    def rm_ff(self, arg: c_int):
        pass

    @_IO(0x84)
    def get_effects(self) -> c_int:
        pass

    @_IO(0x90)
    def grab(self, arg: c_int):
        pass

    @_IO(0x91)
    def revoke(self, arg: c_int):
        pass

    @_IO(0x92)
    def get_mask(self) -> input_mask:
        pass

    @_IO(0x93)
    def set_mask(self, arg: input_mask):
        pass

    @_IO(0xa0)
    def set_clock_id(self, arg: c_int):
        pass


def list_devices():
    return [EventDevice(name)
            for name in os.listdir("/dev/input")
            if name.startswith('event')]

@contextmanager
def grab(device):
    device.grab(1)
    try:
        yield
    finally:
        device.grab(0)
