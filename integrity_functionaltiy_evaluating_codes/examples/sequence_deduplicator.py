import time

def deduplicate_sequence(api_sequence, lm=5, k=2):
    """
    Compress redundant contiguous API loops from dynamic analysis traces.
    
    Parameters:
    - api_sequence (list): Sequence of API calls (strings or dicts).
    - lm (int): Maximum tandem pattern length to scan.
    - k (int): Maximum number of consecutive repetitions retained.
    
    Returns:
    - list: Deduplicated API sequence.
    """
    if not api_sequence:
        return []
    
    result = list(api_sequence)
    
    # Repeat compression passes until the sequence length stabilizes
    while True:
        prev_len = len(result)
        
        # Scan pattern lengths from 1 to lm
        for p in range(1, lm + 1):
            i = 0
            new_seq = []
            
            while i < len(result):
                pattern = result[i : i + p]
                
                # If the remaining slice cannot hold a repeated pattern, append and break
                if i + 2 * p > len(result):
                    new_seq.extend(result[i:])
                    break
                    
                # Count consecutive repetitions of the pattern
                repeats = 1
                idx = i + p
                while idx + p <= len(result) and result[idx : idx + p] == pattern:
                    repeats += 1
                    idx += p
                    
                # If repeated more than k times, retain only k copies
                if repeats > k:
                    for _ in range(k):
                        new_seq.extend(pattern)
                    i = idx 
                else:
                    new_seq.append(result[i])
                    i += 1
                    
            result = new_seq
            
        if len(result) == prev_len:
            break
            
    return result


if __name__ == "__main__":
    raw_dynamic_trace = [
        "LoadLibraryA",
        "GetProcAddress",
        "InternetOpenA", "InternetConnectA",
        "InternetOpenA", "InternetConnectA",
        "InternetOpenA", "InternetConnectA",
        "InternetOpenA", "InternetConnectA",
        "InternetOpenA", "InternetConnectA",
        "InternetOpenA", "InternetConnectA",
        "Sleep", "Sleep", "Sleep", "Sleep", "Sleep",
        "CreateFileA",
        "WriteFile"
    ]
    
    print(f"[*] Original sequence length: {len(raw_dynamic_trace)}")
    print("[*] Original sequence:", raw_dynamic_trace)
    
    start_time = time.time()
    compressed_trace = deduplicate_sequence(raw_dynamic_trace, lm=5, k=2)
    end_time = time.time()
    
    print(f"\n[*] Compressed sequence length: {len(compressed_trace)}")
    print("[*] Compressed sequence:", compressed_trace)
    print(f"[*] Elapsed time: {(end_time - start_time)*1000:.4f} ms")
