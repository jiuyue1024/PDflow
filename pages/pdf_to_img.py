import fitz
doc = fitz.open('C:/Users/Administrator/Desktop/test_extreme.pdf')
for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(dpi=150)
    pix.save(f'C:/Users/Administrator/Desktop/test_extreme_page{i+1}.png')
    print(f'Page {i+1} saved: {pix.width}x{pix.height}')
doc.close()
