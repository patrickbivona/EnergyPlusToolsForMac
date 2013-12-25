

def assert_idf_files(file1, file2):
    with open(file1, 'r') as f1:
        content1 = f1.read()
    with open(file2, 'r') as f2:
        content2 = f2.read()
    assert content1 == content2
