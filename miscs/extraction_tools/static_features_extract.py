import os
import numpy as np
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_MODE_64
from tqdm import tqdm


TARGET_DIRECTORY = "malguise"
OUTPUT_FILE = "malguise_static.npz"


def extract_all_features(target_dir, output_filepath):
    data_dict = {
        "name": [],
        "label": [],
        "raw_byte": [],
        "op_code": [],
        "api_pefile": [],
    }

    # Configure Capstone disassembler for x86 (32-bit) and x86_64 (64-bit)
    md_32 = Cs(CS_ARCH_X86, CS_MODE_32)
    md_64 = Cs(CS_ARCH_X86, CS_MODE_64)
    md_32.skipdata = True
    md_64.skipdata = True

    # Iterate through family subdirectories (Benign, Locker, Mediyes, ...)
    for label in os.listdir(target_dir):
        label_dir = os.path.join(target_dir, label)

        if not os.path.isdir(label_dir):
            continue

        print(f"\n[*] Processing label: {label}")

        for filename in tqdm(os.listdir(label_dir)):
            filepath = os.path.join(label_dir, filename)
            if not os.path.isfile(filepath):
                continue

            # ==========================================
            # 1. EXTRACT RAW BYTES
            # ==========================================
            try:
                with open(filepath, "rb") as f:
                    raw_data = f.read()
                raw_byte_arr = np.frombuffer(raw_data, dtype=np.uint8)
            except Exception as e:
                print(f"[!] Error reading file {filename}: {e}")
                continue

            # ==========================================
            # 2. EXTRACT OPCODES & STATIC APIS
            # ==========================================
            opcodes = []
            apis = []

            try:
                pe = pefile.PE(filepath)

                # --- A. Extract Opcodes ---
                md = md_64 if pe.FILE_HEADER.Machine == 0x8664 else md_32
                for section in pe.sections:
                    if section.Characteristics & 0x20000000:  # Executable
                        code = section.get_data()
                        for instruction in md.disasm(code, section.VirtualAddress):
                            opcodes.append(instruction.mnemonic)

                # --- B. Extract Static APIs ---
                if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
                    for entry in pe.DIRECTORY_ENTRY_IMPORT:
                        for imp in entry.imports:
                            if imp.name is not None:
                                apis.append(imp.name.decode("utf-8", errors="ignore"))

            except Exception:
                # Skip if PE headers are malformed or encrypted
                pass

            opcode_str = " ".join(opcodes)
            api_str = " ".join(apis)

            # ==========================================
            # 3. STORE IN DICTIONARY
            # ==========================================
            data_dict["name"].append(filename)
            data_dict["label"].append(label)
            data_dict["raw_byte"].append(raw_byte_arr)
            data_dict["op_code"].append(opcode_str)
            data_dict["api_pefile"].append(api_str)

    # ==========================================
    # 4. COMPRESS AND EXPORT TO .NPZ
    # ==========================================
    print(f"\n[*] Saving extracted data to {output_filepath}...")
    np.savez_compressed(
        output_filepath,
        name=np.array(data_dict["name"]),
        label=np.array(data_dict["label"]),
        raw_byte=np.array(data_dict["raw_byte"], dtype=object),
        op_code=np.array(data_dict["op_code"], dtype=object),
        api_pefile=np.array(data_dict["api_pefile"], dtype=object),
    )
    print(f"[+] Done! Saved archive to {output_filepath}")


extract_all_features(TARGET_DIRECTORY, OUTPUT_FILE)
