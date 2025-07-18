from pathlib import Path
from tkinter import filedialog
import shutil
import pymupdf
from langchain_core.tools import Tool

def doc_reader() -> str:
    # Separated into two parts: loading and reading before sending to the llm to summarization
    BASE_PATH = Path(__file__).parent.absolute() # references its location within the project's directory tree  
    BIN="loaded_files" # considering a bin for stable referencing, this is only a soft-link within the local machine 

    path = BASE_PATH.joinpath(BIN)

    # prompting the user to search the file they would like summarized
    filepath = filedialog.askopenfilename(initialdir=BASE_PATH,
                                                            title="Choose a file to upload",
                                                            filetypes=[("*", "pdf")])

    filename = filepath.split("/")[-1] # extracting the name of the file found within the absolute path
    path = path.joinpath(filename) # constructing the new path for the link 
    shutil.copyfile(filepath, path)

    # Reading part
    doc = pymupdf.open(path)
    doc_text = ""
    for page in doc:
        doc_text += page.get_text() # get plain text (utf-8 compliant)
    
    return doc_text


def test(doc: pymupdf.Document):
    with open("out.txt", "wb") as file:
        for page in doc:
            text = page.get_text().encode("utf8") # get plain text (utf-8 compliant)
            file.write(text)
            file.write(bytes((12,))) # write page delimiter (form feed 0x0C)
        file.close()


Doc_Reader = Tool(name="doc_reader",
    func=doc_reader,
    description="Useful for pdf text extraction purposes.")
