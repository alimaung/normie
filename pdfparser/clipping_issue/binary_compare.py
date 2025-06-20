import os

def compare_pdfs(file1, file2, show_diff_bytes=10):
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        data1 = f1.read()
        data2 = f2.read()

    if data1 == data2:
        print("✅ The PDF files are identical.")
        return

    print("❌ The PDF files differ.")

    # Find first differences (optional)
    min_len = min(len(data1), len(data2))
    for i in range(min_len):
        if data1[i] != data2[i]:
            print(f"First difference at byte {i}: {data1[i]} != {data2[i]}")
            print("Nearby bytes (file1 | file2):")
            for j in range(i, min(i + show_diff_bytes, min_len)):
                print(f"{j:08d}: {data1[j]:02x} | {data2[j]:02x}")
            break

    if len(data1) != len(data2):
        print(f"Files have different lengths: {len(data1)} vs {len(data2)}")

if __name__ == "__main__":
    # Replace these with your actual file names in the same directory
    file1 = "clipping.pdf"
    file2 = "no_clipping.pdf"

    if not os.path.exists(file1) or not os.path.exists(file2):
        print("One or both files do not exist.")
    else:
        compare_pdfs(file1, file2)
