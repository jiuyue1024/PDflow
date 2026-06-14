import fitz
all_classes = [x for x in dir(fitz) if x[0].isupper()]
print('All fitz classes:')
for c in all_classes:
    print('  ', c)
