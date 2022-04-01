import struct

FILE_OFFSET_ADDRESS = 0xc
FILE_INDEX_START = 0x168

def get_int32(f, offset):
    f.seek(offset)
    buffer = f.read(4)
    return struct.unpack("<I", buffer)[0]


with open("C:\\Program Files (x86)\\Steam\\steamapps\\common\\The Bard's Tale Trilogy\\TheBardsTaleTrilogy_Data\\resources.assets", "rb+") as f:
    f.seek(FILE_OFFSET_ADDRESS)
    file_offset, = struct.unpack(">I", f.read(4))
    for i in range(0x22c):
        f.seek(FILE_INDEX_START + i * 20)
        part1, count, part2, offset, length = struct.unpack("<IIIII", f.read(20))
        # print(f"{part1:x}: {count:x}, {part2:x}, {offset:x}, {length:x}")
        f.seek(file_offset + offset)
        fn_length, = struct.unpack("<I", f.read(4))
        fn = f.read(fn_length)
        if fn.startswith(b"map_bt1") or fn.startswith(b"map_bt2") or fn.startswith(b"map_bt3"):
            print (f"processing {fn}")
            file_start = file_offset + offset + 4  + fn_length
            file_start = (file_start + 3) & ~3 # next nearest quad
            f.seek(file_start)
            file_length, = struct.unpack("<I", f.read(4))
            data = f.read(file_length)
            if not data.startswith(b"name=SCRIPTSTRING"):
                print (f"  skipping")
                continue
            data = data.replace(b", Darkness", b"")
            data = data.replace(b", AntiMagic", b"")
            new_length = len(data)

            if new_length == file_length:
                print ("  no change")
                continue

            if new_length > file_length:
                raise Exception("Processed file is larger?")

            # Pad file with zeros to the original size.
            data += b"\0" * (file_length - new_length)

            if len(data) != file_length:
                raise Exception("File length mismatch after processing")


            f.seek(file_start)
            f.write(struct.pack("<I", new_length))
            f.write(data)
            print ("  patched")

