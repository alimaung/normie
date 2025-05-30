import pypdf as pp
 
def get_meta(file):
    with open(file, "rb") as pdf:
        reader = pp.PdfReader(pdf)
        meta = reader.metadata
        keywords = meta.get('/Keywords', 'Not found')
        
        if keywords == "Not found":
            print("NEED CLASSIFICATION")
            return False
        else:
            print("ALREADY CLASSIFIED")
            return True
    
file = r"P:\k-z\Ofs\Dokumentenservice\TeileundStoffe\Antrag\2021\004-2021_01043695.pdf"
#file = r"C:\Users\u8064927\Downloads\classifier api.pdf"

key = get_meta(file)
print(key)